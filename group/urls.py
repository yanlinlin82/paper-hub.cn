from django.urls import path
from django.http import HttpResponse

from . import views

app_name = 'group'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<str:group_name>/', views.All, name='all'),
    path('<str:group_name>/recent', views.Recent, name='recent'),
    path('<str:group_name>/favor', views.Favor, name='favor'),
    path('<str:group_name>/trash', views.Trash, name='trash'),
    path('<str:group_name>/trash/<int:id>/restore', views.RestorePaperView, name='restore_from_trash'),
    path('<str:group_name>/trash/<int:id>/delete', views.DeleteForeverPaperView, name='delete_forever'),
    path('<str:group_name>/collection/<int:id>', views.CollectionViewByID, name='collection'),
    path('<str:group_name>/collection/<str:slug>', views.CollectionViewBySlug, name='collection'),
    path('<str:group_name>/label/<str:name>', views.PaperLabelView, name='label'),
    path('<str:group_name>/paper/<int:id>/edit', views.EditPaperView, name='edit'),
    path('<str:group_name>/paper/<int:id>/delete', views.DeletePaperView, name='delete'),
    path('<str:group_name>/paper/<int:id>', views.SinglePaperView, name='paper'),
    path('<str:group_name>/user/<int:id>', views.UserView, name='user'),
    path('<str:group_name>/stat', views.StatView, name='stat'),
    path('<str:group_name>/add', views.PaperAdd, name='add'),
]
