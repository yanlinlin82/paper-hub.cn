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
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from core.models import UserProfile, GroupProfile
from core.paper import get_paper_info, prepare_reviews
import json

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
    query = request.GET.get('q', '').strip()
    if query == '':
        return render(request, 'search.html', {'query': query})
    
    # 搜索逻辑...
    return render(request, 'search.html', {'query': query})

def single_page(request, id):
    # 单页逻辑...
    return render(request, 'single.html', {'id': id})

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
    # 推荐页面逻辑...
    return render(request, 'recommendations.html')

def trackings_page(request):
    # 跟踪页面逻辑...
    return render(request, 'trackings.html')

# 重定向到前端应用
def redirect_to_frontend(request):
    """重定向到前端应用"""
    return HttpResponseRedirect('http://localhost:5173')

# 新增：API端点，用于Vue.js前端获取数据
@csrf_exempt
def api_data(request):
    """为Vue.js前端提供数据的API端点"""
    if request.method == 'GET':
        # 获取基础数据
        try:
            group = GroupProfile.objects.get(name='xiangma')
            
            # 获取统计数据
            total_papers = group.reviews.filter(delete_time__isnull=True).count()
            total_users = group.members.count()
            
            # 获取本月分享数量
            from django.utils import timezone
            now = timezone.now()
            this_month_count = group.reviews.filter(
                delete_time__isnull=True,
                create_time__year=now.year,
                create_time__month=now.month
            ).count()
            
            # 获取分享达人数量
            from django.db.models import Count
            top_contributor = group.reviews.filter(delete_time__isnull=True).values('creator').annotate(
                count=Count('id')
            ).order_by('-count').first()
            top_contributor_count = top_contributor['count'] if top_contributor else 0
            
            # 获取最新分享
            recent_reviews = group.reviews.filter(delete_time__isnull=True).order_by('-create_time')[:4]
            
            recent_papers = []
            for review in recent_reviews:
                recent_papers.append({
                    'id': review.id,
                    'title': review.paper.title,
                    'authors': review.creator.nickname,
                    'journal': review.paper.journal,
                    'abstract': review.comment or '暂无摘要',
                    'category': get_category_from_journal(review.paper.journal),
                    'created_at': review.create_time.strftime('%Y-%m-%d %H:%M'),
                    'views': getattr(review, 'views', 0),
                    'likes': getattr(review, 'likes', 0)
                })
            
            data = {
                'success': True,
                'stats': {
                    'totalPapers': total_papers,
                    'totalUsers': total_users,
                    'thisMonthPapers': this_month_count,
                    'topContributor': top_contributor_count
                },
                'recentPapers': recent_papers
            }
            
            return JsonResponse(data)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

def get_category_from_journal(journal):
    """根据期刊名称获取分类"""
    if not journal:
        return '其他'
    
    journal_lower = journal.lower()
    if 'nature' in journal_lower or 'science' in journal_lower:
        return '顶级期刊'
    elif 'machine learning' in journal_lower or 'ai' in journal_lower:
        return 'AI/ML'
    elif 'quantum' in journal_lower:
        return 'Quantum'
    elif 'energy' in journal_lower or 'environmental' in journal_lower:
        return 'Energy'
    elif 'biomedical' in journal_lower or 'medical' in journal_lower:
        return 'Biomedical'
    else:
        return '其他'
