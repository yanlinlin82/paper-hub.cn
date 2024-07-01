from django.urls import path, re_path
from . import views

app_name = 'group'
urlpatterns = [
    path('', views.index_page, name='index'),
    path('<str:group_name>/', views.all_page, name='all'),
    path('<str:group_name>/my_sharing', views.my_sharing_page, name='my_sharing'),
    path('<str:group_name>/recent', views.recent_page, name='recent'),
    path('<str:group_name>/this_month', views.this_month_page, name='this_month'),
    path('<str:group_name>/last_month', views.last_month_page, name='last_month'),
    path('<str:group_name>/trash', views.trash_page, name='trash'),
    path('<str:group_name>/review/<int:id>', views.single_page, name='review'),
    path('<str:group_name>/user/<int:id>', views.user_page, name='user'),
    re_path(r'^(?P<group_name>[^/]+)/journal/(?P<journal_name>.+)', views.journal_page, name='journal'),
    path('<str:group_name>/stat', views.stat_page, name='stat'),
    path('<str:group_name>/stat/this_month', views.stat_this_month_page, name='stat_this_month'),
    path('<str:group_name>/stat/last_month', views.stat_last_month_page, name='stat_last_month'),
    path('<str:group_name>/stat/all', views.stat_all_page, name='stat_all'),
    path('<str:group_name>/stat/journal', views.stat_journal_page, name='stat_journal'),
]
