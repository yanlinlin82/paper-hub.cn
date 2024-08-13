from django.urls import path
from django.http import HttpResponseRedirect
from mysite import settings

from . import views

app_name = 'library'
urlpatterns = [
    path('', views.all_page, name='index'),
    path('recent', views.recent_page, name='recent'),
    path('trash', views.trash_page, name='trash'),
    path('paper/<int:id>', views.single_page, name='paper'),
    path('labels', views.labels_page, name='labels'),
]
