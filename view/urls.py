import re
from django.urls import path, re_path
from django.http import HttpResponseRedirect

from . import views

def redirect(request):
    return HttpResponseRedirect('all')

app_name = 'view'
urlpatterns = [
    path('', redirect, name='index'),
    path('all', views.All, name='all'),
    path('recent', views.Recent, name='recent'),
    path('favor', views.Favor, name='favor'),
    path('trash', views.Trash, name='trash'),
    path('trash/<int:id>/restore', views.RestorePaperView, name='restore_from_trash'),
    path('trash/<int:id>/delete', views.DeleteForeverPaperView, name='delete_forever'),
    path('collection/<int:id>', views.CollectionViewByID, name='collection'),
    path('collection/<str:slug>', views.CollectionViewBySlug, name='collection'),
    path('label/<str:name>', views.PaperLabelView, name='label'),
    path('paper/<int:id>/edit', views.EditPaperView, name='edit'),
    path('paper/<int:id>/delete', views.DeletePaperView, name='delete'),
    path('paper/<int:id>', views.SinglePaperView, name='paper'),
    path('user/<int:id>', views.UserView, name='user'),
    path('add', views.PaperAdd, name='add'),
    path('login', views.Login, name='login'),
    path('logout', views.Logout, name='logout'),
    re_path(r'^ajax/query/user/(?P<user>.+)', views.AjaxFetchUser, name='ajax_query_user'),
    re_path(r'^ajax/fetch/paper/(?P<id>.+)', views.AjaxFetchPaper, name='ajax_fetch_paper'),
]
