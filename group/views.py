import re
import zoneinfo
from datetime import datetime, timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.db.models.aggregates import Min
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from view.models import Label, Paper, User, Collection
from view.forms import PaperForm
from .models import Group

tz_beijing = zoneinfo.ZoneInfo("Asia/Shanghai")

def GetCurrentUser(request):
    if not request.user.is_authenticated:
        return None
    user_list = User.objects.filter(username=request.user.username)
    if user_list.count() <= 0:
        return None
    return user_list[0]

def get_paper_list(request, group_name, latest_month=False, latest_week=False, user=None, id=None, trash=False):
    group = get_object_or_404(Group, name=group_name)
    papers = group.papers

    if user is not None:
        papers = papers.filter(creator=user)

    if id is not None:
        papers = papers.filter(pk=id)

    if trash:
        papers = papers.exclude(delete_time=None)
    else:
        papers = papers.filter(delete_time=None)

    if latest_month:
        today = datetime.today().astimezone(tz_beijing)
        year = today.year
        month = today.month
        papers = papers.filter(create_time__year=year, create_time__month=month)
    elif latest_week:
        last_week = datetime.now().astimezone(tz_beijing) - timedelta(days=7)
        papers = papers.filter(create_time__gte=last_week)

    papers = papers.order_by('-create_time', '-pk')
    total_count = papers.count()

    page_number = request.GET.get('page')
    if page_number is None:
        page_number = 1

    p = Paginator(papers, 20)
    try:
        papers = p.get_page(page_number)
    except PageNotAnInteger:
        page_number = 1
        papers = p.page(1)
    except EmptyPage:
        page_number = p.num_pages
        papers = p.page(p.num_pages)
    papers.page_range = p.get_elided_page_range(page_number, on_each_side=2)
    return papers, total_count

class IndexView(generic.ListView):
    template_name = 'group/index.html'
    context_object_name = 'group_list'
    def get_queryset(self):
        return Group.objects.order_by('-create_time')
    def get_context_data(self, **kwargs):
        context = {
            'current_page': 'index',
            'group_list': Group.objects.order_by('-create_time'),
            'summary_messages': '',
            }
        return context

def All(request, group_name):
    group = get_object_or_404(Group, name=group_name)
    paper_list, total_count = get_paper_list(request, group_name)
    template = loader.get_template('group/list.html')
    context = {
        'group': group,
        'current_page': 'all',
        'total_count': total_count,
        'paper_list': paper_list,
        'summary_messages': '',
    }
    return HttpResponse(template.render(context, request))

def Recent(request, group_name):
    group = get_object_or_404(Group, name=group_name)
    if group_name == "xiangma":
        paper_list, total_count = get_paper_list(request, group_name, latest_month=True)
        summary_message = '本页面显示本月的文献分享。'
    else:
        paper_list, total_count = get_paper_list(request, group_name, latest_week=True)
        summary_message = 'This page shows papers in last week. '
    template = loader.get_template('group/list.html')
    context = {
        'group': group,
        'current_page': 'recent',
        'total_count': total_count,
        'paper_list': paper_list,
        'summary_messages': summary_message
    }
    return HttpResponse(template.render(context, request))

def StatView(request, group_name):
    group = get_object_or_404(Group, name=group_name)
    papers = group.papers.filter(delete_time=None)

    stat_all = papers.values('creator__nickname', 'creator__pk').annotate(Count('creator')).order_by('-creator__count')

    today = datetime.today().astimezone(tz_beijing)
    year = today.year
    month = today.month
    stat_this_month = papers.filter(create_time__year=year, create_time__month=month).values('creator__nickname', 'creator__pk').annotate(Count('creator'), min_create_time=Min('create_time')).order_by('-creator__count', 'min_create_time')
    this_month = str(year) + '/' + str(month)

    if month > 1:
        month = month - 1
    else:
        year = year - 1
        month = 12
    stat_last_month = papers.filter(create_time__year=year, create_time__month=month).values('creator__nickname', 'creator__pk').annotate(Count('creator'), min_create_time=Min('create_time')).order_by('-creator__count', 'min_create_time')
    last_month = str(year) + '/' + str(month)

    stat_journal = papers.exclude(journal='').values('journal').annotate(Count('journal'), min_create_time=Min('create_time')).order_by('-journal__count', 'min_create_time')

    template = loader.get_template('group/stat.html')
    context = {
        'group': group,
        'current_page': 'stat',
        'stat_all': stat_all,
        'stat_this_month': stat_this_month,
        'this_month': this_month,
        'stat_last_month': stat_last_month,
        'last_month': last_month,
        'stat_journal': stat_journal,
    }
    return HttpResponse(template.render(context, request))

def Trash(request, group_name):
    group = get_object_or_404(Group, name=group_name)
    paper_list, total_count = get_paper_list(request, group_name, trash=True)
    summary_message = 'Papers in this folder will be removed after 30 days automatically.'
    return render(request, 'group/list.html', {
        'group': group,
        'current_page': 'trash',
        'total_count': total_count,
        'paper_list': paper_list,
        'summary_messages': summary_message
    })

def PaperAdd(request, group_name):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('group:all', kwargs={'group_name':group_name}))

    group = get_object_or_404(Group, name=group_name)
    if request.method == 'POST':
        form = PaperForm(request.POST)
        if not form.is_valid():
            return render(request, 'group/add.html', {
                'group': group,
                'current_page': 'add',
                'error_message': form.errors,
            })

        paper = Paper()
        paper.creator = AddUserIfNotExist(
            form.cleaned_data['creator_nickname'],
            form.cleaned_data['creator_name'],
            form.cleaned_data['creator_weixin_id'],
            form.cleaned_data['creator_username']
        )    
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

        paper.create_time = form.cleaned_data['create_time']
        paper.save()

        group.papers.add(paper)
        group.save()

        return HttpResponseRedirect(reverse('group:paper', kwargs={'group_name':group_name,'id':paper.id}))
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
            'group': group,
            'current_page': 'add',
            'form': form,
            'paper': paper,
        }
        template = loader.get_template('group/add.html')
        return HttpResponse(template.render(context, request))

def CollectionViewByID(request, id, group_name):
    group = get_object_or_404(Group, name=group_name)
    collections = Collection.objects.filter(pk=id)
    if collections.count() <= 0:
        return render(request, 'group/collection.html', {
            'error_message': 'Invalid collection ID: ' + str(id),
            'current_page': 'collection',
        })
    paper_list = collections[0].papers.order_by('-create_time', '-pk')
    template = loader.get_template('group/collection.html')
    if group_name == "xiangma":
        summary_message = '本页面显示合集 <b>#' + collections[0].name + '</b> 的文献。'
    else:
        summary_message = 'This page shows list <b>#' + str(id) + '</b>. '
    context = {
        'group': group,
        'current_page': 'collection',
        'collection': collections[0],
        'total_count': collections.count(),
        'paper_list': paper_list,
        'summary_messages': summary_message,
    }
    return HttpResponse(template.render(context, request))

def CollectionViewBySlug(request, slug, group_name):
    group = get_object_or_404(Group, name=group_name)
    paper_list, total_count = get_paper_list(request, group_name).order_by('-create_time', '-pk')
    template = loader.get_template('group/list.html')
    if group_name == "xiangma":
        summary_message = '本页面显示列表 <b>#' + str(id) + '</b> 的文献。'
    else:
        summary_message = 'This page shows list <b>#' + str(id) + '</b>. '
    context = {
        'group': group,
        'current_page': 'collection',
        'total_count': total_count,
        'paper_list': paper_list,
        'summary_messages': summary_message,
    }
    return HttpResponse(template.render(context, request))

def PaperLabelView(request, name, group_name):
    group = get_object_or_404(Group, name=group_name)
    paper_list = None
    label_list = Label.objects.filter(name=name)
    if label_list.count() > 0:
        paper_list = label_list[0].paper_set.all().order_by('-create_time', '-pk')
    template = loader.get_template('group/list.html')
    if group_name == "xiangma":
        summary_message = '本页面显示标签 <b>' + name + '</b> 的文献。'
    else:
        summary_message = 'This page shows list of label "<b>' + name + '</b>". '
    context = {
        'group': group,
        'current_page': 'label',
        'total_count': label_list.count(),
        'paper_list': paper_list,
        'summary_messages': summary_message,
    }
    return HttpResponse(template.render(context, request))

def SinglePaperView(request, id, group_name):
    group = get_object_or_404(Group, name=group_name)
    paper_list, total_count = get_paper_list(request, group_name, id=id)
    if total_count <= 0:
        return render(request, 'group/single.html', {
            'group': group,
            'current_page': 'paper',
            'error_message': 'Invalid paper ID: ' + str(id),
        })
    paper = paper_list[0]
    template = loader.get_template('group/single.html')
    context = {
        'group': group,
        'current_page': 'paper',
        'paper': paper,
    }
    return HttpResponse(template.render(context, request))

def RestorePaperView(request, id, group_name):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('group:all', kwargs={'group_name':group_name}))
    group = get_object_or_404(Group, name=group_name)
    paper_list, total_count = get_paper_list(request, group_name, include_trash=True).filter(pk=id)
    if paper_list.count() <= 0:
        return render(request, 'group/list.html', {
            'group': group,
            'current_page': 'edit',
            'error_message': 'Invalid paper ID: ' + str(id),
        })
    p = paper_list[0]
    p.delete_time = None
    p.save()
    return HttpResponseRedirect(reverse('group:paper', kwargs={'group_name':group_name,'id':id}))

def DeleteForeverPaperView(request, id, group_name):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('group:all', kwargs={'group_name':group_name}))
    group = get_object_or_404(Group, name=group_name)
    paper_list, total_count = get_paper_list(request, group_name, include_trash=True).filter(pk=id)
    if paper_list.count() <= 0:
        return render(request, 'group/list.html', {
            'group': group,
            'current_page': 'edit',
            'error_message': 'Invalid paper ID: ' + str(id),
        })
    get_paper_list(request, group_name, include_trash=True).filter(pk=id).delete()
    return HttpResponseRedirect(reverse('group:all', kwargs={'group_name':group_name}))

def DeletePaperView(request, id, group_name):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('group:all', kwargs={'group_name':group_name}))
    group = get_object_or_404(Group, name=group_name)
    paper_list, total_count = get_paper_list(request, group_name, include_trash=True).filter(pk=id)
    if paper_list.count() <= 0:
        return render(request, 'group/list.html', {
            'group': group,
            'current_page': 'edit',
            'error_message': 'Invalid paper ID: ' + str(id),
        })
    p = paper_list[0]
    if p.delete_time == None:
        p.delete_time = timezone.now()
        p.save()
    else:
        get_paper_list(request, group_name, include_trash=True).filter(pk=id).delete()
    return HttpResponseRedirect(reverse('group:all', kwargs={'group_name':group_name}))

def EditPaperView(request, id, group_name):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('group:all', kwargs={'group_name':group_name}))

    group = get_object_or_404(Group, name=group_name)
    paper_list = group.papers.filter(pk=id)
    if paper_list.count() <= 0:
        return render(request, 'group/edit.html', {
            'group': group,
            'current_page': 'edit',
            'error_message': 'Invalid paper ID: ' + str(id),
        })
    paper = paper_list[0]

    if request.method == 'POST':
        form = PaperForm(request.POST)
        if not form.is_valid():
            return render(request, 'group/edit.html', {
                'group': group,
                'current_page': 'edit',
                'error_message': form.errors,
            })

        u = AddUserIfNotExist(
            form.cleaned_data['creator_nickname'],
            form.cleaned_data['creator_name'],
            form.cleaned_data['creator_weixin_id'],
            form.cleaned_data['creator_username']
        )
        paper.creator = u
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
        return HttpResponseRedirect(reverse('group:paper', kwargs={'group_name':group_name,'id':id}))
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
        template = loader.get_template('group/edit.html')
        context = {
            'group': group,
            'current_page': 'edit',
            'paper': paper,
            'form': form,
        }
        return HttpResponse(template.render(context, request))

def UserView(request, id, group_name):
    user = get_object_or_404(User, pk=id)
    group = get_object_or_404(Group, name=group_name)
    paper_list, total_count = get_paper_list(request, group_name, user=user)
    template = loader.get_template('group/list.html')
    if group_name == "xiangma":
        summary_message = '本页面显示由用户 <b>' + user.nickname + '</b> 推荐的文献。'
    else:
        summary_message = 'This page shows papers recommended by <b>' + user.nickname + '</b>. '
    context = {
        'group': group,
        'current_page': 'user',
        'total_count': total_count,
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
