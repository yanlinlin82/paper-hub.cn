from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from django.db.models import Q, Count
from django.core import serializers

from .models import Label, Paper, User
from .forms import PaperForm

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def ajax_test(request):
    if is_ajax(request=request):
        message = "This is ajax"
    else:
        message = "Not ajax"
    return HttpResponse(message)

# Create your views here.
def AllPapersView(request, current_page):
    paper_list = Paper.objects.order_by('-create_time', '-pk')
    template = loader.get_template('list.html')
    context = {
        'current_page': current_page,
        'paper_list': paper_list,
        'summary_messages': '',
    }
    return HttpResponse(template.render(context, request))

def RecentPapersView(request, current_page):
    last_week = datetime.today() - timedelta(days=7)
    paper_list = Paper.objects.filter(create_time__gte=last_week).order_by('-create_time', '-pk')
    template = loader.get_template('list.html')
    context = {
        'current_page': current_page,
        'paper_list': paper_list,
        'summary_messages': 'This page shows papers in last week. '
    }
    return HttpResponse(template.render(context, request))

def PaperListView(request, id, current_page):
    paper_list = Paper.objects.order_by('-create_time', '-pk')
    template = loader.get_template('list.html')
    context = {
        'current_page': current_page,
        'paper_list': paper_list,
        'summary_messages': 'This page shows list <b>#' + str(id) + '</b>. ',
    }
    return HttpResponse(template.render(context, request))

def PaperLabelView(request, name, current_page):
    paper_list = None
    xiangma = Label.objects.filter(name=name)
    if xiangma.count() > 0:
        paper_list = xiangma[0].paper_set.all().order_by('-create_time', '-pk')
    template = loader.get_template('list.html')
    context = {
        'current_page': current_page,
        'paper_list': paper_list,
        'summary_messages': 'This page shows list of label "<b>' + name + '</b>". ',
    }
    return HttpResponse(template.render(context, request))

def SinglePaperView(request, id, current_page):
    paper = Paper.objects.filter(pk=id)
    template = loader.get_template('single.html')
    context = {
        'current_page': current_page,
        'paper': paper[0],
    }
    return HttpResponse(template.render(context, request))

def EditPaperView(request, id, current_page):
    paper_list = Paper.objects.filter(pk=id)
    if paper_list.count == 0:
        return render(request, 'edit.html', {
            'current_page': current_page,
            'error_message': 'Invalid paper id: ' + str(id),
        })
    paper = paper_list[0]
    if request.method == 'POST':
        form = PaperForm(request.POST)
        if form.is_valid():
            paper.doi = form.cleaned_data['doi']
            paper.pmid = form.cleaned_data['pmid']
            paper.journal = form.cleaned_data['journal']
            paper.title = form.cleaned_data['title']
            paper.abstract = form.cleaned_data['abstract']
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
            'journal': paper.journal,
            'pub_date': paper.pub_date,
            'title': paper.title,
            'authors': paper.authors,
            'abstract': paper.abstract,
            'urls': paper.urls,
            'is_private': paper.is_private,
            'comments': paper.comments,
            'full_text': paper.full_text,
        }
        form = PaperForm(data)
    template = loader.get_template('edit.html')
    context = {
        'current_page': current_page,
        'paper': paper,
        'form': form,
    }
    return HttpResponse(template.render(context, request))

def StatView(request, current_page):
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

    template = loader.get_template('stat.html')
    context = {
        'current_page': current_page,
        'stat_all': stat_all,
        'stat_this_month': stat_this_month,
        'stat_last_month': stat_last_month,
        'stat_journal': stat_journal,
    }
    return HttpResponse(template.render(context, request))

def UserView(request, id, current_page):
    u = User.objects.filter(pk=id)
    if u.count() <= 0:
        return render(request, 'list.html', {
            'error_message': "Invalid user id!",
        })
    paper_list = Paper.objects.filter(creator=u[0]).order_by('-create_time', '-pk')
    template = loader.get_template('list.html')
    context = {
        'current_page': current_page,
        'paper_list': paper_list,
        'summary_messages': 'This page shows papers recommended by <b>' + u[0].nickname + '</b>. ',
    }
    return HttpResponse(template.render(context, request))

def PaperAdd(request, current_page):
    paper = Paper()
    context = {
        'current_page': current_page,
        'paper': paper,
    }
    template = loader.get_template('add.html')
    return HttpResponse(template.render(context, request))

def PaperPostAjax(request):
    if is_ajax(request) and request.method == "POST":
        form = PaperForm(request.POST)
        if form.is_valid():
            instance = form.save()
            # serialize in new friend object in json
            ser_instance = serializers.serialize('json', [ instance, ])
            # send to client side.
            return JsonResponse({"instance": ser_instance}, status=200)
        else:
            # some form errors occured.
            return JsonResponse({"error": form.errors}, status=400)
    # some error occured
    return JsonResponse({"error": ""}, status=400)
#    title = ''
#    if request.method == 'POST' and request.POST:
#        title = request.POST['title']
#    if title:
#        p = Paper()
#        return HttpResponseRedirect(reverse('index'))
#    else:
#        template = loader.get_template('add.html')
#        context = {
#            'paper': paper,
#        }
#        return HttpResponse(template.render(context, request))
