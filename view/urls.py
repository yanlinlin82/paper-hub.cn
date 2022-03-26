from django.urls import path

from . import views

app_name = 'view'
urlpatterns = [
    path('', views.IndexView, name='index'),
    path('all', views.AllPapersView, name='all'),
    path('recent', views.RecentPapersView, name='recent'),
    path('list/<int:id>', views.PaperListView, name='list'),
    path('label/<str:name>', views.PaperLabelView, name='label'),
    path('paper/<int:id>', views.SinglePaperView, name='paper'),
    path('user/<int:id>', views.UserView, name='user'),
    path('add', views.PaperAdd, name='add'),
    path('post/ajax/paper', views.PaperPostAjax, name = 'ajax'),
]
