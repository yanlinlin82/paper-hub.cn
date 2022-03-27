from django.urls import path

from . import views

app_name = 'xiangma'
urlpatterns = [
    path('', views.xiangma_RecentPapersView, name='index', kwargs={ 'current_page': 'recent' }),
    path('recent', views.xiangma_RecentPapersView, name='recent', kwargs={ 'current_page': 'recent' }),
    path('all', views.xiangma_AllPapersView, name='all', kwargs={ 'current_page': 'all' }),
    path('list/<int:id>', views.xiangma_PaperListView, name='list', kwargs={ 'current_page': 'list' }),
    path('label/<str:name>', views.xiangma_PaperLabelView, name='label', kwargs={ 'current_page': 'label' }),
    path('paper/<int:id>', views.xiangma_SinglePaperView, name='paper', kwargs={ 'current_page': 'paper' }),
    path('user/<int:id>', views.xiangma_UserView, name='user', kwargs={ 'current_page': 'user' }),
    path('stat', views.xiangma_StatView, name='stat', kwargs={ 'current_page': 'stat' }),
]
