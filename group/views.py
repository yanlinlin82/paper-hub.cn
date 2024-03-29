from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from view.models import UserProfile, GroupProfile
from api.paper import filter_papers, get_this_week_start_time, get_check_in_interval, get_this_month, get_stat_all, get_stat_this_month, get_stat_last_month, get_stat_journal, get_last_month

class IndexView(generic.ListView):
    template_name = 'group/index.html'
    context_object_name = 'group_list'
    def get_queryset(self):
        return GroupProfile.objects.order_by('-create_time')
    def get_context_data(self, **kwargs):
        context = {
            'current_page': 'index',
            'group_list': GroupProfile.objects.order_by('-create_time'),
            'summary_messages': '',
            }
        return context

def all_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    papers, items = filter_papers(group.papers, request.GET.get('page'))
    template = loader.get_template('group/list.html')
    context = {
        'group': group,
        'current_page': 'all',
        'papers': papers,
        'items': items,
        'summary_messages': '',
    }
    return HttpResponse(template.render(context, request))

def recent_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    start_time = get_this_week_start_time()
    papers, items = filter_papers(group.papers, request.GET.get('page'), start_time=start_time)
    summary_message = 'This page shows papers in last week. '
    template = loader.get_template('group/list.html')
    context = {
        'group': group,
        'current_page': 'recent',
        'papers': papers,
        'items': items,
        'summary_messages': summary_message
    }
    return HttpResponse(template.render(context, request))

def this_month_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    start_time, end_time = get_check_in_interval(*get_this_month())
    papers, items = filter_papers(group.papers, request.GET.get('page'), start_time=start_time)
    summary_message = '本页面显示本月的文献分享。'
    template = loader.get_template('group/list.html')
    context = {
        'group': group,
        'current_page': 'this_month',
        'papers': papers,
        'items': items,
        'summary_messages': summary_message
    }
    return HttpResponse(template.render(context, request))

def last_month_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    start_time, end_time = get_check_in_interval(*get_last_month(*get_this_month()))
    papers, items = filter_papers(group.papers, request.GET.get('page'), start_time=start_time, end_time=end_time)
    summary_message = '本页面显示上月的文献分享。'
    template = loader.get_template('group/list.html')
    context = {
        'group': group,
        'current_page': 'last_month',
        'papers': papers,
        'items': items,
        'summary_messages': summary_message
    }
    return HttpResponse(template.render(context, request))

def stat_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    papers = group.papers.filter(delete_time=None)

    stat_3 = get_stat_all(papers, group_name, top_n=10)
    stat_1 = get_stat_this_month(papers, group_name, top_n=10)
    stat_2 = get_stat_last_month(papers, group_name, top_n=10)
    stat_4 = get_stat_journal(papers, group_name, top_n=10)

    template = loader.get_template('group/stat.html')
    context = {
        'group': group,
        'current_page': 'stat',
        'stat_1': stat_1,
        'stat_2': stat_2,
        'stat_3': stat_3,
        'stat_4': stat_4,
    }
    return HttpResponse(template.render(context, request))

def stat_this_month_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    papers = group.papers.filter(delete_time=None)
    stat = get_stat_this_month(papers, group_name)
    template = loader.get_template('group/stat-single.html')
    context = {
        'group': group,
        'current_page': 'stat',
        'stat': stat,
    }
    return HttpResponse(template.render(context, request))

def stat_last_month_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    papers = group.papers.filter(delete_time=None)
    stat = get_stat_last_month(papers, group_name)
    template = loader.get_template('group/stat-single.html')
    context = {
        'group': group,
        'current_page': 'stat',
        'stat': stat,
    }
    return HttpResponse(template.render(context, request))

def stat_all_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    papers = group.papers.filter(delete_time=None)
    stat = get_stat_all(papers, group_name)
    template = loader.get_template('group/stat-single.html')
    context = {
        'group': group,
        'current_page': 'stat',
        'stat': stat,
    }
    return HttpResponse(template.render(context, request))

def stat_journal_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    papers = group.papers.filter(delete_time=None)
    stat = get_stat_journal(papers, group_name)
    template = loader.get_template('group/stat-single.html')
    context = {
        'group': group,
        'current_page': 'stat',
        'stat': stat,
    }
    return HttpResponse(template.render(context, request))

def trash_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    papers, items = filter_papers(group.papers, request.GET.get('page'), trash=True)
    summary_message = '回收站中的内容将在30后自动删除！'
    return render(request, 'group/list.html', {
        'group': group,
        'current_page': 'trash',
        'papers': papers,
        'items': items,
        'summary_messages': summary_message
    })

def single_page(request, id, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    papers, items = filter_papers(group.papers, request.GET.get('page'), id=id)
    if papers.paginator.count <= 0:
        return render(request, 'group/single.html', {
            'group': group,
            'current_page': 'paper',
            'error_message': 'Invalid paper ID: ' + str(id),
        })
    paper = papers[0]
    template = loader.get_template('group/single.html')
    context = {
        'group': group,
        'current_page': 'paper',
        'paper': paper,
        'items': items,
    }
    return HttpResponse(template.render(context, request))

def journal_page(request, group_name, journal_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    papers, items = filter_papers(group.papers, request.GET.get('page'), journal_name=journal_name)
    template = loader.get_template('group/list.html')
    summary_message = '本页面显示发表在 <b>' + journal_name + '</b> 杂志的文献。'
    context = {
        'group': group,
        'current_page': 'user',
        'papers': papers,
        'items': items,
        'summary_messages': summary_message,
    }
    return HttpResponse(template.render(context, request))

def user_page(request, id, group_name):
    user = get_object_or_404(UserProfile, pk=id)
    group = get_object_or_404(GroupProfile, name=group_name)
    papers, items = filter_papers(group.papers, request.GET.get('page'), user=user)
    template = loader.get_template('group/list.html')
    summary_message = '本页面显示由用户 <b>' + user.nickname + '</b> 推荐的文献。'
    context = {
        'group': group,
        'current_page': 'user',
        'papers': papers,
        'items': items,
        'summary_messages': summary_message,
    }
    return HttpResponse(template.render(context, request))
