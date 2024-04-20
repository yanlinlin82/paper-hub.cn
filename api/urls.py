from django.urls import path, re_path

from . import views

app_name = 'api'
urlpatterns = [
    path('login', views.do_login, name='login'),
    path('logout', views.do_logout, name='logout'),
    path('query/user/<str:user>', views.query_user, name='query_user'),
    re_path(r'^query/paper/(?P<id>.+)', views.query_paper, name='query_paper'),
    path('add_paper', views.add_paper, name='add_paper'),
    path('edit_paper', views.edit_paper, name='edit_paper'),
    path('delete_paper', views.delete_paper, name='delete_paper'),
    path('restore_paper', views.restore_paper, name='restore_paper'),
    path('delete_paper_forever', views.delete_paper_forever, name='delete_paper_forever'),
    path('wx_login', views.wx_login, name='wx_login'),
    path('update_nickname', views.update_nickname, name='update_nickname'),
    path('fetch_rank_list', views.fetch_rank_list, name='fetch_rank_list'),
    path('fetch_rank_full_list', views.fetch_rank_full_list, name='fetch_rank_full_list'),
    path('fetch_paper_list', views.fetch_paper_list, name='fetch_paper_list'),
    path('fetch_paper_info', views.fetch_paper_info, name='fetch_paper_info'),
    path('submit_comment', views.submit_comment, name='submit_comment'),
    path('summarize_by_gpt', views.summarize_by_gpt, name='summarize_by_gpt'),
    path('get-weixin-qr/', views.get_weixin_qr, name='get_weixin_qr'),
    path('weixin_callback/', views.weixin_callback, name='weixin_callback'),
]
