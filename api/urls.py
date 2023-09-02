from django.urls import re_path

from . import views

app_name = 'api'
urlpatterns = [
    re_path(r'^query/user/(?P<user>.+)', views.QueryUser, name='query_user'),
    re_path(r'^query/paper/(?P<id>.+)', views.QueryPaper, name='query_paper'),
]
