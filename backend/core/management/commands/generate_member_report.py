"""Generate a member reading-interest report for a paper-sharing group.

This is the manual entry point. It reads every member's paper comments (reviews /
check-ins) for a group, computes a per-member analytic profile plus a group-level
aggregate, optionally enriches the narrative with an LLM, and writes a JSON report
to `backend/reports/<group>_member_report.json`.

The website reads this JSON via `GET /api/groups/<group>/member-report/` and lets
visitors click a member ("打卡人") to open their complete evaluation profile.

Usage::

    uv run python manage.py generate_member_report [--group xiangma] [--no-llm] [--min-count 1]
"""

from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from core.models import GroupProfile
from core.member_report import (
    LLMBridge,
    build_group_aggregate,
    build_member_profiles,
    generate_deterministic_profile,
    generate_llm_profile,
    write_html_report,
    write_report,
)


def _provider_name(base_url: str) -> str:
    """Derive a human-friendly provider label from the API base URL."""
    url = (base_url or "").lower()
    if "deepseek" in url:
        return "DeepSeek"
    if "openai" in url or "openai.com" in url:
        return "OpenAI"
    return base_url.split("//")[-1].split("/")[0] or "LLM"


class Command(BaseCommand):
    help = "Generate per-member reading-interest profiles and a group report."

    def add_arguments(self, parser):
        parser.add_argument("--group", default="xiangma", help="Group name (default: xiangma).")
        parser.add_argument(
            "--min-count",
            type=int,
            default=1,
            help="Minimum number of reviews a member must have to be included (default: 1).",
        )
        parser.add_argument(
            "--no-llm",
            action="store_true",
            help="Skip the LLM and use deterministic templates only.",
        )

    def handle(self, *args, **options):
        group_name = options["group"]
        min_count = options["min_count"]
        use_llm = not options["no_llm"]

        if not GroupProfile.objects.filter(name=group_name).exists():
            raise CommandError(f"Group '{group_name}' does not exist.")

        self.stdout.write(f"Reading reviews for group '{group_name}' ...")
        profiles = build_member_profiles(group_name, min_count=min_count)
        if not profiles:
            raise CommandError("No members found for this group.")

        llm = LLMBridge.from_settings() if use_llm else None
        if use_llm and llm is None:
            self.stdout.write(
                self.style.WARNING(
                    "No LLM API key configured; using deterministic templates."
                )
            )

        self.stdout.write(f"Building profiles for {len(profiles)} members ...")
        llm_success = 0
        for profile in profiles:
            if llm:
                used_llm = generate_llm_profile(profile, llm)
                llm_success += 1 if used_llm else 0
            else:
                generate_deterministic_profile(profile)

        # Record which model generated the report (shown on the website). Be
        # honest: only claim LLM-generation if the LLM actually produced the
        # narrative for most members. On API/network failure it falls back to
        # templates, so we must not mislabel the output.
        if llm and llm_success >= max(1, len(profiles) // 2 + (len(profiles) % 2)):
            generator = {
                "mode": "llm",
                "provider": _provider_name(llm.base_url),
                "model": llm.model,
                "generated_at": datetime.now().astimezone().isoformat(),
            }
        else:
            if llm and llm_success == 0:
                msg = (
                    "LLM calls failed; report was generated with deterministic templates.\n"
                    "  last error: " + (llm.last_error or "unknown")
                )
                self.stdout.write(self.style.WARNING(msg))
            generator = {
                "mode": "rule",
                "provider": "rule",
                "model": "",
                "generated_at": datetime.now().astimezone().isoformat(),
            }

        aggregate = build_group_aggregate(group_name, profiles)
        json_path = write_report(group_name, aggregate, profiles, generator=generator)
        html_path = write_html_report(group_name, aggregate, profiles, generator=generator)

        self.stdout.write(
            self.style.SUCCESS(
                f"Report written to {json_path} and {html_path}\n"
                f"  members: {len(profiles)}\n"
                f"  reviews: {aggregate['total_reviews']}\n"
                f"  llm_mode: {generator['mode']} ({llm_success}/{len(profiles)} LLM-generated)\n"
                "  The website will pick this up at "
                f"/api/groups/{group_name}/member-report/"
            )
        )
