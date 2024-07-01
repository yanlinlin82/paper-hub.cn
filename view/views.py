import zoneinfo
from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from .models import Review, Recommendation, PaperTracking
from paperhub import settings

def get_review_list(request, include_trash=False):
    if not request.user.is_authenticated:
        return None
    if include_trash:
        return Review.objects.filter(creator__auth_user__username=request.user.username)
    else:
        return Review.objects.filter(creator__auth_user__username=request.user.username, delete_time=None)

def recommendations_page(request):
    item_list = Recommendation.objects.filter(user__auth_user__username=request.user.username)
    for item in item_list:
        item.author_list = item.paper.authors.split('\n')
    template = loader.get_template('view/recommendations.html')
    context = {
        'current_page': 'recommendations',
        'item_list': item_list,
    }
    return HttpResponse(template.render(context, request))

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
    if review_list is not None:
        review_list = review_list.order_by('-create_time', '-pk')
    template = loader.get_template('view/list.html')
    context = {
        'current_page': 'all',
        'review_list': review_list,
        'summary_messages': '',
    }
    return HttpResponse(template.render(context, request))

def recent_page(request):
    last_week = datetime.now().astimezone(zoneinfo.ZoneInfo(settings.TIME_ZONE)) - timedelta(days=7)
    review_list = get_review_list(request)
    if review_list is not None:
        review_list = review_list.filter(create_time__gte=last_week).order_by('-create_time', '-pk')
    summary_message = 'This page shows papers in last week. '
    template = loader.get_template('view/list.html')
    context = {
        'current_page': 'recent',
        'review_list': review_list,
        'summary_messages': summary_message
    }
    return HttpResponse(template.render(context, request))

def trash_page(request):
    review_list = get_review_list(request, include_trash=True)
    if review_list is not None:
        review_list = review_list.exclude(delete_time=None).order_by('-create_time', '-pk')
    summary_message = 'Papers in this folder will be removed after 30 days automatically.'
    return render(request, 'view/list.html', {
        'current_page': 'trash',
        'review_list': review_list,
        'summary_messages': summary_message
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
        'review': review,
    }
    return HttpResponse(template.render(context, request))
