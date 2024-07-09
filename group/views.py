from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from core.models import UserProfile, GroupProfile, Review, Paper
from api.paper import get_this_week_start_time, get_check_in_interval, get_this_month, get_stat_all, get_stat_this_month, get_stat_last_month, get_stat_journal, get_last_month
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, F, Min
from urllib.parse import unquote

def index_page(request):
    return HttpResponseRedirect('xiangma')

def get_paginated_reviews(reviews, page_number):
    if page_number is None:
        page_number = 1

    p = Paginator(reviews, 20)
    try:
        reviews = p.get_page(page_number)
    except PageNotAnInteger:
        page_number = 1
        reviews = p.page(1)
    except EmptyPage:
        page_number = p.num_pages
        reviews = p.page(p.num_pages)

    items = list(reviews)
    indices = list(range((reviews.number - 1) * p.per_page + 1, reviews.number * p.per_page + 1))

    return reviews, zip(items, indices)

def my_sharing_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    user = UserProfile.objects.get(auth_user=request.user)
    reviews = group.reviews.filter(creator=user).order_by('-create_time', '-pk')
    page_number = request.GET.get('page')
    reviews, items = get_paginated_reviews(reviews, page_number)

    for index, review in enumerate(reviews):
        review.display_index = index + reviews.start_index()
        review.paper.author_list = [k for k in review.paper.authors.split('\n') if k]
        review.paper.keyword_list = [k for k in review.paper.keywords.split('\n') if k]
        review.other_reviews = review.paper.review_set.exclude(pk=review.pk).filter(delete_time__isnull=True)

    return render(request, 'group/list.html', {
        'group': group,
        'current_page': 'group_my_sharing',
        'reviews': reviews,
        'items': items,
    })

def all_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews = group.reviews.filter(delete_time__isnull=True).order_by('-create_time', '-pk')
    page_number = request.GET.get('page')
    reviews, items = get_paginated_reviews(reviews, page_number)

    for index, review in enumerate(reviews):
        review.display_index = index + reviews.start_index()
        review.paper.author_list = [k for k in review.paper.authors.split('\n') if k]
        review.paper.keyword_list = [k for k in review.paper.keywords.split('\n') if k]
        review.other_reviews = review.paper.review_set.exclude(pk=review.pk).filter(delete_time__isnull=True)

    return render(request, 'group/list.html', {
        'group': group,
        'current_page': 'group_all',
        'reviews': reviews,
        'items': items,
    })

def recent_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    start_time = get_this_week_start_time()
    reviews = group.reviews.filter(create_time__gte=start_time).order_by('-create_time', '-pk')
    page_number = request.GET.get('page')
    reviews, items = get_paginated_reviews(reviews, page_number)

    for index, review in enumerate(reviews):
        review.display_index = index + reviews.start_index()
        review.paper.author_list = [k for k in review.paper.authors.split('\n') if k]
        review.paper.keyword_list = [k for k in review.paper.keywords.split('\n') if k]
        review.other_reviews = review.paper.review_set.exclude(pk=review.pk).filter(delete_time__isnull=True)

    return render(request, 'group/list.html', {
        'group': group,
        'current_page': 'group_recent',
        'reviews': reviews,
        'items': items,
    })

def this_month_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    start_time, end_time = get_check_in_interval(*get_this_month())
    reviews = group.reviews.filter(create_time__gte=start_time).order_by('-create_time', '-pk')
    page_number = request.GET.get('page')
    reviews, items = get_paginated_reviews(reviews, page_number)

    for index, review in enumerate(reviews):
        review.display_index = index + reviews.start_index()
        review.paper.author_list = [k for k in review.paper.authors.split('\n') if k]
        review.paper.keyword_list = [k for k in review.paper.keywords.split('\n') if k]
        review.other_reviews = review.paper.review_set.exclude(pk=review.pk).filter(delete_time__isnull=True)

    return render(request, 'group/list.html', {
        'group': group,
        'current_page': 'group_this_month',
        'reviews': reviews,
        'items': items,
    })

def last_month_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    start_time, end_time = get_check_in_interval(*get_last_month(*get_this_month()))
    reviews = group.reviews.filter(create_time__gte=start_time, create_time__lt=end_time).order_by('-create_time', '-pk')
    page_number = request.GET.get('page')
    reviews, items = get_paginated_reviews(reviews, page_number)

    for index, review in enumerate(reviews):
        review.display_index = index + reviews.start_index()
        review.paper.author_list = [k for k in review.paper.authors.split('\n') if k]
        review.paper.keyword_list = [k for k in review.paper.keywords.split('\n') if k]
        review.other_reviews = review.paper.review_set.exclude(pk=review.pk).filter(delete_time__isnull=True)

    return render(request, 'group/list.html', {
        'group': group,
        'current_page': 'group_last_month',
        'reviews': reviews,
        'items': items,
    })

def trash_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews = group.reviews.filter(delete_time__isnull=False).order_by('-delete_time', '-pk')
    page_number = request.GET.get('page')
    reviews, items = get_paginated_reviews(reviews, page_number)

    for index, review in enumerate(reviews):
        review.display_index = index + reviews.start_index()
        review.paper.author_list = [k for k in review.paper.authors.split('\n') if k]
        review.paper.keyword_list = [k for k in review.paper.keywords.split('\n') if k]
        review.other_reviews = review.paper.review_set.exclude(pk=review.pk).filter(delete_time__isnull=True)

    return render(request, 'group/list.html', {
        'group': group,
        'current_page': 'group_trash',
        'reviews': reviews,
        'items': items,
    })

def single_page(request, id, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    review = get_object_or_404(group.reviews, pk=id)

    review.paper.author_list = [k for k in review.paper.authors.split('\n') if k]
    review.paper.keyword_list = [k for k in review.paper.keywords.split('\n') if k]
    review.other_reviews = review.paper.review_set.exclude(pk=review.pk).filter(delete_time__isnull=True)

    return render(request, 'group/single.html', {
        'group': group,
        'current_page': 'group_single',
        'review': review,
    })

def journal_page(request, group_name, journal_name):
    journal_name = unquote(journal_name)
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews = group.reviews.filter(paper__journal=journal_name)
    page_number = request.GET.get('page')
    reviews, items = get_paginated_reviews(reviews, page_number)

    for index, review in enumerate(reviews):
        review.display_index = index + reviews.start_index()
        review.paper.author_list = [k for k in review.paper.authors.split('\n') if k]
        review.paper.keyword_list = [k for k in review.paper.keywords.split('\n') if k]
        review.other_reviews = review.paper.review_set.exclude(pk=review.pk).filter(delete_time__isnull=True)

    return render(request, 'group/list.html', {
        'group': group,
        'current_page': 'group_journal',
        'journal_name': journal_name,
        'reviews': reviews,
        'items': items,
    })

def user_page(request, id, group_name):
    user = get_object_or_404(UserProfile, pk=id)
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews = group.reviews.filter(creator=user).order_by('-create_time', '-pk')
    page_number = request.GET.get('page')
    reviews, items = get_paginated_reviews(reviews, page_number)

    for index, review in enumerate(reviews):
        review.display_index = index + reviews.start_index()
        review.paper.author_list = [k for k in review.paper.authors.split('\n') if k]
        review.paper.keyword_list = [k for k in review.paper.keywords.split('\n') if k]
        review.other_reviews = review.paper.review_set.exclude(pk=review.pk).filter(delete_time__isnull=True)

    return render(request, 'group/list.html', {
        'group': group,
        'current_page': 'group_user',
        'user_info': user,
        'reviews': reviews,
        'items': items,
    })

def _rank_page(request, group_name, rank_type):
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews = group.reviews.filter(delete_time__isnull=True)
    year, month, page_obj = None, None, None

    if rank_type == 'journal':
        ranks = reviews.exclude(paper__journal='').values('paper__journal').annotate(
                count=Count('paper__journal'),
                name=F('paper__journal'),
                create_time=Min('create_time')
            ).order_by('-count', 'create_time')
    else:
        if rank_type == 'this_month':
            year, month = get_this_month()
            start_time, end_time = get_check_in_interval(year, month)
            print(f'start_time: {start_time}, end_time: {end_time}')
            reviews = reviews.filter(create_time__gte=start_time)
        elif rank_type == 'last_month':
            year, month = get_this_month()
            year, month = get_last_month(year, month)
            start_time, end_time = get_check_in_interval(year, month)
            print(f'start_time: {start_time}, end_time: {end_time}')
            reviews = reviews.filter(create_time__gte=start_time, create_time__lt=end_time)
        elif rank_type == 'monthly':
            year, month = get_this_month()
            year = int(request.GET.get('year', year))
            month = int(request.GET.get('month', month))
            start_time, end_time = get_check_in_interval(year, month)
            print(f'start_time: {start_time}, end_time: {end_time}')
            reviews = reviews.filter(create_time__gte=start_time, create_time__lt=end_time)
        elif rank_type == 'yearly':
            year, _ = get_this_month()
            year = int(request.GET.get('year', year))
            start_time, _ = get_check_in_interval(year, 1)
            _, end_time = get_check_in_interval(year, 12)
            print(f'start_time: {start_time}, end_time: {end_time}')
            reviews = reviews.filter(create_time__gte=start_time, create_time__lt=end_time)
        elif rank_type == 'all':
            pass
        else:
            return HttpResponse('Invalid rank type')

        ranks = reviews.values('creator').annotate(
                count=Count('creator'),
                id=F('creator__pk'),
                name=F('creator__nickname'),
                create_time=Min('create_time')
            ).order_by('-count', 'create_time')

    for index, rank in enumerate(ranks):
        rank['display_index'] = index + 1

    return render(request, 'group/rank.html', {
        'group': group,
        'current_page': 'group_rank',
        'rank_type': rank_type,
        'ranks': ranks,
        'year': year,
        'month': month,
        'year_list': [i for i in range(2022, get_this_month()[0] + 1)],
        'month_list': [i for i in range(1, 13)],
    })

def rank_page(request, group_name):
    return _rank_page(request, group_name, 'this_month')

def rank_type_page(request, group_name, rank_type):
    return _rank_page(request, group_name, rank_type)
