#!/usr/bin/env python
import argparse
import json
import os
import sys
import uuid
from collections import OrderedDict
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import django


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


from django.contrib.auth.models import User
from django.db import connection, transaction
from django.db.models import Count
from django.utils.dateparse import parse_date, parse_datetime

from core.models import (
    CustomCheckInInterval,
    GroupProfile,
    Journal,
    Label,
    Paper,
    PaperReference,
    PaperTranslation,
    Review,
    UserAlias,
    UserProfile,
)


FORMAT_VERSION = 1


@dataclass(frozen=True)
class CommunityScope:
    auth_user_ids: list[int]
    group_ids: list[int]
    group_member_links: list[dict]
    group_review_links: list[dict]
    label_ids: list[int]
    paper_ids: list[int]
    review_ids: list[int]
    review_label_links: list[dict]
    user_alias_ids: list[int]
    user_ids: list[int]


def serialize_value(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, uuid.UUID):
        return str(value)
    return value


def deserialize_value(field, value):
    if value is None:
        return None
    internal_type = field.get_internal_type()
    if internal_type == 'DateTimeField':
        return parse_datetime(value)
    if internal_type == 'DateField':
        return parse_date(value)
    if internal_type in {'DecimalField'}:
        return Decimal(value)
    if internal_type == 'UUIDField':
        return uuid.UUID(value)
    return value


def model_row(instance):
    row = OrderedDict()
    for field in instance._meta.concrete_fields:
        row[field.attname] = serialize_value(getattr(instance, field.attname))
    return row


def through_row(instance):
    row = OrderedDict()
    for field in instance._meta.concrete_fields:
        if field.primary_key:
            continue
        row[field.attname] = serialize_value(getattr(instance, field.attname))
    return row


def get_community_scope():
    group_ids = list(GroupProfile.objects.order_by('pk').values_list('pk', flat=True))

    group_member_links = [
        through_row(link)
        for link in GroupProfile.members.through.objects.order_by('groupprofile_id', 'userprofile_id')
    ]
    group_review_links = [
        through_row(link)
        for link in GroupProfile.reviews.through.objects.order_by('groupprofile_id', 'review_id')
    ]

    review_ids = sorted({item['review_id'] for item in group_review_links})
    review_label_links = [
        through_row(link)
        for link in Review.labels.through.objects.filter(review_id__in=review_ids).order_by('review_id', 'label_id')
    ]
    label_ids = sorted({item['label_id'] for item in review_label_links})

    paper_ids = list(
        Review.objects.filter(pk__in=review_ids).order_by('paper_id').values_list('paper_id', flat=True).distinct()
    )

    user_ids = set(item['userprofile_id'] for item in group_member_links)
    user_ids.update(
        Review.objects.filter(pk__in=review_ids).order_by('creator_id').values_list('creator_id', flat=True).distinct()
    )
    user_ids.update(
        Label.objects.filter(pk__in=label_ids).order_by('user_id').values_list('user_id', flat=True).distinct()
    )
    user_ids = sorted(user_ids)

    auth_user_ids = list(
        UserProfile.objects.filter(pk__in=user_ids, auth_user__isnull=False)
        .order_by('auth_user_id')
        .values_list('auth_user_id', flat=True)
    )

    user_alias_ids = list(
        UserAlias.objects.filter(user_id__in=user_ids, alias_id__in=user_ids)
        .order_by('pk')
        .values_list('pk', flat=True)
    )

    return CommunityScope(
        auth_user_ids=auth_user_ids,
        group_ids=group_ids,
        group_member_links=group_member_links,
        group_review_links=group_review_links,
        label_ids=label_ids,
        paper_ids=paper_ids,
        review_ids=review_ids,
        review_label_links=review_label_links,
        user_alias_ids=user_alias_ids,
        user_ids=user_ids,
    )


def build_export_payload():
    scope = get_community_scope()

    payload = OrderedDict()
    payload['format'] = 'paper-hub-community-data'
    payload['format_version'] = FORMAT_VERSION
    payload['data'] = OrderedDict()
    payload['data']['auth_users'] = [
        model_row(item) for item in User.objects.filter(pk__in=scope.auth_user_ids).order_by('pk')
    ]
    payload['data']['custom_check_in_intervals'] = [
        model_row(item) for item in CustomCheckInInterval.objects.order_by('pk')
    ]
    payload['data']['group_members'] = scope.group_member_links
    payload['data']['group_profiles'] = [
        model_row(item) for item in GroupProfile.objects.filter(pk__in=scope.group_ids).order_by('pk')
    ]
    payload['data']['group_reviews'] = scope.group_review_links
    payload['data']['journals'] = [
        model_row(item) for item in Journal.objects.order_by('pk')
    ]
    payload['data']['labels'] = [
        model_row(item) for item in Label.objects.filter(pk__in=scope.label_ids).order_by('pk')
    ]
    payload['data']['paper_references'] = [
        model_row(item) for item in PaperReference.objects.filter(paper_id__in=scope.paper_ids).order_by('pk')
    ]
    payload['data']['paper_translations'] = [
        model_row(item) for item in PaperTranslation.objects.filter(paper_id__in=scope.paper_ids).order_by('pk')
    ]
    payload['data']['papers'] = [
        model_row(item) for item in Paper.objects.filter(pk__in=scope.paper_ids).order_by('pk')
    ]
    payload['data']['review_labels'] = scope.review_label_links
    payload['data']['reviews'] = [
        model_row(item) for item in Review.objects.filter(pk__in=scope.review_ids).order_by('pk')
    ]
    payload['data']['user_aliases'] = [
        model_row(item) for item in UserAlias.objects.filter(pk__in=scope.user_alias_ids).order_by('pk')
    ]
    payload['data']['user_profiles'] = [
        model_row(item) for item in UserProfile.objects.filter(pk__in=scope.user_ids).order_by('pk')
    ]
    return payload


def collect_cleanup_summary(scope):
    personal_review_qs = Review.objects.exclude(pk__in=scope.review_ids)
    personal_paper_qs = Paper.objects.exclude(pk__in=scope.paper_ids)
    personal_label_qs = Label.objects.exclude(pk__in=scope.label_ids)

    orphan_reference_count = PaperReference.objects.exclude(paper_id__in=scope.paper_ids).count()
    orphan_translation_count = PaperTranslation.objects.exclude(paper_id__in=scope.paper_ids).count()

    return OrderedDict([
        ('kept', OrderedDict([
            ('groups', len(scope.group_ids)),
            ('reviews', len(scope.review_ids)),
            ('papers', len(scope.paper_ids)),
            ('labels', len(scope.label_ids)),
            ('users', len(scope.user_ids)),
        ])),
        ('to_delete', OrderedDict([
            ('reviews', personal_review_qs.count()),
            ('papers', personal_paper_qs.count()),
            ('paper_references', orphan_reference_count),
            ('paper_translations', orphan_translation_count),
            ('labels', personal_label_qs.count()),
        ])),
    ])


def vacuum_sqlite_db():
    if connection.vendor != 'sqlite':
        return
    with connection.cursor() as cursor:
        cursor.execute('VACUUM')


def run_cleanup(run):
    scope = get_community_scope()
    summary = collect_cleanup_summary(scope)
    summary['mode'] = 'run' if run else 'dry-run'

    if not run:
        return summary

    with transaction.atomic():
        Review.objects.exclude(pk__in=scope.review_ids).delete()
        Label.objects.exclude(pk__in=scope.label_ids).delete()
        Paper.objects.exclude(pk__in=scope.paper_ids).delete()

    vacuum_sqlite_db()
    return summary


def import_model_rows(model, rows):
    if not rows:
        return

    attname_to_field = {field.attname: field for field in model._meta.concrete_fields}
    pk_attname = model._meta.pk.attname

    instances = []
    for row in rows:
        kwargs = {}
        for key, value in row.items():
            field = attname_to_field[key]
            kwargs[key] = deserialize_value(field, value)
        instances.append(model(**kwargs))

    model.objects.bulk_create(instances, ignore_conflicts=True)

    for row in rows:
        update_data = {}
        for key, value in row.items():
            if key == pk_attname:
                continue
            field = attname_to_field[key]
            update_data[key] = deserialize_value(field, value)
        model.objects.filter(pk=row[pk_attname]).update(**update_data)


def sync_through_rows(through_model, rows, parent_field_name, parent_ids):
    if parent_ids:
        through_model.objects.filter(**{f'{parent_field_name}__in': parent_ids}).delete()
    if not rows:
        return
    through_model.objects.bulk_create([through_model(**row) for row in rows])


def validate_payload(payload):
    if payload.get('format') != 'paper-hub-community-data':
        raise ValueError('Unsupported format')
    if payload.get('format_version') != FORMAT_VERSION:
        raise ValueError(f"Unsupported format_version: {payload.get('format_version')}")
    if 'data' not in payload or not isinstance(payload['data'], dict):
        raise ValueError('Invalid payload: missing data object')


def run_import(input_path, run):
    with open(input_path, 'r', encoding='utf-8') as handle:
        payload = json.load(handle)

    validate_payload(payload)
    data = payload['data']
    summary = OrderedDict([
        ('mode', 'run' if run else 'dry-run'),
        ('input', str(input_path)),
        ('rows', OrderedDict((key, len(value)) for key, value in data.items())),
    ])

    if not run:
        return summary

    with transaction.atomic():
        import_model_rows(User, data.get('auth_users', []))
        import_model_rows(UserProfile, data.get('user_profiles', []))
        import_model_rows(UserAlias, data.get('user_aliases', []))
        import_model_rows(Journal, data.get('journals', []))
        import_model_rows(Paper, data.get('papers', []))
        import_model_rows(PaperTranslation, data.get('paper_translations', []))
        import_model_rows(PaperReference, data.get('paper_references', []))
        import_model_rows(Label, data.get('labels', []))
        import_model_rows(Review, data.get('reviews', []))
        import_model_rows(GroupProfile, data.get('group_profiles', []))
        import_model_rows(CustomCheckInInterval, data.get('custom_check_in_intervals', []))

        sync_through_rows(
            GroupProfile.members.through,
            data.get('group_members', []),
            'groupprofile_id',
            [item['id'] for item in data.get('group_profiles', [])],
        )
        sync_through_rows(
            GroupProfile.reviews.through,
            data.get('group_reviews', []),
            'groupprofile_id',
            [item['id'] for item in data.get('group_profiles', [])],
        )
        sync_through_rows(
            Review.labels.through,
            data.get('review_labels', []),
            'review_id',
            [item['id'] for item in data.get('reviews', [])],
        )

    return summary


def cmd_cleanup(args):
    summary = run_cleanup(run=args.run)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


def cmd_export(args):
    payload = build_export_payload()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write('\n')
    print(output_path)


def cmd_import(args):
    summary = run_import(Path(args.input), run=args.run)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


def build_parser():
    parser = argparse.ArgumentParser(
        description='Manage community-only data for paper-hub.cn.',
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    cleanup_parser = subparsers.add_parser(
        'cleanup',
        help='Delete personal literature data that is not linked to any community group review.',
    )
    cleanup_parser.add_argument(
        '--run',
        action='store_true',
        help='Apply the cleanup. Without this flag the command runs in dry-run mode.',
    )
    cleanup_parser.set_defaults(func=cmd_cleanup)

    export_parser = subparsers.add_parser(
        'export',
        help='Export community data to a deterministic JSON file.',
    )
    export_parser.add_argument('output', help='Output JSON path.')
    export_parser.set_defaults(func=cmd_export)

    import_parser = subparsers.add_parser(
        'import',
        help='Import community data from a deterministic JSON file.',
    )
    import_parser.add_argument('input', help='Input JSON path.')
    import_parser.add_argument(
        '--run',
        action='store_true',
        help='Apply the import. Without this flag the command runs in dry-run mode.',
    )
    import_parser.set_defaults(func=cmd_import)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())