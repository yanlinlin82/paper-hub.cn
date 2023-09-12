from django.urls import path, re_path

from . import views

app_name = 'api'
urlpatterns = [
    path('login', views.Login, name='login'),
    path('logout', views.Logout, name='logout'),
    path('query/user/<str:user>', views.QueryUser, name='query_user'),
    re_path(r'^query/paper/(?P<id>.+)', views.QueryPaper, name='query_paper'),
    path('delete_paper', views.DeletePaper, name='delete_paper'),
    path('restore_paper', views.RestorePaper, name='restore_paper'),
    path('delete_paper_forever', views.DeletePaperForever, name='delete_paper_forever'),
]
