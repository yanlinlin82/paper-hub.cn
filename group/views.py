from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from view.models import UserProfile, GroupProfile
from api.paper import filter_reviews, get_this_week_start_time, get_check_in_interval, get_this_month, get_stat_all, get_stat_this_month, get_stat_last_month, get_stat_journal, get_last_month

def index_page(request):
    return HttpResponseRedirect('xiangma')

def my_sharing_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    user = UserProfile.objects.get(auth_user=request.user)
    reviews, items = filter_reviews(group.reviews, request.GET.get('page'), user=user)
    template = loader.get_template('group/list.html')
    context = {
        'group': group,
        'current_page': 'group_my_sharing',
        'reviews': reviews,
        'items': items,
    }
    return HttpResponse(template.render(context, request))

def all_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews, items = filter_reviews(group.reviews, request.GET.get('page'))
    template = loader.get_template('group/list.html')
    context = {
        'group': group,
        'current_page': 'group_all',
        'reviews': reviews,
        'items': items,
    }
    return HttpResponse(template.render(context, request))

def recent_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    start_time = get_this_week_start_time()
    reviews, items = filter_reviews(group.reviews, request.GET.get('page'), start_time=start_time)
    template = loader.get_template('group/list.html')
    context = {
        'group': group,
        'current_page': 'group_recent',
        'reviews': reviews,
        'items': items,
    }
    return HttpResponse(template.render(context, request))

def this_month_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    start_time, end_time = get_check_in_interval(*get_this_month())
    reviews, items = filter_reviews(group.reviews, request.GET.get('page'), start_time=start_time)
    template = loader.get_template('group/list.html')
    context = {
        'group': group,
        'current_page': 'group_this_month',
        'reviews': reviews,
        'items': items,
    }
    return HttpResponse(template.render(context, request))

def last_month_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    start_time, end_time = get_check_in_interval(*get_last_month(*get_this_month()))
    reviews, items = filter_reviews(group.reviews, request.GET.get('page'), start_time=start_time, end_time=end_time)
    template = loader.get_template('group/list.html')
    context = {
        'group': group,
        'current_page': 'group_last_month',
        'reviews': reviews,
        'items': items,
    }
    return HttpResponse(template.render(context, request))

def stat_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews = group.reviews.filter(delete_time=None)

    stat_3 = get_stat_all(reviews, group_name, top_n=10)
    stat_1 = get_stat_this_month(reviews, group_name, top_n=10)
    stat_2 = get_stat_last_month(reviews, group_name, top_n=10)
    stat_4 = get_stat_journal(reviews, group_name, top_n=10)

    template = loader.get_template('group/stat.html')
    context = {
        'group': group,
        'current_page': 'group_stat',
        'stat_1': stat_1,
        'stat_2': stat_2,
        'stat_3': stat_3,
        'stat_4': stat_4,
    }
    return HttpResponse(template.render(context, request))

def stat_this_month_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews = group.reviews.filter(delete_time=None)
    stat = get_stat_this_month(reviews, group_name)
    template = loader.get_template('group/stat-single.html')
    context = {
        'group': group,
        'current_page': 'group_stat',
        'stat': stat,
    }
    return HttpResponse(template.render(context, request))

def stat_last_month_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews = group.reviews.filter(delete_time=None)
    stat = get_stat_last_month(reviews, group_name)
    template = loader.get_template('group/stat-single.html')
    context = {
        'group': group,
        'current_page': 'group_stat',
        'stat': stat,
    }
    return HttpResponse(template.render(context, request))

def stat_all_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews = group.reviews.filter(delete_time=None)
    stat = get_stat_all(reviews, group_name)
    template = loader.get_template('group/stat-single.html')
    context = {
        'group': group,
        'current_page': 'group_stat',
        'stat': stat,
    }
    return HttpResponse(template.render(context, request))

def stat_journal_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews = group.reviews.filter(delete_time=None)
    stat = get_stat_journal(reviews, group_name)
    template = loader.get_template('group/stat-single.html')
    context = {
        'group': group,
        'current_page': 'group_stat',
        'stat': stat,
    }
    return HttpResponse(template.render(context, request))

def trash_page(request, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews, items = filter_reviews(group.reviews, request.GET.get('page'), trash=True)
    return render(request, 'group/list.html', {
        'group': group,
        'current_page': 'group_trash',
        'reviews': reviews,
        'items': items,
    })

def single_page(request, id, group_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews, items = filter_reviews(group.reviews, request.GET.get('page'), id=id)
    if reviews.paginator.count <= 0:
        return render(request, 'group/single.html', {
            'group': group,
            'current_page': 'group_paper',
            'error_message': 'Invalid paper ID: ' + str(id),
        })
    review = reviews[0]
    template = loader.get_template('group/single.html')
    context = {
        'group': group,
        'current_page': 'group_paper',
        'review': review,
        'items': items,
    }
    return HttpResponse(template.render(context, request))

def journal_page(request, group_name, journal_name):
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews, items = filter_reviews(group.reviews, request.GET.get('page'), journal_name=journal_name)
    template = loader.get_template('group/list.html')
    context = {
        'group': group,
        'current_page': 'group_user',
        'reviews': reviews,
        'items': items,
    }
    return HttpResponse(template.render(context, request))

def user_page(request, id, group_name):
    user = get_object_or_404(UserProfile, pk=id)
    group = get_object_or_404(GroupProfile, name=group_name)
    reviews, items = filter_reviews(group.reviews, request.GET.get('page'), user=user)
    template = loader.get_template('group/list.html')
    context = {
        'group': group,
        'current_page': 'group_user',
        'reviews': reviews,
        'items': items,
    }
    return HttpResponse(template.render(context, request))
