from django.urls import path
from django.http import HttpResponseRedirect

from . import views

def redirect(request):
    return HttpResponseRedirect('all')

app_name = 'view'
urlpatterns = [
    path('', redirect, name='index'),
    path('all', views.all_page, name='all'),
    path('recent', views.recent_page, name='recent'),
    path('trash', views.trash_page, name='trash'),
    path('paper/<int:id>', views.single_page, name='paper'),
]
