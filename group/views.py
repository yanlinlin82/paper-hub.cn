from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import loader
from view.models import UserProfile, GroupProfile, Review, Paper
from api.paper import get_this_week_start_time, get_check_in_interval, get_this_month, get_stat_all, get_stat_this_month, get_stat_last_month, get_stat_journal, get_last_month
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
    return render(request, 'group/list.html', {
        'group': group,
        'current_page': 'group_last_month',
        'reviews': reviews,
        'items': items,
    })

def stat_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews = group.reviews.filter(delete_time=None)

    stat_3 = get_stat_all(reviews, group_name, top_n=10)
    stat_1 = get_stat_this_month(reviews, group_name, top_n=10)
    stat_2 = get_stat_last_month(reviews, group_name, top_n=10)
    stat_4 = get_stat_journal(reviews, group_name, top_n=10)
    return render(request, 'group/stat.html', {
        'group': group,
        'current_page': 'group_stat',
        'stat_1': stat_1,
        'stat_2': stat_2,
        'stat_3': stat_3,
        'stat_4': stat_4,
    })

def stat_this_month_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews = group.reviews.filter(delete_time=None)
    stat = get_stat_this_month(reviews, group_name)
    return render(request, 'group/stat-single.html', {
        'group': group,
        'current_page': 'group_stat',
        'stat': stat,
    })

def stat_last_month_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews = group.reviews.filter(delete_time=None)
    stat = get_stat_last_month(reviews, group_name)
    return render(request, 'group/stat-single.html', {
        'group': group,
        'current_page': 'group_stat',
        'stat': stat,
    })

def stat_all_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews = group.reviews.filter(delete_time=None)
    stat = get_stat_all(reviews, group_name)
    return render(request, 'group/stat-single.html', {
        'group': group,
        'current_page': 'group_stat',
        'stat': stat,
    })

def stat_journal_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews = group.reviews.filter(delete_time=None)
    stat = get_stat_journal(reviews, group_name)
    return render(request, 'group/stat-single.html', {
        'group': group,
        'current_page': 'group_stat',
        'stat': stat,
    })

def trash_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews = group.reviews.filter(delete_time__isnull=False).order_by('-delete_time', '-pk')
    page_number = request.GET.get('page')
    reviews, items = get_paginated_reviews(reviews, page_number)
    return render(request, 'group/list.html', {
        'group': group,
        'current_page': 'group_trash',
        'reviews': reviews,
        'items': items,
    })

def single_page(request, id, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    review = get_object_or_404(group.reviews, pk=id)
    return render(request, 'group/single.html', {
        'group': group,
        'current_page': 'group_single',
        'review': review,
    })

def journal_page(request, group_name, journal_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews = group.reviews.filter(journal=journal_name)
    page_number = request.GET.get('page')
    reviews, items = get_paginated_reviews(reviews, page_number)
    return render(request, 'group/list.html', {
        'group': group,
        'current_page': 'group_journal',
        'reviews': reviews,
        'items': items,
    })

def user_page(request, id, group_name):
    user = get_object_or_404(UserProfile, pk=id)
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews = group.reviews.filter(creator=user).order_by('-create_time', '-pk')
    page_number = request.GET.get('page')
    reviews, items = get_paginated_reviews(reviews, page_number)
    return render(request, 'group/list.html', {
        'group': group,
        'current_page': 'group_user',
        'reviews': reviews,
        'items': items,
    })
