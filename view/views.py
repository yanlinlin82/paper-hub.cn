import zoneinfo
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.db.models import Subquery, OuterRef, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from paperhub import settings
from api.paper import get_paper_info, guess_identifier_type
from .models import Paper, Review, Recommendation, PaperTracking, Label, UserProfile

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

def _recommendation_list(request, status):
    user = UserProfile.objects.get(
            auth_user__username=request.user.username
        )

    papers = Paper.objects.annotate(
            any_unread_recommendation=Subquery(Recommendation.objects.filter(
                paper=OuterRef('pk'),
                user=user,
                read_time__isnull=True
            ).values('pk')[:1]),
            latest_create_time=Subquery(Recommendation.objects.filter(
                paper=OuterRef('pk'),
                user=user
            ).values('create_time').order_by('-create_time')[:1])
        ).order_by('-latest_create_time', '-pk')

    if status == 'isunread':
        papers = papers.filter(any_unread_recommendation__isnull=False)
    elif status == 'isread':
        papers = papers.filter(any_unread_recommendation__isnull=True)
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
        paper.recommendations = paper.recommendation_set.filter(user=user, read_time__isnull=True).order_by('-create_time')
        paper.historical_recommendations = paper.recommendation_set.filter(user=user, read_time__isnull=False).order_by('-create_time')
        paper.multi_recommendations = paper.recommendation_set.filter(user=user).count() > 1
    return papers, items

def recommendations_page(request):
    if not request.user.is_authenticated:
        return redirect('/')

    status = request.GET.get('status', 'isunread')
    papers, items = _recommendation_list(request, status)
    return render(request, 'view/recommendations.html', {
        'current_page': 'recommendations',
        'papers': papers,
        'items': items,
        'status': status,
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
                delete_time__isnull=False
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
        paper.reviews = paper.review_set.filter(creator=user, delete_time__isnull=True)

    return papers, items

def all_page(request):
    if not request.user.is_authenticated:
        return redirect('/')

    papers, items = _all_page(request, is_trash=False)
    return render(request, 'view/list.html', {
        'current_page': 'all',
        'papers': papers,
        'items': items,
        })

def recent_page(request):
    if not request.user.is_authenticated:
        return redirect('/')

    papers, items = _all_page(request, is_trash=False, last_week=True)
    return render(request, 'view/list.html', {
        'current_page': 'recent',
        'papers': papers,
        'items': items,
        })

def trash_page(request):
    if not request.user.is_authenticated:
        return redirect('/')

    papers, items = _all_page(request, is_trash=True)
    return render(request, 'view/list.html', {
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
    return render(request, 'view/single.html', {
        'current_page': 'paper',
        'paper': paper,
    })

def labels_page(request):
    if not request.user.is_authenticated:
        return redirect('/')

    user = UserProfile.objects.get(auth_user__username=request.user.username)
    label_list = Label.objects.filter(user=user).order_by('name')

    return render(request, 'view/labels.html', {
        'current_page': 'labels',
        'label_list': label_list,
    })
