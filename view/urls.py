from django.urls import path

from . import views

app_name = 'view'
urlpatterns = [
    path('', views.RecentPapersView, name='index'),
    path('recent', views.RecentPapersView, name='recent'),
    path('all', views.AllPapersView, name='all'),
    path('list/<int:id>', views.PaperListView, name='list'),
    path('label/<str:name>', views.PaperLabelView, name='label'),
    path('paper/<int:id>/edit', views.EditPaperView, name='edit'),
    path('paper/<int:id>', views.SinglePaperView, name='paper'),
    path('user/<int:id>', views.UserView, name='user'),
    path('stat', views.StatView, name='stat'),
    path('add', views.PaperAdd, name='add'),
    path('post/ajax/paper', views.PaperPostAjax, name = 'ajax'),
]
