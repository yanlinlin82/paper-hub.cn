import re
from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from django.db.models import Q, Count
from django.core import serializers
from django.utils import timezone

from .models import Label, Paper, User
from .forms import PaperForm

def get_site_name(request):
    if re.match("^/xiangma/", request.path):
        return '响马读paper'
    return 'Paper-Hub'

def get_paper_list(request):
    if re.match("^/xiangma/", request.path):
        paper_list = None
        label_list = Label.objects.filter(name='响马')
        if label_list.count() > 0:
            paper_list = label_list[0].paper_set
        return paper_list
    return Paper.objects

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def ajax_test(request):
    if is_ajax(request=request):
        message = "This is ajax"
    else:
        message = "Not ajax"
    return HttpResponse(message)

# Create your views here.
def AllPapersView(request):
    paper_list = get_paper_list(request).order_by('-create_time', '-pk')
    template = loader.get_template('list.html')
    context = {
        'site_name': get_site_name(request),
        'current_page': 'all',
        'paper_list': paper_list,
        'summary_messages': '',
    }
    return HttpResponse(template.render(context, request))

def RecentPapersView(request):
    last_week = timezone.now() - timedelta(days=7)
    paper_list = get_paper_list(request).filter(create_time__gte=last_week).order_by('-create_time', '-pk')
    template = loader.get_template('list.html')
    context = {
        'site_name': get_site_name(request),
        'current_page': 'recent',
        'paper_list': paper_list,
        'summary_messages': 'This page shows papers in last week. '
    }
    return HttpResponse(template.render(context, request))

def PaperListView(request, id):
    paper_list = get_paper_list(request).order_by('-create_time', '-pk')
    template = loader.get_template('list.html')
    context = {
        'site_name': get_site_name(request),
        'current_page': 'list',
        'paper_list': paper_list,
        'summary_messages': 'This page shows list <b>#' + str(id) + '</b>. ',
    }
    return HttpResponse(template.render(context, request))

def PaperLabelView(request, name):
    paper_list = None
    label_list = Label.objects.filter(name=name)
    if label_list.count() > 0:
        paper_list = label_list[0].paper_set.all().order_by('-create_time', '-pk')
    template = loader.get_template('list.html')
    context = {
        'site_name': get_site_name(request),
        'current_page': 'label',
        'paper_list': paper_list,
        'summary_messages': 'This page shows list of label "<b>' + name + '</b>". ',
    }
    return HttpResponse(template.render(context, request))

def SinglePaperView(request, id):
    paper_list = get_paper_list(request).filter(pk=id)
    if paper_list.count() <= 0:
        return render(request, 'single.html', {
            'site_name': get_site_name(request),
            'current_page': 'paper',
            'error_message': 'Invalid paper ID: ' + str(id),
        })
    paper = paper_list[0]
    template = loader.get_template('single.html')
    context = {
        'site_name': get_site_name(request),
        'current_page': 'paper',
        'paper': paper,
    }
    return HttpResponse(template.render(context, request))

def EditPaperView(request, id):
    paper_list = get_paper_list(request).filter(pk=id)
    if paper_list.count() <= 0:
        return render(request, 'edit.html', {
            'site_name': get_site_name(request),
            'current_page': 'edit',
            'error_message': 'Invalid paper ID: ' + str(id),
        })
    paper = paper_list[0]
    if request.method == 'POST':
        form = PaperForm(request.POST)
        if not form.is_valid():
            return render(request, 'edit.html', {
                'site_name': get_site_name(request),
                'current_page': 'edit',
                'error_message': form.errors,
            })
        user_list = User.objects.filter(nickname=form.cleaned_data['creator'])
        if user_list.count() <= 0:
            return render(request, 'edit.html', {
                'site_name': get_site_name(request),
                'current_page': 'edit',
                'error_message': 'Invalid user "' + form.cleaned_data['creator'] + '"'
            })
        paper.creator = user_list[0]
        paper.create_time = form.cleaned_data['create_time']
        paper.update_time = form.cleaned_data['update_time']
        paper.doi = form.cleaned_data['doi']
        paper.pmid = form.cleaned_data['pmid']
        paper.arxiv_id = form.cleaned_data['arxiv_id']
        paper.pmcid = form.cleaned_data['pmcid']
        paper.cnki_id = form.cleaned_data['cnki_id']
        paper.journal = form.cleaned_data['journal']
        paper.pub_date = form.cleaned_data['pub_date']
        paper.title = form.cleaned_data['title']
        paper.authors = form.cleaned_data['authors']
        paper.abstract = form.cleaned_data['abstract']
        paper.keywords = form.cleaned_data['keywords']
        paper.urls = form.cleaned_data['urls']
        #paper.full_text = form.cleaned_data['full_text']
        paper.is_preprint = form.cleaned_data['is_preprint']
        paper.is_review = form.cleaned_data['is_review']
        paper.is_open = form.cleaned_data['is_open']
        paper.is_favorite = form.cleaned_data['is_favorite']
        paper.is_private = form.cleaned_data['is_private']
        paper.comments = form.cleaned_data['comments']
        paper.save()
        return HttpResponseRedirect(reverse('view:paper', args=[id]))
    else:
        data = {
            'creator': paper.creator,
            'create_time': paper.create_time,
            'update_time': paper.update_time,
            'doi': paper.doi,
            'pmid': paper.pmid,
            'arxiv_id': paper.arxiv_id,
            'pmcid': paper.pmcid,
            'cnki_id': paper.cnki_id,
            'journal': paper.journal,
            'pub_date': paper.pub_date,
            'title': paper.title,
            'authors': paper.authors,
            'abstract': paper.abstract,
            'keywords': paper.keywords,
            'urls': paper.urls,
            #'full_text': paper.full_text,
            'is_preprint': paper.is_preprint,
            'is_review': paper.is_review,
            'is_open': paper.is_open,
            'is_favorite': paper.is_favorite,
            'is_private': paper.is_private,
            'comments': paper.comments,
        }
        form = PaperForm(data)
        template = loader.get_template('edit.html')
        context = {
            'site_name': get_site_name(request),
            'current_page': 'edit',
            'paper': paper,
            'form': form,
        }
        return HttpResponse(template.render(context, request))

def StatView(request):
    stat_all = get_paper_list(request).values('creator__nickname', 'creator__pk').annotate(Count('creator')).order_by('-creator__count')

    today = datetime.today()
    year = today.year
    month = today.month
    stat_this_month = get_paper_list(request).filter(create_time__year=year, create_time__month=month).values('creator__nickname', 'creator__pk').annotate(Count('creator')).order_by('-creator__count')

    if month > 1:
        month = month - 1
    else:
        year = year - 1
        month = 12
    stat_last_month = get_paper_list(request).filter(create_time__year=year, create_time__month=month).values('creator__nickname', 'creator__pk').annotate(Count('creator')).order_by('-creator__count')

    stat_journal = get_paper_list(request).values('journal').annotate(Count('journal')).order_by('-journal__count')

    template = loader.get_template('stat.html')
    context = {
        'site_name': get_site_name(request),
        'current_page': 'stat',
        'stat_all': stat_all,
        'stat_this_month': stat_this_month,
        'stat_last_month': stat_last_month,
        'stat_journal': stat_journal,
    }
    return HttpResponse(template.render(context, request))

def UserView(request, id):
    u = User.objects.filter(pk=id)
    if u.count() <= 0:
        return render(request, 'list.html', {
            'site_name': get_site_name(request),
            'current_page': 'list',
            'error_message': "Invalid user id!",
        })
    paper_list = get_paper_list(request).filter(creator=u[0]).order_by('-create_time', '-pk')
    template = loader.get_template('list.html')
    context = {
        'site_name': get_site_name(request),
        'current_page': 'user',
        'paper_list': paper_list,
        'summary_messages': 'This page shows papers recommended by <b>' + u[0].nickname + '</b>. ',
    }
    return HttpResponse(template.render(context, request))

def PaperAdd(request):
    if request.method == 'POST':
        form = PaperForm(request.POST)
        if not form.is_valid():
            return render(request, 'add.html', {
                'site_name': get_site_name(request),
                'current_page': 'add',
                'error_message': form.errors,
            })
        user_list = User.objects.filter(nickname=form.cleaned_data['creator'])
        if user_list.count() <= 0:
            return render(request, 'edit.html', {
                'site_name': get_site_name(request),
                'current_page': 'add',
                'error_message': 'Invalid user "' + form.cleaned_data['creator'] + '"'
                })
        paper = Paper()
        paper.creator = user_list[0]
        paper.create_time = timezone.now()
        paper.update_time = timezone.now()
        paper.doi = form.cleaned_data['doi']
        paper.pmid = form.cleaned_data['pmid']
        paper.arxiv_id = form.cleaned_data['arxiv_id']
        paper.pmcid = form.cleaned_data['pmcid']
        paper.cnki_id = form.cleaned_data['cnki_id']
        paper.journal = form.cleaned_data['journal']
        paper.pub_date = form.cleaned_data['pub_date']
        paper.title = form.cleaned_data['title']
        paper.authors = form.cleaned_data['authors']
        paper.abstract = form.cleaned_data['abstract']
        paper.keywords = form.cleaned_data['keywords']
        paper.urls = form.cleaned_data['urls']
        #paper.full_text = form.cleaned_data['full_text']
        paper.is_preprint = form.cleaned_data['is_preprint']
        paper.is_review = form.cleaned_data['is_review']
        paper.is_open = form.cleaned_data['is_open']
        paper.is_favorite = form.cleaned_data['is_favorite']
        paper.is_private = form.cleaned_data['is_private']
        paper.comments = form.cleaned_data['comments']
        paper.save()
        return HttpResponseRedirect(reverse('view:paper', args=[paper.id]))
    else:
        u = User.objects.filter(pk=1)
        paper = Paper(
            creator = u[0],
            create_time = timezone.now(),
            update_time = timezone.now(),
            is_private = True)
        data = {
            'creator': paper.creator,
            'create_time': paper.create_time,
            'update_time': paper.update_time,
            'is_private': paper.is_private}
        form = PaperForm(data)
        context = {
            'site_name': get_site_name(request),
            'current_page': 'add',
            'form': form,
            'paper': paper,
        }
        template = loader.get_template('add.html')
        return HttpResponse(template.render(context, request))

def AjaxFetchDOI(request, doi):
    if request.method == "GET":
        print(request.GET)
        return JsonResponse({"query": { "doi": doi, "results": 123}}, status=200)
    else:
        return JsonResponse({"error": 1234}, status=400)
