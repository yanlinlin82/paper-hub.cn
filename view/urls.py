from django.urls import path
from django.http import HttpResponseRedirect
from paperhub import settings

from . import views

def redirect(request):
    return HttpResponseRedirect('search')

urlpatterns = [
    path('', redirect, name='index'),
    path('search', views.search_page, name='search'),
    path('recommendations', views.recommendations_page, name='recommendations'),
    path('recommendations-trash', views.recommendations_trash_page, name='recommendations-trash'),
    path('trackings', views.trackings_page, name='trackings'),
    path('all', views.all_page, name='all'),
    path('recent', views.recent_page, name='recent'),
    path('labels', views.labels_page, name='labels'),
    path('trash', views.trash_page, name='trash'),
    path('paper/<int:id>', views.single_page, name='paper'),
]
