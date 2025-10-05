from django.urls import path, re_path

from . import views

app_name = 'api'
urlpatterns = [
    # web login/logout
    path('login', views.do_login, name='login'),
    path('logout', views.do_logout, name='logout'),
    path('get-weixin-qr/', views.get_weixin_qr, name='get_weixin_qr'),
    path('weixin-callback/', views.weixin_callback, name='weixin_callback'),

    # for weixin mini program
    path('wx-login', views.wx_login, name='wx_login'),
    path('update-nickname', views.update_nickname, name='update_nickname'),

    # for title/abstract translation on web
    path('translate-title', views.translate_title, name='translate_title'),
    path('translate-abstract', views.translate_abstract, name='translate_abstract'),

    # new api (request from web '/group/...')
    path('check-in', views.check_in, name='check_in'),
    path('check-in-by-admin', views.check_in_by_admin, name='check_in_by_admin'),
    path('create-user', views.create_user, name='create_user'),
    path('new-remove-paper', views.new_remove_paper, name='new_remove_paper'),
    path('new-restore-paper', views.new_restore_paper, name='new_restore_paper'),
    path('new-remove-paper-permanently', views.new_remove_paper_permanently, name='new_remove_paper_permanently'),
    path('new-edit-review', views.new_edit_review, name='new_edit_review'),
    path('new-remove-review', views.new_remove_review, name='new_remove_review'),
    path('new-restore-review', views.new_restore_review, name='new_restore_review'),
    path('new-remove-review-permanently', views.new_remove_review_permanently, name='new_remove_review_permanently'),

    # new api (request from web '/view/...')
    path('add-search-result', views.add_search_result, name='add_search_result'),
    path('add-recommendation', views.add_recommendation, name='add_recommendation'),
    path('mark-read-recommendation', views.mark_read_recommendation, name='mark_read_recommendation'),
    path('restore-recommendation', views.restore_recommendation, name='restore_recommendation'),

    # fetch data for weixin mini program
    path('query/user/<str:user>', views.query_user, name='query_user'),
    re_path(r'^query/review/(?P<id>.+)', views.query_review, name='query_review'),
    path('submit-review', views.submit_review, name='submit_review'),
    path('add-review', views.add_review, name='add_review'),
    path('edit-review', views.edit_review, name='edit_review'),
    path('delete-review', views.delete_review, name='delete_review'),
    path('restore-review', views.restore_review, name='restore_review'),
    path('delete-review-forever', views.delete_review_forever, name='delete_review_forever'),

    path('fetch-rank-list', views.fetch_rank_list, name='fetch_rank_list'),
    path('fetch-rank-full-list', views.fetch_rank_full_list, name='fetch_rank_full_list'),
    path('fetch-review-list', views.fetch_review_list, name='fetch_review_list'),
    path('fetch-review-info', views.fetch_review_info, name='fetch_review_info'),

    path('submit-comment', views.submit_comment, name='submit_comment'),
    path('summarize-by-gpt', views.summarize_by_gpt, name='summarize_by_gpt'),
    path('query-paper-info', views.query_paper_info, name='query_paper_info'),

    path('username-autocomplete', views.username_autocomplete, name='username_autocomplete'),
]
