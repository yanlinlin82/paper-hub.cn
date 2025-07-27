from django.urls import path
from django.http import HttpResponseRedirect
from . import views

def redirect(request):
    return HttpResponseRedirect('xiangma')

app_name = 'group'
urlpatterns = [
    path('', redirect, name='index'),
    path('<str:group_name>/', views.index_page, name='index'),
    path('<str:group_name>/all', views.all_page, name='all'),
    path('<str:group_name>/my_sharing', views.my_sharing_page, name='my_sharing'),
    path('<str:group_name>/recent', views.recent_page, name='recent'),
    path('<str:group_name>/this_month', views.this_month_page, name='this_month'),
    path('<str:group_name>/last_month', views.last_month_page, name='last_month'),
    path('<str:group_name>/trash', views.trash_page, name='trash'),
    path('<str:group_name>/review/<int:id>', views.single_page, name='review'),
    path('<str:group_name>/user/<int:id>', views.user_page, name='user'),
    path('<str:group_name>/journal/<str:journal_name>', views.journal_page, name='journal'),
    path('<str:group_name>/rank', views.rank_page, name='rank'),
    path('<str:group_name>/rank/<str:rank_type>', views.rank_type_page, name='rank_type'),
]
