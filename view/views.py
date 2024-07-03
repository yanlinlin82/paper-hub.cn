import zoneinfo
from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from .models import Paper, Review, Recommendation, PaperTracking, Label, UserProfile
from paperhub import settings
from django.shortcuts import render, redirect
from django.conf import settings
from api.paper import get_paper_info, get_paginated_reviews
from django.db.models import Max
from django.db.models import Subquery, OuterRef

def get_review_list(request, include_trash=False):
    if not request.user.is_authenticated:
        return None
    if include_trash:
        return Review.objects.filter(creator__auth_user__username=request.user.username)
    else:
        return Review.objects.filter(creator__auth_user__username=request.user.username, delete_time=None)

def search_page(request):
    context = {
        'current_page': 'search',
    }

    query = request.GET.get('q')
    if query is not None:
        context['query'] = query
        paper_info, raw_dict = get_paper_info(query)
        if paper_info is None:
            context['error_message'] = f"Failed to query paper info with '{query}'!"
        else:
            context['results'] = [{
                "id": paper_info.get('id'),
                "title": paper_info.get('title', ''),
                "journal": paper_info.get('journal', ''),
                "pub_year": paper_info.get('pub_year', ''),
                "authors": paper_info.get('authors', []),
                "abstract": paper_info.get('abstract', ''),
                "urls": paper_info.get('urls', []),
            }]
    return render(request, 'view/search.html', context)

def recommendations_page(request):
    u = UserProfile.objects.get(auth_user__username=request.user.username)

    recommendations = Recommendation.objects.filter(
        user=u,
        delete_time__isnull=True
        ).order_by('-create_time', '-pk')
    
    papers = Paper.objects.filter(pk__in=[r.paper_id for r in recommendations])

    page_number = request.GET.get('page')
    papers, items = get_paginated_reviews(papers, page_number)

    for index, paper in enumerate(papers):
        paper.display_index = index + papers.start_index()
        paper.author_list = [k for k in paper.authors.split('\n') if k]
        paper.keyword_list = [k for k in paper.keywords.split('\n') if k]

    return render(request, 'view/recommendations.html', {
        'current_page': 'recommendations',
        'papers': papers,
        'items': items,
        })

def recommendations_page_trash(request):
    u = UserProfile.objects.get(auth_user__username=request.user.username)

    recommendations = Recommendation.objects.filter(
        user=u,
        delete_time__isnull=False
        ).order_by('-delete_time', '-pk')
    
    latest_delete_time_subquery = Recommendation.objects.filter(
        paper=OuterRef('pk'),
        user=u,
        delete_time__isnull=False
    ).order_by('-delete_time').values('delete_time')[:1]

    papers = Paper.objects.filter(
        pk__in=[r.paper_id for r in recommendations]
    ).annotate(
        latest_delete_time=Subquery(latest_delete_time_subquery)
    ).order_by('-latest_delete_time')

    page_number = request.GET.get('page')
    papers, items = get_paginated_reviews(papers, page_number)

    for index, paper in enumerate(papers):
        paper.display_index = index + papers.start_index()
        paper.author_list = [k for k in paper.authors.split('\n') if k]
        paper.keyword_list = [k for k in paper.keywords.split('\n') if k]

    return render(request, 'view/recommendations.html', {
        'current_page': 'recommendations-trash',
        'papers': papers,
        'items': items,
        })

def trackings_page(request):
    item_list = PaperTracking.objects.filter(user__auth_user__username=request.user.username)
    template = loader.get_template('view/trackings.html')
    context = {
        'current_page': 'trackings',
        'item_list': item_list,
    }
    return HttpResponse(template.render(context, request))

def all_page(request):
    review_list = get_review_list(request)
    if review_list:
        review_list = review_list.order_by('-create_time', '-pk')
        for item in review_list:
            item.author_list = [k for k in item.paper.authors.split('\n') if k]

        page_number = request.GET.get('page')
        reviews, items = get_paginated_reviews(review_list, page_number)
    else:
        reviews = None
        items = None

    template = loader.get_template('view/list.html')
    context = {
        'current_page': 'all',
        'reviews': reviews,
        'items': items,
    }
    return HttpResponse(template.render(context, request))

def recent_page(request):
    last_week = datetime.now().astimezone(zoneinfo.ZoneInfo(settings.TIME_ZONE)) - timedelta(days=7)
    review_list = get_review_list(request)
    if review_list is not None:
        review_list = review_list.filter(create_time__gte=last_week).order_by('-create_time', '-pk')
    for item in review_list:
        item.author_list = [k for k in item.paper.authors.split('\n') if k]

    page_number = request.GET.get('page')
    reviews, items = get_paginated_reviews(review_list, page_number)

    template = loader.get_template('view/list.html')
    context = {
        'current_page': 'recent',
        'reviews': reviews,
        'items': items,
    }
    return HttpResponse(template.render(context, request))

def trash_page(request):
    review_list = get_review_list(request, include_trash=True)
    if review_list is not None:
        review_list = review_list.exclude(delete_time=None).order_by('-create_time', '-pk')
    for item in review_list:
        item.author_list = [k for k in item.paper.authors.split('\n') if k]

    page_number = request.GET.get('page')
    reviews, items = get_paginated_reviews(review_list, page_number)

    return render(request, 'view/list.html', {
        'current_page': 'trash',
        'reviews': reviews,
        'items': items,
    })

def single_page(request, id):
    review_list = get_review_list(request)
    if review_list is not None:
        review_list = review_list.filter(pk=id)
    if review_list.count() <= 0:
        return render(request, 'view/single.html', {
            'current_page': 'paper',
            'error_message': 'Invalid paper ID: ' + str(id),
        })
    review = review_list[0]
    template = loader.get_template('view/single.html')
    context = {
        'current_page': 'paper',
        'item': review,
    }
    return HttpResponse(template.render(context, request))

def labels_page(request):
    u = UserProfile.objects.get(auth_user__username=request.user.username)
    label_list = Label.objects.filter(user=u).order_by('name')

    return render(request, 'view/labels.html', {
        'current_page': 'labels',
        'label_list': label_list,
    })
