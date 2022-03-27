from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from django.db.models import Q, Count
from django.core import serializers

from .models import Label, Paper, User
from .forms import PaperForm

# Create your views here.
def xiangma_AllPapersView(request, current_page):
    paper_list = Paper.objects.order_by('-create_time', '-pk')
    template = loader.get_template('xiangma-list.html')
    context = {
        'current_page': current_page,
        'paper_list': paper_list,
        'summary_messages': '',
    }
    return HttpResponse(template.render(context, request))

def xiangma_RecentPapersView(request, current_page):
    last_week = datetime.today() - timedelta(days=7)
    paper_list = Paper.objects.filter(create_time__gte=last_week).order_by('-create_time', '-pk')
    template = loader.get_template('xiangma-list.html')
    context = {
        'current_page': current_page,
        'paper_list': paper_list,
        'summary_messages': '本页面显示最近一周的文献分享。'
    }
    return HttpResponse(template.render(context, request))

def xiangma_PaperListView(request, id, current_page):
    paper_list = Paper.objects.order_by('-create_time', '-pk')
    template = loader.get_template('xiangma-list.html')
    context = {
        'current_page': current_page,
        'paper_list': paper_list,
        'summary_messages': 'This page shows list <b>#' + str(id) + '</b>. ',
    }
    return HttpResponse(template.render(context, request))

def xiangma_PaperLabelView(request, name, current_page):
    paper_list = None
    xiangma = Label.objects.filter(name=name)
    if xiangma.count() > 0:
        paper_list = xiangma[0].paper_set.all().order_by('-create_time', '-pk')
    template = loader.get_template('xiangma-list.html')
    context = {
        'current_page': current_page,
        'paper_list': paper_list,
        'summary_messages': 'This page shows list of label "<b>' + name + '</b>". ',
    }
    return HttpResponse(template.render(context, request))

def xiangma_SinglePaperView(request, id, current_page):
    paper = Paper.objects.filter(pk=id)
    template = loader.get_template('xiangma-single.html')
    context = {
        'current_page': current_page,
        'paper': paper[0],
    }
    return HttpResponse(template.render(context, request))

def xiangma_StatView(request, current_page):
    stat_all = Paper.objects.values('creator__nickname', 'creator__pk').annotate(Count('creator')).order_by('-creator__count')

    today = datetime.today()
    year = today.year
    month = today.month
    stat_this_month = Paper.objects.filter(create_time__year=year, create_time__month=month).values('creator__nickname', 'creator__pk').annotate(Count('creator')).order_by('-creator__count')

    if month > 1:
        month = month - 1
    else:
        year = year - 1
        month = 12
    stat_last_month = Paper.objects.filter(create_time__year=year, create_time__month=month).values('creator__nickname', 'creator__pk').annotate(Count('creator')).order_by('-creator__count')

    stat_journal = Paper.objects.values('journal').annotate(Count('journal')).order_by('-journal__count')

    template = loader.get_template('xiangma-stat.html')
    context = {
        'current_page': current_page,
        'stat_all': stat_all,
        'stat_this_month': stat_this_month,
        'stat_last_month': stat_last_month,
        'stat_journal': stat_journal,
    }
    return HttpResponse(template.render(context, request))

def xiangma_UserView(request, id, current_page):
    u = User.objects.filter(pk=id)
    if u.count() <= 0:
        return render(request, 'xiangma-list.html', {
            'error_message': "Invalid user id!",
        })
    paper_list = Paper.objects.filter(creator=u[0]).order_by('-create_time', '-pk')
    template = loader.get_template('xiangma-list.html')
    context = {
        'current_page': current_page,
        'paper_list': paper_list,
        'summary_messages': '本页面显示由用户 <b>' + u[0].nickname + '</b> 推荐的文献。',
    }
    return HttpResponse(template.render(context, request))
