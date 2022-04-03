import re
from django.urls import path, re_path
from django.http import HttpResponseRedirect

from . import views

def is_xiangma(request):
    return re.match("^/xiangma/", request.path)

def redirect(request):
    if is_xiangma(request):
        return HttpResponseRedirect('recent')
    else:
        return HttpResponseRedirect('all')

app_name = 'view'
urlpatterns = [
    path('', redirect, name='index'),
    path('all', views.All, name='all'),
    path('recent', views.Recent, name='recent'),
    path('favor', views.Favor, name='favor'),
    path('trash', views.Trash, name='trash'),
    path('trash/<int:id>/delete', views.DeletePaperView, name='delete-forever'),
    path('collection/<int:id>', views.CollectionViewByID, name='collection'),
    path('collection/<str:slug>', views.CollectionViewBySlug, name='collection'),
    path('label/<str:name>', views.PaperLabelView, name='label'),
    path('paper/<int:id>/edit', views.EditPaperView, name='edit'),
    path('paper/<int:id>/delete', views.DeletePaperView, name='delete'),
    path('paper/<int:id>', views.SinglePaperView, name='paper'),
    path('user/<int:id>', views.UserView, name='user'),
    path('stat', views.StatView, name='stat'),
    path('add', views.PaperAdd, name='add'),
    path('login', views.Login, name='login'),
    path('logout', views.Logout, name='logout'),
    re_path(r'^ajax/fetch/doi/(?P<doi>.+)', views.AjaxFetchDOI, name='ajax-fetch-doi'),
    re_path(r'^ajax/fetch-raw/doi/(?P<doi>.+)', views.AjaxFetchRawDOI, name='ajax-fetch-doi'),
]
