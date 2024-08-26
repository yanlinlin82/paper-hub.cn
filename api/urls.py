from django.urls import path, re_path

from . import views

app_name = 'api'
urlpatterns = [
    # web login/logout
    path('login', views.do_login, name='login'),
    path('logout', views.do_logout, name='logout'),
    path('get-weixin-qr/', views.get_weixin_qr, name='get_weixin_qr'),
    path('weixin_callback/', views.weixin_callback, name='weixin_callback'),

    # for weixin mini program
    path('wx_login', views.wx_login, name='wx_login'),
    path('update_nickname', views.update_nickname, name='update_nickname'),

    # for title/abstract translation on web
    path('translate_title', views.translate_title, name='translate_title'),
    path('translate_abstract', views.translate_abstract, name='translate_abstract'),

    # new api (request from web '/group/...')
    path('check_in', views.check_in, name='check_in'),
    path('check_in_by_admin', views.check_in_by_admin, name='check_in_by_admin'),
    path('new_remove_paper', views.new_remove_paper, name='new_remove_paper'),
    path('new_restore_paper', views.new_restore_paper, name='new_restore_paper'),
    path('new_remove_paper_permanently', views.new_remove_paper_permanently, name='new_remove_paper_permanently'),
    path('new_edit_review', views.new_edit_review, name='new_edit_review'),
    path('new_remove_review', views.new_remove_review, name='new_remove_review'),
    path('new_restore_review', views.new_restore_review, name='new_restore_review'),
    path('new_remove_review_permanently', views.new_remove_review_permanently, name='new_remove_review_permanently'),

    # new api (request from web '/view/...')
    path('add_search_result', views.add_search_result, name='add_search_result'),
    path('add_recommendation', views.add_recommendation, name='add_recommendation'),
    path('mark_read_recommendation', views.mark_read_recommendation, name='mark_read_recommendation'),
    path('restore_recommendation', views.restore_recommendation, name='restore_recommendation'),

    # fetch data for weixin mini program
    path('query/user/<str:user>', views.query_user, name='query_user'),
    re_path(r'^query/review/(?P<id>.+)', views.query_review, name='query_review'),
    path('submit_review', views.submit_review, name='submit_review'),
    path('add_review', views.add_review, name='add_review'),
    path('edit_review', views.edit_review, name='edit_review'),
    path('delete_review', views.delete_review, name='delete_review'),
    path('restore_review', views.restore_review, name='restore_review'),
    path('delete_review_forever', views.delete_review_forever, name='delete_review_forever'),

    path('fetch_rank_list', views.fetch_rank_list, name='fetch_rank_list'),
    path('fetch_rank_full_list', views.fetch_rank_full_list, name='fetch_rank_full_list'),
    path('fetch_review_list', views.fetch_review_list, name='fetch_review_list'),
    path('fetch_review_info', views.fetch_review_info, name='fetch_review_info'),

    path('submit_comment', views.submit_comment, name='submit_comment'),
    path('summarize_by_gpt', views.summarize_by_gpt, name='summarize_by_gpt'),
    path('query_paper_info', views.query_paper_info, name='query_paper_info'),

    path('username_autocomplete', views.username_autocomplete, name='username_autocomplete'),
]
