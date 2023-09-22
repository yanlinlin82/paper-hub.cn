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
    path('favor', views.Favor, name='favor'),
    path('trash', views.Trash, name='trash'),
    path('trash/<int:id>/restore', views.RestorePaperView, name='restore_from_trash'),
    path('trash/<int:id>/delete', views.DeleteForeverPaperView, name='delete_forever'),
    path('paper/<int:id>/delete', views.DeletePaperView, name='delete'),
    path('paper/<int:id>', views.SinglePaperView, name='paper'),
    path('user/<int:id>', views.UserView, name='user'),
]
