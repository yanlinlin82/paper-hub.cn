from django.urls import path

from . import views

#app_name = 'view'
urlpatterns = [
    path('', views.index, name='index'),
    path('paper/<int:id>', views.paper, name='paper'),
    path('label/<str:text>', views.label, name='label'),
    path('user/<int:id>', views.user, name='user'),
    path('add', views.add, name='add'),
    path('post/ajax/paper', views.postPaper, name = 'post_paper'),
]
