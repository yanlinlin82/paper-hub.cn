from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.urls import reverse

from .models import Paper

# Create your views here.
def index(request):
    paper_list = Paper.objects.order_by('-create_time')
    template = loader.get_template('index.html')
    context = {
        'paper_list': paper_list,
    }
    return HttpResponse(template.render(context, request))
