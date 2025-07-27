import zoneinfo
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.db.models import Subquery, OuterRef, Q, Max, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from mysite import settings
from core.paper import get_paper_info, guess_identifier_type, prepare_single_paper
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
            paper = Paper(
                journal=paper_info.get('journal', '') or '',
                pub_year=paper_info.get('pub_year', '') or '',
                pub_date=paper_info.get('pub_date', paper_info.get('pub_year', '') or ''),
                title=paper_info.get('title', '') or '',
                authors='\n'.join(paper_info.get('authors', [])),
                affiliations='\n'.join(paper_info.get('affiliations', [])),
                abstract=paper_info.get('abstract', '') or '',
                keywords='\n'.join(paper_info.get('keywords', [])),
                urls='\n'.join(paper_info.get('urls', [])),
                doi=paper_info['id'].get('doi', '') or '',
                pmid=paper_info['id'].get('pmid', '') or '',
                arxiv_id=paper_info['id'].get('arxiv_id', '') or '',
                pmcid=paper_info['id'].get('pmcid', '') or '',
                cnki_id=paper_info['id'].get('cnki_id', '') or '',
                language=paper_info['id'].get('language', 'eng'),
            )
            paper.save()
            papers = Paper.objects.filter(pk=paper.pk).order_by('-pk')

    return papers

def search_page(request):
    context = {'current_page': 'search'}
    query = request.GET.get('q')
    if query is not None:
        context['query'] = query
        papers = query_papers(query)

        page_number = request.GET.get('page')
        papers, items = get_paginated_reviews(papers, page_number)

        user = None
        if request.user.is_authenticated:
            user = UserProfile.objects.get(auth_user__username=request.user.username)

        for index, paper in enumerate(papers):
            paper.display_index = index + papers.start_index()
            paper.author_list = [k for k in paper.authors.split('\n') if k]
            paper.keyword_list = [k for k in paper.keywords.split('\n') if k]
            paper.has_any_review = False
            if user is not None:
                if paper.review_set.filter(creator=user, delete_time__isnull=True).count() > 0:
                    paper.has_any_review = True

        context['papers'] = papers
        context['items'] = items

    get_params = request.GET.copy()
    if 'page' in get_params:
        del get_params['page']
    context['get_params'] = get_params

    return render(request, 'view/search.html', context)

def single_page(request, id):
    paper = get_object_or_404(Paper, pk=id)
    paper = prepare_single_paper(paper)    
    paper.ref_list = paper.references.filter(type='ReferenceList').order_by('index')
    paper.cc_list = paper.references.filter(type='CommentsCorrectionsList').order_by('index')
    if request.user.is_authenticated:
        user = UserProfile.objects.get(auth_user__username=request.user.username)
        paper.reviews = paper.review_set.filter(creator=user, delete_time__isnull=True)
    return render(request, 'view/single.html', {
        'current_page': 'paper',
        'paper': paper,
    })

def _recommendation_list(request, status, recommended):
    user = UserProfile.objects.get(
            auth_user__username=request.user.username
        )

    if status == 'isunread':
        recommendations = Recommendation.objects.filter(
                user=user,
                read_time__isnull=True
            )
        papers = Paper.objects.filter(
            pk__in=recommendations.values('paper')
        ).annotate(
            latest_recommended_time=Max('recommendation__create_time'),
            recommended_count=Count('recommendation__pk')
        ).order_by('-latest_recommended_time')
    else:
        recommendations = Recommendation.objects.filter(
                user=user,
                read_time__isnull=False
            )
        recommendations2 = Recommendation.objects.filter(
                user=user,
                read_time__isnull=True
            )
        papers = Paper.objects.filter(
            pk__in=recommendations.values('paper')
        ).exclude(
            pk__in=recommendations2.values('paper')
        ).annotate(
            latest_read_time=Max('recommendation__read_time'),
            recommended_count=Count('recommendation__pk')
        ).order_by('-latest_read_time')

    if recommended == 'first':
        papers = papers.filter(recommended_count=1)
    elif recommended == 'multi':
        papers = papers.filter(recommended_count__gt=1)
    else:
        pass

    page_number = request.GET.get('page')
    papers, items = get_paginated_reviews(papers, page_number)

    for index, paper in enumerate(papers):
        paper.display_index = index + papers.start_index()
        paper.author_list = [k for k in paper.authors.split('\n') if k]
        paper.keyword_list = [k for k in paper.keywords.split('\n') if k]
        if paper.review_set.filter(creator=user, delete_time__isnull=True).count() > 0:
            paper.has_any_review = True
        if status == 'isunread':
            paper.recommendations = paper.recommendation_set.filter(user=user, read_time__isnull=True).order_by('-create_time')
            paper.historical_recommendations = paper.recommendation_set.filter(user=user, read_time__isnull=False).order_by('-create_time')
        else:
            paper.recommendations = paper.recommendation_set.filter(user=user).order_by('-create_time')

    return papers, items

def recommendations_page(request):
    if not request.user.is_authenticated:
        return redirect('/')

    status = request.GET.get('status', 'isunread')
    recommended = request.GET.get('recommended', 'first')
    papers, items = _recommendation_list(request, status, recommended)

    get_params = request.GET.copy()
    if 'page' in get_params:
        del get_params['page']

    return render(request, 'view/recommendations.html', {
        'current_page': 'recommendations',
        'papers': papers,
        'items': items,
        'status': status,
        'recommended': recommended,
        'get_params': get_params,
        })

def trackings_page(request):
    if not request.user.is_authenticated:
        return redirect('/')

    item_list = PaperTracking.objects.filter(user__auth_user__username=request.user.username)
    template = loader.get_template('view/trackings.html')
    context = {
        'current_page': 'trackings',
        'item_list': item_list,
    }
    return HttpResponse(template.render(context, request))
