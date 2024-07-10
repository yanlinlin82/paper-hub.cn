import zoneinfo
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.db.models import Subquery, OuterRef, Q, Max, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from paperhub import settings
from core.paper import get_paper_info, guess_identifier_type
from core.models import Paper, Review, Recommendation, PaperTracking, Label, UserProfile

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

def _all_page(request, is_trash=False, last_week=False):
    user = UserProfile.objects.get(auth_user__username=request.user.username)

    if not is_trash:
        reviews = Review.objects.filter(
                creator=user,
                delete_time__isnull=True
            )
        if last_week:
            last_week = datetime.now().astimezone(zoneinfo.ZoneInfo(settings.TIME_ZONE)) - timedelta(days=7)
            reviews = reviews.filter(create_time__gte=last_week)
        latest_update_time_subquery = Review.objects.filter(
                paper=OuterRef('pk'),
                creator=user,
                delete_time__isnull=True
            ).order_by('-update_time').values('update_time')[:1]
        papers = Paper.objects.filter(
                pk__in=[r.paper_id for r in reviews]
            ).annotate(
                latest_update_time=Subquery(latest_update_time_subquery)
            ).order_by('-latest_update_time', '-pk')
    else:
        reviews = Review.objects.filter(
                creator=user,
                delete_time__isnull=False
            )
        if last_week:
            last_week = datetime.now().astimezone(zoneinfo.ZoneInfo(settings.TIME_ZONE)) - timedelta(days=7)
            reviews = reviews.filter(create_time__gte=last_week)
        latest_delete_time_subquery = Review.objects.filter(
                paper=OuterRef('pk'),
                creator=user,
                delete_time__isnull=False
            ).order_by('-delete_time').values('delete_time')[:1]
        papers = Paper.objects.filter(
                pk__in=[r.paper_id for r in reviews]
            ).annotate(
                latest_delete_time=Subquery(latest_delete_time_subquery)
            ).order_by('-latest_delete_time', '-pk')

    page_number = request.GET.get('page')
    papers, items = get_paginated_reviews(papers, page_number)

    for index, paper in enumerate(papers):
        paper.display_index = index + papers.start_index()
        paper.author_list = [k for k in paper.authors.split('\n') if k]
        paper.keyword_list = [k for k in paper.keywords.split('\n') if k]
        if not is_trash:
            paper.reviews = paper.review_set.filter(creator=user, delete_time__isnull=True)
        else:
            paper.reviews = paper.review_set.filter(creator=user, delete_time__isnull=False)

    return papers, items

def all_page(request):
    if not request.user.is_authenticated:
        return redirect('/')

    papers, items = _all_page(request, is_trash=False)
    return render(request, 'library/list.html', {
        'current_page': 'all',
        'papers': papers,
        'items': items,
        })

def recent_page(request):
    if not request.user.is_authenticated:
        return redirect('/')

    papers, items = _all_page(request, is_trash=False, last_week=True)
    return render(request, 'library/list.html', {
        'current_page': 'recent',
        'papers': papers,
        'items': items,
        })

def trash_page(request):
    if not request.user.is_authenticated:
        return redirect('/')

    papers, items = _all_page(request, is_trash=True)
    return render(request, 'library/list.html', {
        'current_page': 'trash',
        'papers': papers,
        'items': items,
    })

def single_page(request, id):
    paper = get_object_or_404(Paper, pk=id)
    paper.author_list = [k for k in paper.authors.split('\n') if k]
    paper.keyword_list = [k for k in paper.keywords.split('\n') if k]
    if request.user.is_authenticated:
        user = UserProfile.objects.get(auth_user__username=request.user.username)
        paper.reviews = paper.review_set.filter(creator=user, delete_time__isnull=True)
    return render(request, 'library/single.html', {
        'current_page': 'paper',
        'paper': paper,
    })

def labels_page(request):
    if not request.user.is_authenticated:
        return redirect('/')

    user = UserProfile.objects.get(auth_user__username=request.user.username)
    label_list = Label.objects.filter(user=user).order_by('name')

    return render(request, 'library/labels.html', {
        'current_page': 'labels',
        'label_list': label_list,
    })
