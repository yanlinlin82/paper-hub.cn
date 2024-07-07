from django.urls import path, re_path

from . import views

app_name = 'api'
urlpatterns = [
    path('login', views.do_login, name='login'),
    path('logout', views.do_logout, name='logout'),
    path('query/user/<str:user>', views.query_user, name='query_user'),
    re_path(r'^query/review/(?P<id>.+)', views.query_review, name='query_review'),
    path('add_review', views.add_review, name='add_review'),
    path('edit_review', views.edit_review, name='edit_review'),
    path('delete_review', views.delete_review, name='delete_review'),
    path('restore_review', views.restore_review, name='restore_review'),
    path('delete_review_forever', views.delete_review_forever, name='delete_review_forever'),
    path('add_search_result', views.add_search_result, name='add_search_result'),
    path('add_recommendation', views.add_recommendation, name='add_recommendation'),
    path('delete_recommendation', views.delete_recommendation, name='delete_recommendation'),
    path('restore_recommendation', views.restore_recommendation, name='restore_recommendation'),
    path('wx_login', views.wx_login, name='wx_login'),
    path('update_nickname', views.update_nickname, name='update_nickname'),
    path('fetch_rank_list', views.fetch_rank_list, name='fetch_rank_list'),
    path('fetch_rank_full_list', views.fetch_rank_full_list, name='fetch_rank_full_list'),
    path('fetch_review_list', views.fetch_review_list, name='fetch_review_list'),
    path('fetch_review_info', views.fetch_review_info, name='fetch_review_info'),
    path('submit_comment', views.submit_comment, name='submit_comment'),
    path('summarize_by_gpt', views.summarize_by_gpt, name='summarize_by_gpt'),
    path('get-weixin-qr/', views.get_weixin_qr, name='get_weixin_qr'),
    path('weixin_callback/', views.weixin_callback, name='weixin_callback'),
    path('translate_title', views.translate_title, name='translate_title'),
    path('translate_abstract', views.translate_abstract, name='translate_abstract'),
]
