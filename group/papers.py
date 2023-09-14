import zoneinfo
from datetime import datetime, timedelta
from django.urls import reverse
from django.db.models import Count
from django.db.models.aggregates import Min
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import CustomCheckInInterval

tz_beijing = zoneinfo.ZoneInfo("Asia/Shanghai")

def get_paginated_papers(papers, page_number):
    if page_number is None:
        page_number = 1

    p = Paginator(papers, 20)
    try:
        papers = p.get_page(page_number)
    except PageNotAnInteger:
        page_number = 1
        papers = p.page(1)
    except EmptyPage:
        page_number = p.num_pages
        papers = p.page(p.num_pages)

    items = list(papers)
    indices = list(range((papers.number - 1) * p.per_page + 1, papers.number * p.per_page + 1))

    return papers, zip(items, indices)

def filter_papers(papers, page_number, latest_month=False, latest_week=False, user=None, id=None, trash=False, journal_name=None):
    if user is not None:
        papers = papers.filter(creator=user)

    if id is not None:
        papers = papers.filter(pk=id)

    if trash:
        papers = papers.exclude(delete_time=None)
    else:
        papers = papers.filter(delete_time=None)

    if latest_month:
        today = datetime.today().astimezone(tz_beijing)
        year = today.year
        month = today.month
        papers = papers.filter(create_time__year=year, create_time__month=month)
    elif latest_week:
        last_week = datetime.now().astimezone(tz_beijing) - timedelta(days=7)
        papers = papers.filter(create_time__gte=last_week)

    if journal_name is not None:
        papers = papers.filter(journal=journal_name)

    papers = papers.order_by('-create_time', '-pk')
    return get_paginated_papers(papers, page_number)

def get_stat_all(papers, group_name, top_n = None):
    stat_all = papers\
        .values('creator__nickname', 'creator__pk')\
        .annotate(Count('creator'))\
        .order_by('-creator__count')

    if top_n is None:
        top_n = stat_all.count()
        title = '总排名（完整榜单）'
    else:
        title = '总排名（Top10）'

    stat = {
        'name': 'all',
        'title': title,
        'columns': ['排名', '分享者', '分享数'],
        'content': [{
            'id': item['creator__pk'],
            'name': item['creator__nickname'],
            'count': item['creator__count']
        } for item in stat_all[:top_n]],
    }
    if stat_all.count() > top_n:
        stat['full_rank'] = reverse('group:stat_all', kwargs={'group_name':group_name})

    return stat

def get_last_month(year, month):
    if month > 1:
        month = month - 1
    else:
        year = year - 1
        month = 12
    return year, month

def get_next_month(year, month):
    if month < 12:
        month = month + 1
    else:
        year = year + 1
        month = 1
    return year, month

def get_deadline(year, month):
    m = CustomCheckInInterval.objects.filter(year=year, month=month)
    if m.count() > 0:
        return m[0].deadline
    return datetime(*get_next_month(year, month), 1)

def get_check_in_interval(year, month):
    start_time = get_deadline(*get_last_month(year, month))
    end_time = get_deadline(year, month)
    return start_time, end_time

def get_stat_this_month(papers, group_name, top_n = None):
    today = datetime.today().astimezone(tz_beijing)
    year = today.year
    month = today.month

    start_time, end_time = get_check_in_interval(year, month)
    print("This month:")
    print(start_time)
    print(end_time)

    stat_this_month = papers\
        .filter(create_time__gte=start_time, create_time__lt=end_time)\
        .values('creator__nickname', 'creator__pk')\
        .annotate(Count('creator'), min_create_time=Min('create_time'))\
        .order_by('-creator__count', 'min_create_time')

    this_month = str(year) + '/' + str(month)
    if top_n is None:
        top_n = stat_this_month.count()
        title = f'本月排名（{this_month}，完整榜单）'
    else:
        title = f'本月排名（{this_month}，Top10）'

    stat = {
        'name': 'this-month',
        'title': title,
        'columns': ['排名', '分享者', '分享数'],
        'content': [{
            'id': item['creator__pk'],
            'name': item['creator__nickname'],
            'count': item['creator__count']
        } for item in stat_this_month[:top_n]],
    }
    if stat_this_month.count() > top_n:
        stat['full_rank'] = reverse('group:stat_this_month', kwargs={'group_name':group_name})

    return stat

def get_stat_last_month(papers, group_name, top_n = None):
    today = datetime.today().astimezone(tz_beijing)
    year = today.year
    month = today.month
    year, month = get_last_month(year, month)

    start_time, end_time = get_check_in_interval(year, month)
    print("Last month:")
    print(start_time)
    print(end_time)

    stat_last_month = papers\
        .filter(create_time__gte=start_time, create_time__lt=end_time)\
        .values('creator__nickname', 'creator__pk')\
        .annotate(Count('creator'), min_create_time=Min('create_time'))\
        .order_by('-creator__count', 'min_create_time')

    last_month = str(year) + '/' + str(month)
    if top_n is None:
        top_n = stat_last_month.count()
        title = f'上月排名（{last_month}，完整榜单）'
    else:
        title = f'上月排名（{last_month}，Top10）'

    stat = {
        'name': 'last-month',
        'title': title,
        'columns': ['排名', '分享者', '分享数'],
        'content': [{
            'id': item['creator__pk'],
            'name': item['creator__nickname'],
            'count': item['creator__count']
        } for item in stat_last_month[:top_n]],
    }
    if stat_last_month.count() > top_n:
        stat['full_rank'] = reverse('group:stat_last_month', kwargs={'group_name':group_name})

    return stat

def get_stat_journal(papers, group_name, top_n = None):
    stat_journal = papers\
        .exclude(journal='')\
        .values('journal')\
        .annotate(Count('journal'), min_create_time=Min('create_time'))\
        .order_by('-journal__count', 'min_create_time')

    if top_n is None:
        top_n = stat_journal.count()
        title = '杂志排名（完整榜单）'
    else:
        title = '杂志排名（Top10）'

    stat = {
        'name': 'journal',
        'title': title,
        'columns': ['排名', '杂志', '分享数'],
        'content': [{
            'link': reverse('group:journal', kwargs={'group_name':group_name,'journal_name':item['journal']}),
            'name': item['journal'],
            'count': item['journal__count']
        } for item in stat_journal[:top_n]],
    }
    if stat_journal.count() > top_n:
        stat['full_rank'] = reverse('group:stat_journal', kwargs={'group_name':group_name})

    return stat
