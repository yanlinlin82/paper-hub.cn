import re
from functools import wraps
from urllib.parse import unquote
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, F, Min, Q
from core.models import UserProfile, GroupProfile
from core.paper import get_this_week_start_time, get_check_in_interval, get_this_month, get_last_month, prepare_reviews, prepare_single_review

def redirect_query(func):
    @wraps(func)
    def wrapper(request, group_name, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        if query != '':
            url = reverse('group:all', args=[group_name])
            full_url = f"{url}?{request.GET.urlencode()}"
            return redirect(full_url)
        request.query = query
        return func(request, group_name, *args, **kwargs)
    return wrapper

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

def filter_review_by_query(reviews, query):
    if query != '':
        reviews = reviews.filter(
            Q(creator__nickname=query) |
            Q(comment__icontains=query) |
            Q(paper__title__icontains=query) |
            Q(paper__authors__icontains=query) |
            Q(paper__journal__icontains=query) |
            Q(paper__abstract__icontains=query) |
            Q(paper__keywords__icontains=query))
    return reviews

def my_sharing_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    user = UserProfile.objects.get(auth_user=request.user)
    reviews = group.reviews.filter(creator=user, delete_time__isnull=True)
    query = request.GET.get('q', '').strip()
    reviews = filter_review_by_query(reviews, query)
    reviews = reviews.order_by('-create_time', '-pk')
    page_number = request.GET.get('page')
    reviews, items = get_paginated_reviews(reviews, page_number)
    prepare_reviews(reviews)

    get_params = request.GET.copy()
    if 'page' in get_params:
        del get_params['page']

    return render(request, 'group/list.html', {
        'group': group,
        'current_page': 'group_my_sharing',
        'query': query,
        'reviews': reviews,
        'items': items,
        'get_params': get_params,
    })

@redirect_query
def index_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    
    # 获取最新分享的论文
    recent_reviews = group.reviews.filter(delete_time__isnull=True).order_by('-create_time')[:4]
    # 为每个review准备数据
    for review in recent_reviews:
        prepare_single_review(review)
    
    # 获取本月分享数量
    from django.utils import timezone
    now = timezone.now()
    this_month_count = group.reviews.filter(
        delete_time__isnull=True,
        create_time__year=now.year,
        create_time__month=now.month
    ).count()
    
    # 获取分享达人数量（分享最多的用户）
    from django.db.models import Count
    top_contributor = group.reviews.filter(delete_time__isnull=True).values('creator').annotate(
        count=Count('id')
    ).order_by('-count').first()
    top_contributor_count = top_contributor['count'] if top_contributor else 0

    return render(request, 'group/index.html', {
        'group': group,
        'current_page': 'group_index',
        'recent_reviews': recent_reviews,
        'this_month_count': this_month_count,
        'top_contributor_count': top_contributor_count,
    })

def all_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews = group.reviews.filter(delete_time__isnull=True)
    query = request.GET.get('q', '').strip()
    reviews = filter_review_by_query(reviews, query)
    reviews = reviews.order_by('-create_time', '-pk')
    page_number = request.GET.get('page')
    reviews, items = get_paginated_reviews(reviews, page_number)
    prepare_reviews(reviews)

    get_params = request.GET.copy()
    if 'page' in get_params:
        del get_params['page']

    return render(request, 'group/list.html', {
        'group': group,
        'current_page': 'group_all',
        'query': query,
        'reviews': reviews,
        'items': items,
        'get_params': get_params,
    })

def recent_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    start_time = get_this_week_start_time()
    reviews = group.reviews.filter(create_time__gte=start_time, delete_time__isnull=True)
    query = request.GET.get('q', '').strip()
    reviews = filter_review_by_query(reviews, query)
    reviews = reviews.order_by('-create_time', '-pk')
    page_number = request.GET.get('page')
    reviews, items = get_paginated_reviews(reviews, page_number)
    prepare_reviews(reviews)

    get_params = request.GET.copy()
    if 'page' in get_params:
        del get_params['page']

    return render(request, 'group/list.html', {
        'group': group,
        'current_page': 'group_recent',
        'query': query,
        'reviews': reviews,
        'items': items,
        'get_params': get_params,
    })

def this_month_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    start_time, end_time = get_check_in_interval(*get_this_month())
    reviews = group.reviews.filter(create_time__gte=start_time, delete_time__isnull=True)
    query = request.GET.get('q', '').strip()
    reviews = filter_review_by_query(reviews, query)
    reviews = reviews.order_by('-create_time', '-pk')
    page_number = request.GET.get('page')
    reviews, items = get_paginated_reviews(reviews, page_number)
    prepare_reviews(reviews)

    get_params = request.GET.copy()
    if 'page' in get_params:
        del get_params['page']

    return render(request, 'group/list.html', {
        'group': group,
        'current_page': 'group_this_month',
        'query': query,
        'reviews': reviews,
        'items': items,
        'get_params': get_params,
    })

def last_month_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    start_time, end_time = get_check_in_interval(*get_last_month(*get_this_month()))
    reviews = group.reviews.filter(create_time__gte=start_time, create_time__lt=end_time, delete_time__isnull=True)
    query = request.GET.get('q', '').strip()
    reviews = filter_review_by_query(reviews, query)
    reviews = reviews.order_by('-create_time', '-pk')
    page_number = request.GET.get('page')
    reviews, items = get_paginated_reviews(reviews, page_number)
    prepare_reviews(reviews)

    get_params = request.GET.copy()
    if 'page' in get_params:
        del get_params['page']

    return render(request, 'group/list.html', {
        'group': group,
        'current_page': 'group_last_month',
        'query': query,
        'reviews': reviews,
        'items': items,
        'get_params': get_params,
    })

def trash_page(request, group_name):
    if not request.user.is_authenticated:
        return redirect('/')

    group = get_object_or_404(GroupProfile, name=group_name)
    reviews = group.reviews.filter(delete_time__isnull=False)
    query = request.GET.get('q', '').strip()
    reviews = filter_review_by_query(reviews, query)
    reviews = reviews.order_by('-delete_time', '-pk')
    page_number = request.GET.get('page')
    reviews, items = get_paginated_reviews(reviews, page_number)
    prepare_reviews(reviews, is_trash=True)

    get_params = request.GET.copy()
    if 'page' in get_params:
        del get_params['page']

    return render(request, 'group/list.html', {
        'group': group,
        'current_page': 'group_trash',
        'query': query,
        'reviews': reviews,
        'items': items,
        'get_params': get_params,
    })

@redirect_query
def single_page(request, group_name, id):
    group = get_object_or_404(GroupProfile, name=group_name)
    review = get_object_or_404(group.reviews, pk=id)
    prepare_single_review(review)

    return render(request, 'group/single.html', {
        'group': group,
        'current_page': 'group_review',
        'review': review,
    })

def journal_page(request, group_name, journal_name):
    journal_name = unquote(journal_name)
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews = group.reviews.filter(paper__journal=journal_name, delete_time__isnull=True)
    query = request.GET.get('q', '').strip()
    reviews = filter_review_by_query(reviews, query)
    reviews = reviews.order_by('-create_time', '-pk')
    page_number = request.GET.get('page')
    reviews, items = get_paginated_reviews(reviews, page_number)
    prepare_reviews(reviews)

    get_params = request.GET.copy()
    if 'page' in get_params:
        del get_params['page']

    return render(request, 'group/list.html', {
        'group': group,
        'current_page': 'group_journal',
        'query': query,
        'journal_name': journal_name,
        'reviews': reviews,
        'items': items,
        'get_params': get_params,
    })

def user_page(request, id, group_name):
    user = get_object_or_404(UserProfile, pk=id)
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews = group.reviews.filter(creator=user, delete_time__isnull=True)
    query = request.GET.get('q', '').strip()
    reviews = filter_review_by_query(reviews, query)
    reviews = reviews.order_by('-create_time', '-pk')
    page_number = request.GET.get('page')
    reviews, items = get_paginated_reviews(reviews, page_number)
    prepare_reviews(reviews)

    get_params = request.GET.copy()
    if 'page' in get_params:
        del get_params['page']

    return render(request, 'group/list.html', {
        'group': group,
        'current_page': 'group_user',
        'query': query,
        'user_info': user,
        'reviews': reviews,
        'items': items,
        'get_params': get_params,
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
            reviews = reviews.filter(create_time__gte=start_time)
        elif rank_type == 'last_month':
            year, month = get_this_month()
            year, month = get_last_month(year, month)
            start_time, end_time = get_check_in_interval(year, month)
            reviews = reviews.filter(create_time__gte=start_time, create_time__lt=end_time)
        elif rank_type == 'monthly':
            year, month = get_this_month()
            year = int(request.GET.get('year', year))
            month = int(request.GET.get('month', month))
            start_time, end_time = get_check_in_interval(year, month)
            reviews = reviews.filter(create_time__gte=start_time, create_time__lt=end_time)
        elif rank_type == 'yearly':
            year, _ = get_this_month()
            year = int(request.GET.get('year', year))
            start_time, _ = get_check_in_interval(year, 1)
            _, end_time = get_check_in_interval(year, 12)
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

@redirect_query
def rank_page(request, group_name):
    return _rank_page(request, group_name, 'this_month')

@redirect_query
def rank_type_page(request, group_name, rank_type):
    return _rank_page(request, group_name, rank_type)
