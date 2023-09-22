from django.urls import path
from django.http import HttpResponseRedirect

from . import views

def redirect(request):
    return HttpResponseRedirect('all')

app_name = 'view'
urlpatterns = [
    path('', redirect, name='index'),
    path('all', views.All, name='all'),
    path('recent', views.Recent, name='recent'),
    path('trash', views.Trash, name='trash'),
    path('paper/<int:id>', views.SinglePaperView, name='paper'),
]
