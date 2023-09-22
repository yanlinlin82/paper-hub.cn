import zoneinfo
from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from .models import Paper, User
from .forms import PaperForm
from paperhub import settings

def GetCurrentUser(request):
    if not request.user.is_authenticated:
        return None
    user_list = User.objects.filter(auth_user__username=request.user.username)
    if user_list.count() <= 0:
        return None
    return user_list[0]

def get_paper_list(request, include_trash=False):
    u = GetCurrentUser(request)
    if u is None:
        u = User()
    if include_trash:
        return Paper.objects.filter(creator=u)
    else:
        return Paper.objects.filter(creator=u, delete_time=None)

def All(request):
    paper_list = get_paper_list(request).order_by('-create_time', '-pk')
    template = loader.get_template('view/list.html')
    context = {
        'current_page': 'all',
        'paper_list': paper_list,
        'summary_messages': '',
    }
    return HttpResponse(template.render(context, request))

def Recent(request):
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

def Favor(request):
    paper_list = get_paper_list(request).filter(is_favorite=True).order_by('-create_time', '-pk')
    summary_message = 'This page shows favorite papers. '
    template = loader.get_template('view/list.html')
    context = {
        'current_page': 'favor',
        'paper_list': paper_list,
        'summary_messages': summary_message
    }
    return HttpResponse(template.render(context, request))

def Trash(request):
    paper_list = get_paper_list(request, include_trash=True).exclude(delete_time=None).order_by('-create_time', '-pk')
    summary_message = 'Papers in this folder will be removed after 30 days automatically.'
    return render(request, 'view/list.html', {
        'current_page': 'trash',
        'paper_list': paper_list,
        'summary_messages': summary_message
    })

def SinglePaperView(request, id):
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

def RestorePaperView(request, id):
    if not request.user.is_authenticated:
        return render(request, 'base.html', {
            'current_page': 'restore_from_trash',
            'error_message': 'No permission! Login first!',
        })
    paper_list = get_paper_list(request, include_trash=True).filter(pk=id)
    if paper_list.count() <= 0:
        return render(request, 'view/list.html', {
            'current_page': 'edit',
            'error_message': 'Invalid paper ID: ' + str(id),
        })
    p = paper_list[0]
    p.delete_time = None
    p.save()
    return HttpResponseRedirect(reverse('view:paper', args=[id]))

def DeleteForeverPaperView(request, id):
    if not request.user.is_authenticated:
        return render(request, 'base.html', {
            'current_page': 'delete_forever',
            'error_message': 'No permission! Login first!',
        })
    paper_list = get_paper_list(request, include_trash=True).filter(pk=id)
    if paper_list.count() <= 0:
        return render(request, 'view/list.html', {
            'current_page': 'edit',
            'error_message': 'Invalid paper ID: ' + str(id),
        })
    get_paper_list(request, include_trash=True).filter(pk=id).delete()
    return HttpResponseRedirect(reverse('view:index'))

def DeletePaperView(request, id):
    if not request.user.is_authenticated:
        return render(request, 'base.html', {
            'current_page': 'delete',
            'error_message': 'No permission! Login first!',
        })
    paper_list = get_paper_list(request, include_trash=True).filter(pk=id)
    if paper_list.count() <= 0:
        return render(request, 'view/list.html', {
            'current_page': 'edit',
            'error_message': 'Invalid paper ID: ' + str(id),
        })
    p = paper_list[0]
    if p.delete_time == None:
        p.delete_time = timezone.now()
        p.save()
    else:
        get_paper_list(request, include_trash=True).filter(pk=id).delete()
    return HttpResponseRedirect(reverse('view:index'))

def UserView(request, id):
    u = User.objects.filter(pk=id)
    if u.count() <= 0:
        return render(request, 'view/list.html', {
            'current_page': 'list',
            'error_message': "Invalid user id!",
        })
    paper_list = get_paper_list(request).filter(creator=u[0]).order_by('-create_time', '-pk')
    template = loader.get_template('view/list.html')
    summary_message = 'This page shows papers recommended by <b>' + u[0].nickname + '</b>. '
    context = {
        'current_page': 'user',
        'paper_list': paper_list,
        'summary_messages': summary_message,
    }
    return HttpResponse(template.render(context, request))
