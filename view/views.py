from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from django.db.models import Q

from .models import Label, Paper

# Create your views here.
def index(request):
    paper_list = None
    xiangma = Label.objects.filter(name="xiangma")
    if xiangma.count() > 0:
        paper_list = xiangma[0].paper_set.all()
    #paper_list = Paper.objects.filter(Q(labels="xiangma")).order_by('-create_time')
    #paper_list = Paper.objects.order_by('-create_time')
    template = loader.get_template('index.html')
    context = {
        'paper_list': paper_list,
    }
    return HttpResponse(template.render(context, request))
