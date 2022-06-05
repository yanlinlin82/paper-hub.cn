import re
import requests
import json

from backports import zoneinfo
from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from django.db.models import Q, Count
from django.core import serializers
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.db.models.aggregates import Min, Max

from .models import Label, Paper, User, CrossRefCache, Collection
from .forms import PaperForm

tz_beijing = zoneinfo.ZoneInfo("Asia/Shanghai")

def is_xiangma(request):
    return re.match("^/xiangma/", request.path)

def get_site_name(request):
    if is_xiangma(request):
        return '响马读paper'
    return 'Paper-Hub'

def GetCurrentUser(request):
    if not request.user.is_authenticated:
        return None
    user_list = User.objects.filter(username=request.user.username)
    if user_list.count() <= 0:
        return None
    return user_list[0]

def get_paper_list(request, include_trash=False):
    if re.match("^/xiangma/", request.path):
        paper_list = None
        label_list = Label.objects.filter(name='响马')
        if label_list.count() > 0:
            paper_list = label_list[0].paper_set
        return paper_list

    u = GetCurrentUser(request)
    if u is None:
        u = User()
    if include_trash:
        return Paper.objects.filter(creator=u)
    else:
        return Paper.objects.filter(creator=u, delete_time=None)

def All(request):
    paper_list = get_paper_list(request).order_by('-create_time', '-pk')
    template = loader.get_template('list.html')
    context = {
        'site_name': get_site_name(request),
        'current_page': 'all',
        'paper_list': paper_list,
        'summary_messages': '',
    }
    return HttpResponse(template.render(context, request))

def Recent(request):
    if is_xiangma(request):
        today = datetime.today().astimezone(tz_beijing)
        year = today.year
        month = today.month
        print("Recent: ", today, ", ", year, ", ", month)
        paper_list = get_paper_list(request).filter(create_time__year=year, create_time__month=month).order_by('-create_time', '-pk')
        summary_message = '本页面显示本月的文献分享。'
    else:
        last_week = datetime.now().astimezone(tz_beijing) - timedelta(days=7)
        print("last_week: ", last_week)
        paper_list = get_paper_list(request).filter(create_time__gte=last_week).order_by('-create_time', '-pk')
        summary_message = 'This page shows papers in last week. '
    template = loader.get_template('list.html')
    context = {
        'site_name': get_site_name(request),
        'current_page': 'recent',
        'paper_list': paper_list,
        'summary_messages': summary_message
    }
    return HttpResponse(template.render(context, request))

def Favor(request):
    paper_list = get_paper_list(request).filter(is_favorite=True).order_by('-create_time', '-pk')
    summary_message = 'This page shows favorite papers. '
    template = loader.get_template('list.html')
    context = {
        'site_name': get_site_name(request),
        'current_page': 'favor',
        'paper_list': paper_list,
        'summary_messages': summary_message
    }
    return HttpResponse(template.render(context, request))

def Trash(request):
    paper_list = get_paper_list(request, include_trash=True).exclude(delete_time=None).order_by('-create_time', '-pk')
    summary_message = 'Papers in this folder will be removed after 30 days automatically.'
    return render(request, 'list.html', {
        'site_name': get_site_name(request),
        'current_page': 'trash',
        'paper_list': paper_list,
        'summary_messages': summary_message
    })

def CollectionViewByID(request, id):
    collections = Collection.objects.filter(pk=id)
    if collections.count() <= 0:
        return render(request, 'collection.html', {
            'error_message': 'Invalid collection ID: ' + str(id),
            'site_name': get_site_name(request),
            'current_page': 'collection',
        })
    paper_list = collections[0].papers.order_by('-create_time', '-pk')
    template = loader.get_template('collection.html')
    if is_xiangma(request):
        summary_message = '本页面显示合集 <b>#' + collections[0].name + '</b> 的文献。'
    else:
        summary_message = 'This page shows list <b>#' + str(id) + '</b>. '
    context = {
        'site_name': get_site_name(request),
        'current_page': 'collection',
        'collection': collections[0],
        'paper_list': paper_list,
        'summary_messages': summary_message,
    }
    return HttpResponse(template.render(context, request))

def CollectionViewBySlug(request, slug):
    paper_list = get_paper_list(request).order_by('-create_time', '-pk')
    template = loader.get_template('list.html')
    if is_xiangma(request):
        summary_message = '本页面显示列表 <b>#' + str(id) + '</b> 的文献。'
    else:
        summary_message = 'This page shows list <b>#' + str(id) + '</b>. '
    context = {
        'site_name': get_site_name(request),
        'current_page': 'collection',
        'paper_list': paper_list,
        'summary_messages': summary_message,
    }
    return HttpResponse(template.render(context, request))

def PaperLabelView(request, name):
    paper_list = None
    label_list = Label.objects.filter(name=name)
    if label_list.count() > 0:
        paper_list = label_list[0].paper_set.all().order_by('-create_time', '-pk')
    template = loader.get_template('list.html')
    if is_xiangma(request):
        summary_message = '本页面显示标签 <b>' + name + '</b> 的文献。'
    else:
        summary_message = 'This page shows list of label "<b>' + name + '</b>". '
    context = {
        'site_name': get_site_name(request),
        'current_page': 'label',
        'paper_list': paper_list,
        'summary_messages': summary_message,
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
    print(paper.create_time)
    return HttpResponse(template.render(context, request))

def RestorePaperView(request, id):
    if not request.user.is_authenticated:
        return render(request, 'base.html', {
            'site_name': get_site_name(request),
            'current_page': 'restore_from_trash',
            'error_message': 'No permission! Login first!',
        })
    paper_list = get_paper_list(request, include_trash=True).filter(pk=id)
    if paper_list.count() <= 0:
        return render(request, 'list.html', {
            'site_name': get_site_name(request),
            'current_page': 'edit',
            'error_message': 'Invalid paper ID: ' + str(id),
        })
    p = paper_list[0]
    p.delete_time = None
    p.save()
    return HttpResponseRedirect(reverse('view:paper', args=[id], current_app=request.resolver_match.namespace))

def DeleteForeverPaperView(request, id):
    if not request.user.is_authenticated:
        return render(request, 'base.html', {
            'site_name': get_site_name(request),
            'current_page': 'delete_forever',
            'error_message': 'No permission! Login first!',
        })
    paper_list = get_paper_list(request, include_trash=True).filter(pk=id)
    if paper_list.count() <= 0:
        return render(request, 'list.html', {
            'site_name': get_site_name(request),
            'current_page': 'edit',
            'error_message': 'Invalid paper ID: ' + str(id),
        })
    get_paper_list(request, include_trash=True).filter(pk=id).delete()
    return HttpResponseRedirect(reverse('view:index', current_app=request.resolver_match.namespace))

def DeletePaperView(request, id):
    if not request.user.is_authenticated:
        return render(request, 'base.html', {
            'site_name': get_site_name(request),
            'current_page': 'delete',
            'error_message': 'No permission! Login first!',
        })
    paper_list = get_paper_list(request, include_trash=True).filter(pk=id)
    if paper_list.count() <= 0:
        return render(request, 'list.html', {
            'site_name': get_site_name(request),
            'current_page': 'edit',
            'error_message': 'Invalid paper ID: ' + str(id),
        })
    p = paper_list[0]
    if p.delete_time == None:
        p.delete_time = timezone.now()
        p.save()
    else:
        get_paper_list(request, include_trash=True).filter(pk=id).delete()
    return HttpResponseRedirect(reverse('view:index', current_app=request.resolver_match.namespace))

def EditPaperView(request, id):
    if not request.user.is_authenticated:
        return render(request, 'edit.html', {
            'site_name': get_site_name(request),
            'current_page': 'edit',
            'error_message': 'No permission! Login first!',
            'is_xiangma': is_xiangma(request),
        })
    paper_list = get_paper_list(request).filter(pk=id)
    if paper_list.count() <= 0:
        return render(request, 'edit.html', {
            'site_name': get_site_name(request),
            'current_page': 'edit',
            'error_message': 'Invalid paper ID: ' + str(id),
            'is_xiangma': is_xiangma(request),
        })
    paper = paper_list[0]
    if request.method == 'POST':
        form = PaperForm(request.POST)
        if not form.is_valid():
            return render(request, 'edit.html', {
                'site_name': get_site_name(request),
                'current_page': 'edit',
                'error_message': form.errors,
                'is_xiangma': is_xiangma(request),
            })

        paper.creator = AddUserIfNotExist(
            form.cleaned_data['creator_nickname'],
            form.cleaned_data['creator_name'],
            form.cleaned_data['creator_weixin_id'],
            form.cleaned_data['creator_username']
        )

        if form.cleaned_data['create_time']:
            paper.create_time = form.cleaned_data['create_time']
        else:
            paper.create_time = timezone.now()
        if form.cleaned_data['update_time']:
            paper.update_time = form.cleaned_data['update_time']
        else:
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
        return HttpResponseRedirect(reverse('view:paper', args=[id], current_app=request.resolver_match.namespace))
    else:
        data = {
            'creator_nickname': paper.creator.nickname,
            'creator_name': paper.creator.name,
            'creator_weixin_id': paper.creator.weixin_id,
            'creator_username': paper.creator.username,
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
            'is_xiangma': is_xiangma(request),
        }
        return HttpResponse(template.render(context, request))

def StatView(request):
    stat_all = get_paper_list(request).values('creator__nickname', 'creator__pk').annotate(Count('creator')).order_by('-creator__count')

    today = datetime.today().astimezone(tz_beijing)
    year = today.year
    month = today.month
    stat_this_month = get_paper_list(request).filter(create_time__year=year, create_time__month=month).values('creator__nickname', 'creator__pk').annotate(Count('creator'), min_create_time=Min('create_time')).order_by('-creator__count', 'min_create_time')
    this_month = str(year) + '/' + str(month)

    if month > 1:
        month = month - 1
    else:
        year = year - 1
        month = 12
    stat_last_month = get_paper_list(request).filter(create_time__year=year, create_time__month=month).values('creator__nickname', 'creator__pk').annotate(Count('creator'), min_create_time=Min('create_time')).order_by('-creator__count', 'min_create_time')
    last_month = str(year) + '/' + str(month)

    stat_journal = get_paper_list(request).exclude(journal='').values('journal').annotate(Count('journal'), min_create_time=Min('create_time')).order_by('-journal__count', 'min_create_time')

    template = loader.get_template('stat.html')
    context = {
        'site_name': get_site_name(request),
        'current_page': 'stat',
        'stat_all': stat_all,
        'stat_this_month': stat_this_month,
        'this_month': this_month,
        'stat_last_month': stat_last_month,
        'last_month': last_month,
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
    if is_xiangma(request):
        summary_message = '本页面显示由用户 <b>' + u[0].nickname + '</b> 推荐的文献。'
    else:
        summary_message = 'This page shows papers recommended by <b>' + u[0].nickname + '</b>. '
    context = {
        'site_name': get_site_name(request),
        'current_page': 'user',
        'paper_list': paper_list,
        'summary_messages': summary_message,
    }
    return HttpResponse(template.render(context, request))

def AddUserIfNotExist(nickname, name, weixin_id, username):
    user_list = User.objects.filter(nickname=nickname)
    if user_list.count() > 0:
        return user_list[0]
    u = User(
        username = username,
        nickname = nickname,
        weixin_id = weixin_id,
        name = name,
        create_time = timezone.now()
    )
    u.save()
    return u

def PaperAdd(request):
    if not request.user.is_authenticated:
        return render(request, 'add.html', {
            'site_name': get_site_name(request),
            'current_page': 'add',
            'error_message': 'No permission! Login first!',
            'is_xiangma': is_xiangma(request),
        })
    if request.method == 'POST':
        form = PaperForm(request.POST)
        if not form.is_valid():
            print("form invalid")
            print(request.POST)
            return render(request, 'add.html', {
                'site_name': get_site_name(request),
                'current_page': 'add',
                'error_message': form.errors,
                'is_xiangma': is_xiangma(request),
            })

        paper = Paper()
        if is_xiangma(request):
            paper.creator = AddUserIfNotExist(
                form.cleaned_data['creator_nickname'],
                form.cleaned_data['creator_name'],
                form.cleaned_data['creator_weixin_id'],
                form.cleaned_data['creator_username']
            )
        else:
            paper.creator = GetCurrentUser(request)
    
        if is_xiangma(request):
            paper.create_time = form.cleaned_data['create_time']
            paper.update_time = form.cleaned_data['create_time']
        else:
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

        if is_xiangma(request):
            label_name = "响马"
            if Label.objects.filter(name=label_name).count() == 0:
                xiangma = Label(name = label_name)
                xiangma.save()
            else:
                xiangma = Label.objects.filter(name=label_name)[0]
            xiangma.paper_set.add(paper)
            xiangma.save()

        return HttpResponseRedirect(reverse('view:paper', args=[paper.id], current_app=request.resolver_match.namespace))
    else:
        u = User.objects.filter(username=request.user)
        paper = Paper(
            creator = u[0],
            create_time = timezone.now(),
            update_time = timezone.now(),
            is_private = True)
        data = {
            'creator_nickname': u[0].nickname,
            'creator_name': u[0].name,
            'creator_weixin_id': u[0].weixin_id,
            'creator_username': u[0].username,
            'create_time': paper.create_time,
            'update_time': paper.update_time,
            'is_private': paper.is_private
            }
        form = PaperForm(data)
        context = {
            'site_name': get_site_name(request),
            'current_page': 'add',
            'form': form,
            'paper': paper,
            'is_xiangma': is_xiangma(request),
        }
        template = loader.get_template('add.html')
        return HttpResponse(template.render(context, request))

def AjaxFetchUser(request, user):
    print("User query: ", user)
    if request.method != "GET":
        return JsonResponse({"error": "Invalid http query"}, status=400)
    u = User.objects.filter(nickname=user)
    if u.count() == 0:
        u = User.objects.filter(name=user)
    if u.count() == 0:
        u = User.objects.filter(weixin_id=user)
    if u.count() == 0:
        u = User.objects.filter(username=user)
    if u.count() == 0:
        return JsonResponse({"error": "user '" + user + "' not found."}, status=200)
    else:
        return JsonResponse({"error": "", "query": user, "results": {
            "nickname": u[0].nickname,
            "name": u[0].name,
            "weixin_id": u[0].weixin_id,
            "username": u[0].username,
        }}, status=200)

def AjaxFetchPaper(request, id):
    print("Fetch Paper: ", id)
    if request.method != "GET":
        return JsonResponse({"error": "Invalid http query"}, status=400)
    doi = id
    cache = CrossRefCache.objects.filter(type=CrossRefCache.DOI, key=doi)
    if cache.count() == 0:
        print("load from query")
        try:
            url = 'http://api.crossref.org/works/' + doi
            data = requests.get(url).json()
        except:
            return JsonResponse({"error": "Failed to query json from URL: " + url}, status=400)
        item = CrossRefCache(type=CrossRefCache.DOI, key=doi, value=json.dumps(data))
        item.save()
    else:
        print("load from cache")
        data = json.loads(cache[0].value)

    try:
        type = data["message"]["type"]
    except:
        type = ""

    try:
        title = " ".join(data["message"]["title"])
    except:
        title = ""
    
    try:
        journal = " ".join(data["message"]["container-title"])
    except:
        journal = ""

    try:
        pub_date = data["message"]["created"]["date-time"][0:10]
    except:
        pub_date = ""
    
    try:
        issue = data["message"]["issue"]
    except:
        issue = ""

    try:
        volume = data["message"]["volume"]
    except:
        volume = ""

    try:
        page = data["message"]["page"]
    except:
        page = ""

    try:
        abstract = data["message"]["abstract"]
    except:
        abstract = ""

    try:
        authors = "\n".join(node["given"] + " " + node["family"] for node in data["message"]["author"])
    except:
        authors = ""

    try:
        urls = "\n".join(node["URL"] for node in data["message"]["link"])
    except:
        urls = ""

    return JsonResponse({"error": "", "doi": doi, "results": {
        "doi": doi,
        "type": type,
        "title": title,
        "journal": journal,
        "pub_date": pub_date,
        "issue": issue,
        "volume": volume,
        "page": page,
        "authors": authors,
        "abstract": abstract,
        "urls": urls,
    }}, status=200)

def AjaxFetchDOI(request, doi):
    print("DOI query: ", doi)
    if request.method != "GET":
        return JsonResponse({"error": "Invalid http query"}, status=400)
    cache = CrossRefCache.objects.filter(type=CrossRefCache.DOI, key=doi)
    if cache.count() == 0:
        print("load from query")
        try:
            url = 'http://api.crossref.org/works/' + doi
            data = requests.get(url).json()
        except:
            return JsonResponse({"error": "Failed to query json from URL: " + url}, status=400)
        item = CrossRefCache(type=CrossRefCache.DOI, key=doi, value=json.dumps(data))
        item.save()
    else:
        print("load from cache")
        data = json.loads(cache[0].value)
    return JsonResponse({"error": "", "doi": doi, "results": data}, status=200)

def Login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('view:index', current_app=request.resolver_match.namespace))
    return render(request, 'login.html', {
        'site_name': get_site_name(request),
    })

def Logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('view:index', current_app=request.resolver_match.namespace))
