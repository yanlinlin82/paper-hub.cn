from django.urls import path, re_path, include

from . import views

app_name = 'view'
urlpatterns = [
    path('', views.RecentPapersView, name='index'),
    path('recent', views.RecentPapersView, name='recent'),
    path('all', views.AllPapersView, name='all'),
    path('favor', views.FavorPapersView, name='favor'),
    path('list/<int:id>', views.PaperListView, name='list'),
    path('label/<str:name>', views.PaperLabelView, name='label'),
    path('paper/<int:id>/edit', views.EditPaperView, name='edit'),
    path('paper/<int:id>/delete', views.DeletePaperView, name='delete'),
    path('paper/<int:id>', views.SinglePaperView, name='paper'),
    path('user/<int:id>', views.UserView, name='user'),
    path('stat', views.StatView, name='stat'),
    path('add', views.PaperAdd, name='add'),
    path('login', views.Login, name='login'),
    path('logout', views.Logout, name='logout'),
    re_path(r'^ajax/fetch/doi/(?P<doi>.+)', views.AjaxFetchDOI, name='ajax-fetch-doi'),
    re_path(r'^ajax/fetch-raw/doi/(?P<doi>.+)', views.AjaxFetchRawDOI, name='ajax-fetch-doi'),
]
