"""
REST API views for the React frontend.
These endpoints return JSON data consumed by the frontend SPA.
"""

from urllib.parse import unquote

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, F, Min, Q
from django.http import JsonResponse

from core.models import GroupProfile, Review, UserProfile
from core.paper import (
    get_check_in_interval,
    get_last_month,
    get_this_month,
    get_this_week_start_time,
    prepare_single_paper,
    prepare_single_review,
    process_xml_tags,
)


def serialize_paper(paper, group_name):
    """Serialize a Paper object to a dict for JSON response."""
    return {
        "id": paper.pk,
        "title": process_xml_tags(paper.title),
        "journal": paper.journal,
        "journal_abbreviation": paper.journal_abbreviation,
        "journal_impact_factor": str(paper.journal_impact_factor)
        if paper.journal_impact_factor
        else None,
        "journal_impact_factor_quartile": paper.journal_impact_factor_quartile,
        "pub_date": paper.pub_date,
        "pub_year": paper.pub_year,
        "authors": paper.authors,
        "affiliations": paper.affiliations,
        "abstract": process_xml_tags(paper.abstract),
        "keywords": paper.keywords,
        "urls": paper.urls,
        "doi": paper.doi,
        "pmid": paper.pmid,
        "pmcid": paper.pmcid,
        "arxiv_id": paper.arxiv_id,
        "cnki_id": paper.cnki_id,
    }


def serialize_review(review, group_name, request=None):
    """Serialize a Review object to a dict for JSON response."""
    paper = review.paper
    prepare_single_paper(paper)

    is_superuser = False
    if request and request.user.is_authenticated and request.user.is_superuser:
        is_superuser = True

    data = {
        "id": review.pk,
        "creator_id": review.creator.pk,
        "creator_name": str(review.creator),
        "create_time": review.create_time.isoformat(),
        "update_time": review.update_time.isoformat(),
        "delete_time": review.delete_time.isoformat() if review.delete_time else None,
        "comment": review.comment,
        "paper": serialize_paper(paper, group_name),
        "is_superuser": is_superuser,
        "other_reviews": [
            {
                "id": r.pk,
                "creator_id": r.creator.pk,
                "creator_name": str(r.creator),
                "create_time": r.create_time.isoformat(),
            }
            for r in review.other_reviews.all()
        ]
        if hasattr(review, "other_reviews")
        else [],
    }
    return data


def paginate_reviews(queryset, page_number):
    """Paginate a review queryset and return JSON-serializable data."""
    if page_number is None:
        page_number = 1

    paginator = Paginator(queryset, 20)
    try:
        page = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_number = 1
        page = paginator.page(1)
    except EmptyPage:
        page_number = paginator.num_pages
        page = paginator.page(paginator.num_pages)

    return (
        page,
        paginator,
        list(
            range(
                (page.number - 1) * paginator.per_page + 1,
                (page.number - 1) * paginator.per_page + len(page.object_list) + 1,
            )
        ),
    )


def filter_reviews_by_query(reviews, query):
    if not query:
        return reviews
    return reviews.filter(
        Q(creator__nickname=query)
        | Q(comment__icontains=query)
        | Q(paper__title__icontains=query)
        | Q(paper__authors__icontains=query)
        | Q(paper__journal__icontains=query)
        | Q(paper__abstract__icontains=query)
        | Q(paper__keywords__icontains=query)
    )


# ---- Endpoints ----


def get_group_info(request, group_name):
    """GET /api/groups/{group_name}/ - Get group information."""
    try:
        group = GroupProfile.objects.get(name=group_name)
    except GroupProfile.DoesNotExist:
        return JsonResponse({"error": "Group not found"}, status=404)

    return JsonResponse(
        {
            "name": group.name,
            "display_name": group.display_name,
            "desc": group.desc,
            "create_time": group.create_time.isoformat(),
        }
    )


def get_group_reviews(request, group_name):
    """
    GET /api/groups/{group_name}/reviews/ - Get paginated reviews for a group.
    Query params: page, q (search), type (all|my_sharing|recent|this_month|last_month|trash)
    """
    try:
        group = GroupProfile.objects.get(name=group_name)
    except GroupProfile.DoesNotExist:
        return JsonResponse({"error": "Group not found"}, status=404)

    review_type = request.GET.get("type", "all")
    page_number = request.GET.get("page", "1")
    query = request.GET.get("q", "").strip()

    # Determine base queryset
    if review_type == "trash":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        reviews = group.reviews.filter(delete_time__isnull=False)
        reviews = reviews.order_by("-delete_time", "-pk")
    elif review_type == "my_sharing":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        try:
            user = UserProfile.objects.get(auth_user=request.user)
        except UserProfile.DoesNotExist:
            return JsonResponse({"error": "User profile not found"}, status=404)
        reviews = group.reviews.filter(creator=user, delete_time__isnull=True)
        reviews = reviews.order_by("-create_time", "-pk")
    elif review_type == "recent":
        start_time = get_this_week_start_time()
        reviews = group.reviews.filter(
            create_time__gte=start_time, delete_time__isnull=True
        )
        reviews = reviews.order_by("-create_time", "-pk")
    elif review_type == "this_month":
        year, month = get_this_month()
        start_time, end_time = get_check_in_interval(year, month)
        reviews = group.reviews.filter(
            create_time__gte=start_time, delete_time__isnull=True
        )
        reviews = reviews.order_by("-create_time", "-pk")
    elif review_type == "last_month":
        year, month = get_this_month()
        year, month = get_last_month(year, month)
        start_time, end_time = get_check_in_interval(year, month)
        reviews = group.reviews.filter(
            create_time__gte=start_time,
            create_time__lt=end_time,
            delete_time__isnull=True,
        )
        reviews = reviews.order_by("-create_time", "-pk")
    else:  # 'all'
        reviews = group.reviews.filter(delete_time__isnull=True)
        reviews = reviews.order_by("-create_time", "-pk")

    # Apply search query
    reviews = filter_reviews_by_query(reviews, query)

    # Paginate
    page, paginator, indices = paginate_reviews(reviews, page_number)
    is_trash = review_type == "trash"

    # Serialize
    reviews_data = []
    for review in page.object_list:
        prepare_single_review(review, is_trash)
        rdata = serialize_review(review, group_name, request)
        rdata["display_index"] = (
            len(reviews_data) + (page.number - 1) * paginator.per_page + 1
        )
        reviews_data.append(rdata)

    return JsonResponse(
        {
            "reviews": reviews_data,
            "total_count": paginator.count,
            "start_index": (page.number - 1) * paginator.per_page + 1,
            "end_index": min(page.number * paginator.per_page, paginator.count),
            "indices": indices,
            "paginator": {
                "number": page.number,
                "num_pages": paginator.num_pages,
                "has_previous": page.has_previous(),
                "has_next": page.has_next(),
                "previous_page_number": page.previous_page_number()
                if page.has_previous()
                else None,
                "next_page_number": page.next_page_number()
                if page.has_next()
                else None,
                "start_index": (page.number - 1) * paginator.per_page + 1,
                "end_index": min(page.number * paginator.per_page, paginator.count),
            },
        }
    )


def get_single_review(request, group_name, review_id):
    """GET /api/groups/{group_name}/reviews/{review_id}/ - Get a single review."""
    try:
        group = GroupProfile.objects.get(name=group_name)
    except GroupProfile.DoesNotExist:
        return JsonResponse({"error": "Group not found"}, status=404)

    try:
        review = group.reviews.get(pk=review_id)
    except Review.DoesNotExist:
        return JsonResponse({"error": "Review not found"}, status=404)

    prepare_single_review(review)
    data = serialize_review(review, group_name, request)
    return JsonResponse(data)


def get_user_reviews(request, group_name, user_id):
    """GET /api/groups/{group_name}/users/{user_id}/ - Get reviews by a specific user."""
    try:
        group = GroupProfile.objects.get(name=group_name)
    except GroupProfile.DoesNotExist:
        return JsonResponse({"error": "Group not found"}, status=404)

    try:
        user = UserProfile.objects.get(pk=user_id)
    except UserProfile.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    page_number = request.GET.get("page", "1")
    query = request.GET.get("q", "").strip()

    reviews = group.reviews.filter(creator=user, delete_time__isnull=True)
    reviews = filter_reviews_by_query(reviews, query)
    reviews = reviews.order_by("-create_time", "-pk")

    page, paginator, indices = paginate_reviews(reviews, page_number)

    reviews_data = []
    for review in page.object_list:
        prepare_single_review(review)
        rdata = serialize_review(review, group_name, request)
        reviews_data.append(rdata)

    return JsonResponse(
        {
            "reviews": reviews_data,
            "total_count": paginator.count,
            "start_index": (page.number - 1) * paginator.per_page + 1,
            "end_index": min(page.number * paginator.per_page, paginator.count),
            "indices": indices,
            "user_info": {
                "id": user.pk,
                "nickname": str(user),
            },
            "paginator": {
                "number": page.number,
                "num_pages": paginator.num_pages,
                "has_previous": page.has_previous(),
                "has_next": page.has_next(),
                "previous_page_number": page.previous_page_number()
                if page.has_previous()
                else None,
                "next_page_number": page.next_page_number()
                if page.has_next()
                else None,
            },
        }
    )


def get_journal_reviews(request, group_name, journal_name):
    """GET /api/groups/{group_name}/journals/{journal_name}/ - Get reviews for a journal."""
    journal_name = unquote(journal_name)
    try:
        group = GroupProfile.objects.get(name=group_name)
    except GroupProfile.DoesNotExist:
        return JsonResponse({"error": "Group not found"}, status=404)

    page_number = request.GET.get("page", "1")
    query = request.GET.get("q", "").strip()

    reviews = group.reviews.filter(
        paper__journal=journal_name, delete_time__isnull=True
    )
    reviews = filter_reviews_by_query(reviews, query)
    reviews = reviews.order_by("-create_time", "-pk")

    page, paginator, indices = paginate_reviews(reviews, page_number)

    reviews_data = []
    for review in page.object_list:
        prepare_single_review(review)
        rdata = serialize_review(review, group_name, request)
        reviews_data.append(rdata)

    return JsonResponse(
        {
            "reviews": reviews_data,
            "total_count": paginator.count,
            "start_index": (page.number - 1) * paginator.per_page + 1,
            "end_index": min(page.number * paginator.per_page, paginator.count),
            "indices": indices,
            "journal_name": journal_name,
            "paginator": {
                "number": page.number,
                "num_pages": paginator.num_pages,
                "has_previous": page.has_previous(),
                "has_next": page.has_next(),
                "previous_page_number": page.previous_page_number()
                if page.has_previous()
                else None,
                "next_page_number": page.next_page_number()
                if page.has_next()
                else None,
            },
        }
    )


def get_group_rankings(request, group_name, rank_type):
    """
    GET /api/groups/{group_name}/rank/{rank_type}/
    Rank types: this_month, last_month, monthly, yearly, all, journal
    Query params for monthly/yearly: year, month
    """
    try:
        group = GroupProfile.objects.get(name=group_name)
    except GroupProfile.DoesNotExist:
        return JsonResponse({"error": "Group not found"}, status=404)

    reviews = group.reviews.filter(delete_time__isnull=True)
    year, month, ranks = None, None, None

    current_year, current_month = get_this_month()

    if rank_type == "journal":
        # Journal rankings
        journal_ranks = (
            reviews.exclude(paper__journal="")
            .values("paper__journal")
            .annotate(
                count=Count("paper__journal"),
                name=F("paper__journal"),
                create_time=Min("create_time"),
            )
            .order_by("-count", "create_time")
        )
        ranks = list(journal_ranks)
    else:
        # User rankings
        if rank_type == "this_month":
            year, month = current_year, current_month
            start_time, end_time = get_check_in_interval(year, month)
            reviews = reviews.filter(create_time__gte=start_time)
        elif rank_type == "last_month":
            year, month = get_last_month(current_year, current_month)
            start_time, end_time = get_check_in_interval(year, month)
            reviews = reviews.filter(
                create_time__gte=start_time, create_time__lt=end_time
            )
        elif rank_type == "monthly":
            year = int(request.GET.get("year", current_year))
            month = int(request.GET.get("month", current_month))
            start_time, end_time = get_check_in_interval(year, month)
            reviews = reviews.filter(
                create_time__gte=start_time, create_time__lt=end_time
            )
        elif rank_type == "yearly":
            year = int(request.GET.get("year", current_year))
            start_time, _ = get_check_in_interval(year, 1)
            _, end_time = get_check_in_interval(year, 12)
            reviews = reviews.filter(
                create_time__gte=start_time, create_time__lt=end_time
            )
        elif rank_type == "all":
            pass
        else:
            return JsonResponse({"error": "Invalid rank type"}, status=400)

        user_ranks = (
            reviews.values("creator")
            .annotate(
                count=Count("creator"),
                id=F("creator__pk"),
                name=F("creator__nickname"),
                create_time=Min("create_time"),
            )
            .order_by("-count", "create_time")
        )
        ranks = list(user_ranks)

    # Add display index
    for index, rank in enumerate(ranks):
        rank["display_index"] = index + 1

    # Format create_time as ISO string for JSON
    for rank in ranks:
        if "create_time" in rank and rank["create_time"]:
            if hasattr(rank["create_time"], "isoformat"):
                rank["create_time"] = rank["create_time"].isoformat()

    return JsonResponse(
        {
            "ranks": ranks,
            "rank_type": rank_type,
            "year": year,
            "month": month,
            "year_list": list(range(2022, current_year + 1)),
            "month_list": list(range(1, 13)),
        }
    )


def get_current_user(request):
    """GET /api/me/ - Get current authenticated user info."""
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(auth_user=request.user)
            return JsonResponse(
                {
                    "is_authenticated": True,
                    "username": request.user.username,
                    "nickname": str(profile),
                    "is_superuser": request.user.is_superuser,
                    "user_id": profile.pk,
                }
            )
        except UserProfile.DoesNotExist:
            return JsonResponse(
                {
                    "is_authenticated": True,
                    "username": request.user.username,
                    "nickname": request.user.username,
                    "is_superuser": request.user.is_superuser,
                    "user_id": None,
                }
            )
    return JsonResponse({"is_authenticated": False})
