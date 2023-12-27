import zoneinfo
from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from .models import Paper, UserProfile
from paperhub import settings

def get_paper_list(request, include_trash=False):
    if not request.user.is_authenticated:
        return None
    if include_trash:
        return Paper.objects.filter(creator__auth_user__username=request.user.username)
    else:
        return Paper.objects.filter(creator__auth_user__username=request.user.username, delete_time=None)

def all_page(request):
    paper_list = get_paper_list(request).order_by('-create_time', '-pk')
    template = loader.get_template('view/list.html')
    context = {
        'current_page': 'all',
        'paper_list': paper_list,
        'summary_messages': '',
    }
    return HttpResponse(template.render(context, request))

def recent_page(request):
    last_week = datetime.now().astimezone(zoneinfo.ZoneInfo(settings.TIME_ZONE)) - timedelta(days=7)
    paper_list = get_paper_list(request).filter(create_time__gte=last_week).order_by('-create_time', '-pk')
    summary_message = 'This page shows papers in last week. '
    template = loader.get_template('view/list.html')
    context = {
        'current_page': 'recent',
        'paper_list': paper_list,
        'summary_messages': summary_message
    }
    return HttpResponse(template.render(context, request))

def trash_page(request):
    paper_list = get_paper_list(request, include_trash=True).exclude(delete_time=None).order_by('-create_time', '-pk')
    summary_message = 'Papers in this folder will be removed after 30 days automatically.'
    return render(request, 'view/list.html', {
        'current_page': 'trash',
        'paper_list': paper_list,
        'summary_messages': summary_message
    })

def single_page(request, id):
    paper_list = get_paper_list(request).filter(pk=id)
    if paper_list.count() <= 0:
        return render(request, 'view/single.html', {
            'current_page': 'paper',
            'error_message': 'Invalid paper ID: ' + str(id),
        })
    paper = paper_list[0]
    template = loader.get_template('view/single.html')
    context = {
        'current_page': 'paper',
        'paper': paper,
    }
    return HttpResponse(template.render(context, request))
