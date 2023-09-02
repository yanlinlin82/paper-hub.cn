import zoneinfo

from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout

from .models import Label, Paper, User, Collection
from .forms import PaperForm
from .paper import *

tz_beijing = zoneinfo.ZoneInfo("Asia/Shanghai")

def GetCurrentUser(request):
    if not request.user.is_authenticated:
        return None
    user_list = User.objects.filter(username=request.user.username)
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
    last_week = datetime.now().astimezone(tz_beijing) - timedelta(days=7)
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

def CollectionViewByID(request, id):
    collections = Collection.objects.filter(pk=id)
    if collections.count() <= 0:
        return render(request, 'view/collection.html', {
            'error_message': 'Invalid collection ID: ' + str(id),
            'current_page': 'collection',
        })
    paper_list = collections[0].papers.order_by('-create_time', '-pk')
    template = loader.get_template('view/collection.html')
    summary_message = 'This page shows list <b>#' + str(id) + '</b>. '
    context = {
        'current_page': 'collection',
        'collection': collections[0],
        'paper_list': paper_list,
        'summary_messages': summary_message,
    }
    return HttpResponse(template.render(context, request))

def CollectionViewBySlug(request, slug):
    paper_list = get_paper_list(request).order_by('-create_time', '-pk')
    template = loader.get_template('view/list.html')
    summary_message = 'This page shows list <b>#' + str(id) + '</b>. '
    context = {
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
    template = loader.get_template('view/list.html')
    summary_message = 'This page shows list of label "<b>' + name + '</b>". '
    context = {
        'current_page': 'label',
        'paper_list': paper_list,
        'summary_messages': summary_message,
    }
    return HttpResponse(template.render(context, request))

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

def EditPaperView(request, id):
    if not request.user.is_authenticated:
        return render(request, 'view/edit.html', {
            'current_page': 'edit',
            'error_message': 'No permission! Login first!',
        })
    paper_list = get_paper_list(request).filter(pk=id)
    if paper_list.count() <= 0:
        return render(request, 'view/edit.html', {
            'current_page': 'edit',
            'error_message': 'Invalid paper ID: ' + str(id),
        })

    if request.method == 'POST':
        form = PaperForm(request.POST)
        if not form.is_valid():
            return render(request, 'view/edit.html', {
                'current_page': 'edit',
                'error_message': form.errors,
            })

        u = GetCurrentUser(request)
        paper_list = get_paper_list(request).filter(pk=id)
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
        return HttpResponseRedirect(reverse('view:paper', args=[id]))
    else:
        paper = get_paper_list(request).get(pk=id)
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
        template = loader.get_template('view/edit.html')
        context = {
            'current_page': 'edit',
            'paper': paper,
            'form': form,
        }
        return HttpResponse(template.render(context, request))

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

def PaperAdd(request):
    if not request.user.is_authenticated:
        return render(request, 'view/add.html', {
            'current_page': 'add',
            'error_message': 'No permission! Login first!',
        })
    if request.method == 'POST':
        form = PaperForm(request.POST)
        if not form.is_valid():
            return render(request, 'view/add.html', {
                'current_page': 'add',
                'error_message': form.errors,
            })

        paper = Paper()
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

        return HttpResponseRedirect(reverse('view:paper', args=[paper.id]))
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
            'current_page': 'add',
            'form': form,
            'paper': paper,
        }
        template = loader.get_template('view/add.html')
        return HttpResponse(template.render(context, request))

def Login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(request.GET['ref'])
    return render(request, 'view/login.html', {
        'ref': request.GET['ref'],
    })

def Logout(request):
    logout(request)
    return HttpResponseRedirect(request.GET['ref'])
