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
from api.paper import get_paper_info, get_paginated_reviews, guess_identifier_type
from django.db.models import Max
from django.db.models import Subquery, OuterRef
from django.db.models import Q

def get_review_list(request, include_trash=False):
    if not request.user.is_authenticated:
        return None
    if include_trash:
        return Review.objects.filter(creator__auth_user__username=request.user.username)
    else:
        return Review.objects.filter(creator__auth_user__username=request.user.username, delete_time=None)

def query_papers(query):
    identifier_type, id = guess_identifier_type(query)
    if identifier_type == 'doi':
        papers = Paper.objects.filter(doi=id).order_by('-pk')
    elif identifier_type == 'arxiv':
        papers = Paper.objects.filter(arxiv_id=id).order_by('-pk')
    elif identifier_type == 'pmid':
        papers = Paper.objects.filter(pmid=id).order_by('-pk')
    elif identifier_type == 'pmcid':
        papers = Paper.objects.filter(pmcid=id).order_by('-pk')
    else:
        papers = Paper.objects.filter(
            Q(title__icontains=query) |
            Q(authors__icontains=query) |
            Q(journal__icontains=query) |
            Q(abstract__icontains=query) |
            Q(keywords__icontains=query))

    if identifier_type != "unknown" and papers.count() == 0:
        paper_info, raw_dict = get_paper_info(query)
        if paper_info is not None:
            print(f'doi: {paper_info["id"].get("doi", "")}')
            paper = Paper(
                journal=paper_info.get('journal', ''),
                pub_year=paper_info.get('pub_year', ''),
                pub_date=paper_info.get('pub_date', paper_info.get('pub_year', '')),
                title=paper_info.get('title', ''),
                authors='\n'.join(paper_info.get('authors', [])),
                institutes='\n'.join(paper_info.get('institutes', [])),
                abstract=paper_info.get('abstract', ''),
                keywords='\n'.join(paper_info.get('keywords', [])),
                urls='\n'.join(paper_info.get('urls', [])),
                doi=paper_info['id'].get('doi', ''),
                pmid=paper_info['id'].get('pmid', ''),
                arxiv_id=paper_info['id'].get('arxiv_id', ''),
                pmcid=paper_info['id'].get('pmcid', ''),
                cnki_id=paper_info['id'].get('cnki_id', ''),
                language=paper_info['id'].get('language', 'eng'),
            )
            paper.save()
            print(f'Save paper into database: {paper.pk} {paper.title}')
            papers = Paper.objects.filter(pk=paper.pk).order_by('-pk')

    return papers

def search_page(request):
    u = UserProfile.objects.get(auth_user__username=request.user.username)

    context = {'current_page': 'search'}
    query = request.GET.get('q')
    if query is not None:
        context['query'] = query
        papers = query_papers(query)

        page_number = request.GET.get('page')
        papers, items = get_paginated_reviews(papers, page_number)

        for index, paper in enumerate(papers):
            paper.display_index = index + papers.start_index()
            paper.author_list = [k for k in paper.authors.split('\n') if k]
            paper.keyword_list = [k for k in paper.keywords.split('\n') if k]
            if paper.review_set.filter(creator=u, delete_time__isnull=True).count() > 0:
                paper.has_any_review = True

        context['papers'] = papers
        context['items'] = items

    return render(request, 'view/search.html', context)

def _recommendation_list(request, is_trash=False):
    u = UserProfile.objects.get(
            auth_user__username=request.user.username
        )

    if not is_trash:
        recommendations = Recommendation.objects.filter(
                user=u,
                delete_time__isnull=True
            )
        latest_create_time_subquery = Recommendation.objects.filter(
                paper=OuterRef('pk'),
                user=u,
                delete_time__isnull=True
            ).order_by('-create_time').values('create_time')[:1]
        papers = Paper.objects.filter(
                pk__in=[r.paper_id for r in recommendations]
            ).annotate(
                latest_create_time=Subquery(latest_create_time_subquery)
            ).order_by('-latest_create_time', '-pk')
    else:
        recommendations = Recommendation.objects.filter(
            user=u,
            delete_time__isnull=False
            )
        latest_delete_time_subquery = Recommendation.objects.filter(
                paper=OuterRef('pk'),
                user=u,
                delete_time__isnull=False
            ).order_by('-delete_time').values('delete_time')[:1]
        papers = Paper.objects.filter(
                pk__in=[r.paper_id for r in recommendations]
            ).annotate(
                latest_delete_time=Subquery(latest_delete_time_subquery)
            ).order_by('-latest_delete_time', '-pk')

    page_number = request.GET.get('page')
    papers, items = get_paginated_reviews(papers, page_number)

    for index, paper in enumerate(papers):
        paper.display_index = index + papers.start_index()
        paper.author_list = [k for k in paper.authors.split('\n') if k]
        paper.keyword_list = [k for k in paper.keywords.split('\n') if k]
        if paper.review_set.filter(creator=u, delete_time__isnull=True).count() > 0:
            paper.has_any_review = True
        paper.recommendations = paper.recommendation_set.filter(user=u, delete_time__isnull=True).order_by('-create_time')
        paper.historical_recommendations = paper.recommendation_set.filter(user=u, delete_time__isnull=False).order_by('-create_time')

    return papers, items

def recommendations_page(request):
    papers, items = _recommendation_list(request, is_trash=False)
    return render(request, 'view/recommendations.html', {
        'current_page': 'recommendations',
        'papers': papers,
        'items': items,
        })

def recommendations_trash_page(request):
    papers, items = _recommendation_list(request, is_trash=True)
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

def _all_page(request, is_trash=False, last_week=False):
    u = UserProfile.objects.get(auth_user__username=request.user.username)

    if not is_trash:
        reviews = Review.objects.filter(
                creator=u,
                delete_time__isnull=True
            )
        if last_week:
            last_week = datetime.now().astimezone(zoneinfo.ZoneInfo(settings.TIME_ZONE)) - timedelta(days=7)
            reviews = reviews.filter(create_time__gte=last_week)
        latest_update_time_subquery = Review.objects.filter(
                paper=OuterRef('pk'),
                creator=u,
                delete_time__isnull=False
            ).order_by('-update_time').values('update_time')[:1]
        papers = Paper.objects.filter(
                pk__in=[r.paper_id for r in reviews]
            ).annotate(
                latest_update_time=Subquery(latest_update_time_subquery)
            ).order_by('-latest_update_time', '-pk')
    else:
        reviews = Review.objects.filter(
                creator=u,
                delete_time__isnull=False
            )
        if last_week:
            last_week = datetime.now().astimezone(zoneinfo.ZoneInfo(settings.TIME_ZONE)) - timedelta(days=7)
            reviews = reviews.filter(create_time__gte=last_week)
        latest_delete_time_subquery = Review.objects.filter(
                paper=OuterRef('pk'),
                creator=u,
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
        paper.reviews = paper.review_set.filter(creator=u, delete_time__isnull=True)

    return papers, items

def all_page(request):
    papers, items = _all_page(request, is_trash=False)
    return render(request, 'view/list.html', {
        'current_page': 'all',
        'papers': papers,
        'items': items,
        })

def recent_page(request):
    papers, items = _all_page(request, is_trash=False, last_week=True)
    return render(request, 'view/list.html', {
        'current_page': 'recent',
        'papers': papers,
        'items': items,
        })

def trash_page(request):
    papers, items = _all_page(request, is_trash=True)
    return render(request, 'view/list.html', {
        'current_page': 'trash',
        'papers': papers,
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
