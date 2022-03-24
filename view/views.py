from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from django.db.models import Q

from .models import Label, Paper, User

# Create your views here.
def index(request):
    paper_list = Paper.objects.order_by('-create_time')
    template = loader.get_template('list.html')
    context = {
        'paper_list': paper_list,
    }
    return HttpResponse(template.render(context, request))

def paper(request, id):
    paper = Paper.objects.filter(pk=id)
    template = loader.get_template('single.html')
    context = {
        'paper': paper[0],
    }
    return HttpResponse(template.render(context, request))

def label(request, text):
    paper_list = None
    xiangma = Label.objects.filter(name=text)
    if xiangma.count() > 0:
        paper_list = xiangma[0].paper_set.all().order_by('-create_time')
    template = loader.get_template('index.html')
    context = {
        'paper_list': paper_list,
    }
    return HttpResponse(template.render(context, request))

def user(request, id):
    u = User.objects.filter(pk=id)
    if u.count() <= 0:
        return render(request, 'list.html', {
            'error_message': "Invalid user id!",
        })
    paper_list = Paper.objects.filter(creator=u[0].nickname)
    template = loader.get_template('list.html')
    context = {
        'paper_list': paper_list,
    }
    return HttpResponse(template.render(context, request))
