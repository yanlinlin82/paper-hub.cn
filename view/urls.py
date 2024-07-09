from django.urls import path
from django.http import HttpResponseRedirect
from paperhub import settings

from . import views

def redirect(request):
    return HttpResponseRedirect('group/xiangma')

urlpatterns = [
    path('', redirect, name='index'),
    path('search', views.search_page, name='search'),
    path('recommendations', views.recommendations_page, name='recommendations'),
    path('trackings', views.trackings_page, name='trackings'),
]
