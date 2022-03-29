from django.urls import path

from . import views

app_name = 'view'
urlpatterns = [
    path('', views.RecentPapersView, name='index', kwargs={ 'current_page': 'recent' }),
    path('recent', views.RecentPapersView, name='recent', kwargs={ 'current_page': 'recent' }),
    path('all', views.AllPapersView, name='all', kwargs={ 'current_page': 'all' }),
    path('list/<int:id>', views.PaperListView, name='list', kwargs={ 'current_page': 'list' }),
    path('label/<str:name>', views.PaperLabelView, name='label', kwargs={ 'current_page': 'label' }),
    path('paper/<int:id>/edit', views.EditPaperView, name='edit', kwargs={ 'current_page': 'edit' }),
    path('paper/<int:id>', views.SinglePaperView, name='paper', kwargs={ 'current_page': 'paper' }),
    path('user/<int:id>', views.UserView, name='user', kwargs={ 'current_page': 'user' }),
    path('stat', views.StatView, name='stat', kwargs={ 'current_page': 'stat' }),
    path('add', views.PaperAdd, name='add', kwargs={ 'current_page': 'add' }),
    path('post/ajax/paper', views.PaperPostAjax, name = 'ajax'),
]
