import re

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo
from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from django.db.models import Count
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.db.models.aggregates import Min

from view.models import Label, Paper, User, Collection
from view.forms import PaperForm
from view.paper import *

tz_beijing = zoneinfo.ZoneInfo("Asia/Shanghai")

def is_xiangma(group_name):
    return group_name == "xiangma"

def get_site_name(group_name):
    if is_xiangma(group_name):
        return '响马读paper'
    return 'Paper-Hub'

def GetCurrentUser(request):
    if not request.user.is_authenticated:
        return None
    user_list = User.objects.filter(username=request.user.username)
    if user_list.count() <= 0:
        return None
    return user_list[0]

def get_paper_list(request, group_name, include_trash=False):
    if group_name == "xiangma":
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

def All(request, group_name):
    paper_list = get_paper_list(request, group_name).order_by('-create_time', '-pk')
    template = loader.get_template('group/list.html')
    context = {
        'site_name': get_site_name(group_name),
        'group_name': group_name,
        'current_page': 'all',
        'paper_list': paper_list,
        'summary_messages': '',
    }
    return HttpResponse(template.render(context, request))

def Recent(request, group_name):
    if is_xiangma(group_name):
        today = datetime.today().astimezone(tz_beijing)
        year = today.year
        month = today.month
        paper_list = get_paper_list(request, group_name).filter(create_time__year=year, create_time__month=month).order_by('-create_time', '-pk')
        summary_message = '本页面显示本月的文献分享。'
    else:
        last_week = datetime.now().astimezone(tz_beijing) - timedelta(days=7)
        paper_list = get_paper_list(request, group_name).filter(create_time__gte=last_week).order_by('-create_time', '-pk')
        summary_message = 'This page shows papers in last week. '
    template = loader.get_template('group/list.html')
    context = {
        'site_name': get_site_name(group_name),
        'group_name': group_name,
        'current_page': 'recent',
        'paper_list': paper_list,
        'summary_messages': summary_message
    }
    return HttpResponse(template.render(context, request))

def Favor(request, group_name):
    paper_list = get_paper_list(request, group_name).filter(is_favorite=True).order_by('-create_time', '-pk')
    summary_message = 'This page shows favorite papers. '
    template = loader.get_template('group/list.html')
    context = {
        'site_name': get_site_name(group_name),
        'group_name': group_name,
        'current_page': 'favor',
        'paper_list': paper_list,
        'summary_messages': summary_message
    }
    return HttpResponse(template.render(context, request))

def Trash(request, group_name):
    paper_list = get_paper_list(request, group_name, include_trash=True).exclude(delete_time=None).order_by('-create_time', '-pk')
    summary_message = 'Papers in this folder will be removed after 30 days automatically.'
    return render(request, 'group/list.html', {
        'site_name': get_site_name(group_name),
        'group_name': group_name,
        'current_page': 'trash',
        'paper_list': paper_list,
        'summary_messages': summary_message
    })

def CollectionViewByID(request, id, group_name):
    collections = Collection.objects.filter(pk=id)
    if collections.count() <= 0:
        return render(request, 'group/collection.html', {
            'error_message': 'Invalid collection ID: ' + str(id),
            'site_name': get_site_name(group_name),
            'group_name': group_name,
            'current_page': 'collection',
        })
    paper_list = collections[0].papers.order_by('-create_time', '-pk')
    template = loader.get_template('group/collection.html')
    if is_xiangma(group_name):
        summary_message = '本页面显示合集 <b>#' + collections[0].name + '</b> 的文献。'
    else:
        summary_message = 'This page shows list <b>#' + str(id) + '</b>. '
    context = {
        'site_name': get_site_name(group_name),
        'group_name': group_name,
        'current_page': 'collection',
        'collection': collections[0],
        'paper_list': paper_list,
        'summary_messages': summary_message,
    }
    return HttpResponse(template.render(context, request))

def CollectionViewBySlug(request, slug, group_name):
    paper_list = get_paper_list(request, group_name).order_by('-create_time', '-pk')
    template = loader.get_template('group/list.html')
    if is_xiangma(group_name):
        summary_message = '本页面显示列表 <b>#' + str(id) + '</b> 的文献。'
    else:
        summary_message = 'This page shows list <b>#' + str(id) + '</b>. '
    context = {
        'site_name': get_site_name(group_name),
        'group_name': group_name,
        'current_page': 'collection',
        'paper_list': paper_list,
        'summary_messages': summary_message,
    }
    return HttpResponse(template.render(context, request))

def PaperLabelView(request, name, group_name):
    paper_list = None
    label_list = Label.objects.filter(name=name)
    if label_list.count() > 0:
        paper_list = label_list[0].paper_set.all().order_by('-create_time', '-pk')
    template = loader.get_template('group/list.html')
    if is_xiangma(group_name):
        summary_message = '本页面显示标签 <b>' + name + '</b> 的文献。'
    else:
        summary_message = 'This page shows list of label "<b>' + name + '</b>". '
    context = {
        'site_name': get_site_name(group_name),
        'group_name': group_name,
        'current_page': 'label',
        'paper_list': paper_list,
        'summary_messages': summary_message,
    }
    return HttpResponse(template.render(context, request))

def SinglePaperView(request, id, group_name):
    paper_list = get_paper_list(request, group_name).filter(pk=id)
    if paper_list.count() <= 0:
        return render(request, 'group/single.html', {
            'site_name': get_site_name(group_name),
            'group_name': group_name,
            'current_page': 'paper',
            'error_message': 'Invalid paper ID: ' + str(id),
        })
    paper = paper_list[0]
    template = loader.get_template('group/single.html')
    context = {
        'site_name': get_site_name(group_name),
        'group_name': group_name,
        'current_page': 'paper',
        'paper': paper,
    }
    return HttpResponse(template.render(context, request))

def RestorePaperView(request, id, group_name):
    if not request.user.is_authenticated:
        return render(request, 'group/base.html', {
            'site_name': get_site_name(group_name),
            'group_name': group_name,
            'current_page': 'restore_from_trash',
            'error_message': 'No permission! Login first!',
        })
    paper_list = get_paper_list(request, group_name, include_trash=True).filter(pk=id)
    if paper_list.count() <= 0:
        return render(request, 'group/list.html', {
            'site_name': get_site_name(group_name),
            'group_name': group_name,
            'current_page': 'edit',
            'error_message': 'Invalid paper ID: ' + str(id),
        })
    p = paper_list[0]
    p.delete_time = None
    p.save()
    return HttpResponseRedirect(reverse('group:paper', args=[id], current_app=request.resolver_match.namespace))

def DeleteForeverPaperView(request, id, group_name):
    if not request.user.is_authenticated:
        return render(request, 'group/base.html', {
            'site_name': get_site_name(group_name),
            'group_name': group_name,
            'current_page': 'delete_forever',
            'error_message': 'No permission! Login first!',
        })
    paper_list = get_paper_list(request, group_name, include_trash=True).filter(pk=id)
    if paper_list.count() <= 0:
        return render(request, 'group/list.html', {
            'site_name': get_site_name(group_name),
            'group_name': group_name,
            'current_page': 'edit',
            'error_message': 'Invalid paper ID: ' + str(id),
        })
    get_paper_list(request, group_name, include_trash=True).filter(pk=id).delete()
    return HttpResponseRedirect(reverse('group:index', current_app=request.resolver_match.namespace))

def DeletePaperView(request, id, group_name):
    if not request.user.is_authenticated:
        return render(request, 'group/base.html', {
            'site_name': get_site_name(group_name),
            'group_name': group_name,
            'current_page': 'delete',
            'error_message': 'No permission! Login first!',
        })
    paper_list = get_paper_list(request, group_name, include_trash=True).filter(pk=id)
    if paper_list.count() <= 0:
        return render(request, 'group/list.html', {
            'site_name': get_site_name(group_name),
            'group_name': group_name,
            'current_page': 'edit',
            'error_message': 'Invalid paper ID: ' + str(id),
        })
    p = paper_list[0]
    if p.delete_time == None:
        p.delete_time = timezone.now()
        p.save()
    else:
        get_paper_list(request, group_name, include_trash=True).filter(pk=id).delete()
    return HttpResponseRedirect(reverse('group:index', current_app=request.resolver_match.namespace))

def EditPaperView(request, id, group_name):
    if not request.user.is_authenticated:
        return render(request, 'group/edit.html', {
            'site_name': get_site_name(group_name),
            'group_name': group_name,
            'current_page': 'edit',
            'error_message': 'No permission! Login first!',
            'is_xiangma': is_xiangma(group_name),
        })
    paper_list = get_paper_list(request, group_name).filter(pk=id)
    if paper_list.count() <= 0:
        return render(request, 'group/edit.html', {
            'site_name': get_site_name(group_name),
            'group_name': group_name,
            'current_page': 'edit',
            'error_message': 'Invalid paper ID: ' + str(id),
            'is_xiangma': is_xiangma(group_name),
        })

    if request.method == 'POST':
        form = PaperForm(request.POST)
        if not form.is_valid():
            return render(request, 'group/edit.html', {
                'site_name': get_site_name(group_name),
                'group_name': group_name,
                'current_page': 'edit',
                'error_message': form.errors,
                'is_xiangma': is_xiangma(group_name),
            })

        if is_xiangma(group_name):
            u = AddUserIfNotExist(
                form.cleaned_data['creator_nickname'],
                form.cleaned_data['creator_name'],
                form.cleaned_data['creator_weixin_id'],
                form.cleaned_data['creator_username']
            )
        else:
            u = GetCurrentUser(request)
        paper_list = get_paper_list(request, group_name).filter(pk=id)
        paper_list.update(creator = u)

        paper = paper_list[0]
        if form.cleaned_data['create_time']:
            paper.create_time = form.cleaned_data['create_time']
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
        return HttpResponseRedirect(reverse('group:paper', args=[id], current_app=request.resolver_match.namespace))
    else:
        paper = get_paper_list(request, group_name).get(pk=id)
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
        template = loader.get_template('group/edit.html')
        context = {
            'site_name': get_site_name(group_name),
            'group_name': group_name,
            'current_page': 'edit',
            'paper': paper,
            'form': form,
            'is_xiangma': is_xiangma(group_name),
        }
        return HttpResponse(template.render(context, request))

def StatView(request, group_name):
    stat_all = get_paper_list(request, group_name).values('creator__nickname', 'creator__pk').annotate(Count('creator')).order_by('-creator__count')

    today = datetime.today().astimezone(tz_beijing)
    year = today.year
    month = today.month
    stat_this_month = get_paper_list(request, group_name).filter(create_time__year=year, create_time__month=month).values('creator__nickname', 'creator__pk').annotate(Count('creator'), min_create_time=Min('create_time')).order_by('-creator__count', 'min_create_time')
    this_month = str(year) + '/' + str(month)

    if month > 1:
        month = month - 1
    else:
        year = year - 1
        month = 12
    stat_last_month = get_paper_list(request, group_name).filter(create_time__year=year, create_time__month=month).values('creator__nickname', 'creator__pk').annotate(Count('creator'), min_create_time=Min('create_time')).order_by('-creator__count', 'min_create_time')
    last_month = str(year) + '/' + str(month)

    stat_journal = get_paper_list(request, group_name).exclude(journal='').values('journal').annotate(Count('journal'), min_create_time=Min('create_time')).order_by('-journal__count', 'min_create_time')

    template = loader.get_template('group/stat.html')
    context = {
        'site_name': get_site_name(group_name),
        'group_name': group_name,
        'current_page': 'stat',
        'stat_all': stat_all,
        'stat_this_month': stat_this_month,
        'this_month': this_month,
        'stat_last_month': stat_last_month,
        'last_month': last_month,
        'stat_journal': stat_journal,
    }
    return HttpResponse(template.render(context, request))

def UserView(request, id, group_name):
    u = User.objects.filter(pk=id)
    if u.count() <= 0:
        return render(request, 'group/list.html', {
            'site_name': get_site_name(group_name),
            'group_name': group_name,
            'current_page': 'list',
            'error_message': "Invalid user id!",
        })
    paper_list = get_paper_list(request, group_name).filter(creator=u[0]).order_by('-create_time', '-pk')
    template = loader.get_template('group/list.html')
    if is_xiangma(group_name):
        summary_message = '本页面显示由用户 <b>' + u[0].nickname + '</b> 推荐的文献。'
    else:
        summary_message = 'This page shows papers recommended by <b>' + u[0].nickname + '</b>. '
    context = {
        'site_name': get_site_name(group_name),
        'group_name': group_name,
        'current_page': 'user',
        'paper_list': paper_list,
        'summary_messages': summary_message,
    }
    return HttpResponse(template.render(context, request))

def AddUserIfNotExist(a_nickname, a_name, a_weixin_id, a_username):
    if a_nickname != "":
        user_list = User.objects.filter(nickname=a_nickname)
        if user_list.count() > 0:
            if user_list[0].name != a_name:
                user_list.update(name=a_name)
            if user_list[0].weixin_id != a_weixin_id:
                user_list.update(weixin_id=a_weixin_id)
            if user_list[0].username != a_username:
                user_list[0].update(username=a_username)
            return user_list[0]
    if a_name != "":
        user_list = User.objects.filter(name=a_name)
        if user_list.count() > 0:
            if user_list[0].nickname != a_nickname:
                user_list.update(nickname=a_nickname)
            if user_list[0].weixin_id != a_weixin_id:
                user_list.update(weixin_id=a_weixin_id)
            if user_list[0].username != a_username:
                user_list[0].update(username=a_username)
            return user_list[0]
    if a_weixin_id != "":
        user_list = User.objects.filter(weixin_id=a_weixin_id)
        if user_list.count() > 0:
            if user_list[0].name != a_name:
                user_list.update(name=a_name)
            if user_list[0].nickname != a_nickname:
                user_list.update(nickname=a_nickname)
            if user_list[0].username != a_username:
                user_list[0].update(username=a_username)
            return user_list[0]
    if a_username != "":
        user_list = User.objects.filter(username=a_username)
        if user_list.count() > 0:
            if user_list[0].name != a_name:
                user_list.update(name=a_name)
            if user_list[0].nickname != a_nickname:
                user_list.update(nickname=a_nickname)
            if user_list[0].weixin_id != a_weixin_id:
                user_list.update(weixin_id=a_weixin_id)
            return user_list[0]
    u = User(
        username = a_username,
        nickname = a_nickname,
        weixin_id = a_weixin_id,
        name = a_name,
        create_time = timezone.now()
    )
    u.save()
    return u

def PaperAdd(request, group_name):
    if not request.user.is_authenticated:
        return render(request, 'group/add.html', {
            'site_name': get_site_name(group_name),
            'group_name': group_name,
            'current_page': 'add',
            'error_message': 'No permission! Login first!',
            'is_xiangma': is_xiangma(group_name),
        })
    if request.method == 'POST':
        form = PaperForm(request.POST)
        if not form.is_valid():
            return render(request, 'group/add.html', {
                'site_name': get_site_name(group_name),
                'group_name': group_name,
                'current_page': 'add',
                'error_message': form.errors,
                'is_xiangma': is_xiangma(group_name),
            })

        paper = Paper()
        if is_xiangma(group_name):
            paper.creator = AddUserIfNotExist(
                form.cleaned_data['creator_nickname'],
                form.cleaned_data['creator_name'],
                form.cleaned_data['creator_weixin_id'],
                form.cleaned_data['creator_username']
            )
        else:
            paper.creator = GetCurrentUser(request)
    
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

        if is_xiangma(group_name):
            paper.create_time = form.cleaned_data['create_time']
            paper.save()

        if is_xiangma(group_name):
            label_name = "响马"
            if Label.objects.filter(name=label_name).count() == 0:
                xiangma = Label(name = label_name)
                xiangma.save()
            else:
                xiangma = Label.objects.filter(name=label_name)[0]
            xiangma.paper_set.add(paper)
            xiangma.save()

        return HttpResponseRedirect(reverse('group:paper', args=[paper.id], current_app=request.resolver_match.namespace))
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
            'site_name': get_site_name(group_name),
            'group_name': group_name,
            'current_page': 'add',
            'form': form,
            'paper': paper,
            'is_xiangma': is_xiangma(group_name),
        }
        template = loader.get_template('group/add.html')
        return HttpResponse(template.render(context, request))

def AjaxFetchUser(request, user):
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
    if request.method != "GET":
        return JsonResponse({"error": "Invalid http query"}, status=400)
    pattern_pubmed = re.compile('^[0-9]+$')
    if pattern_pubmed.search(id):
        return query_pubmed(id)
    pattern_arxiv = re.compile('^10\.48550\/arXiv\.([0-9]+\.[0-9]+)$')
    m = pattern_arxiv.match(id)
    if m:
        arxiv_id = m.group(1)
        return query_arxiv(arxiv_id)
    else:
        return query_doi(id)

def Login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('group:index', current_app=request.resolver_match.namespace))
    return render(request, 'group/login.html', {
        'site_name': get_site_name(group_name),
        'group_name': group_name,
    })

def Logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('group:index', current_app=request.resolver_match.namespace))