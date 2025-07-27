from django.urls import path
from django.http import HttpResponseRedirect
from . import views

def redirect(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('group/xiangma')
    return HttpResponseRedirect('search')

urlpatterns = [
    path('', redirect, name='index'),
    path('search', views.search_page, name='search'),
    path('paper/<int:id>', views.single_page, name='paper'),
    path('recommendations', views.recommendations_page, name='recommendations'),
    path('trackings', views.trackings_page, name='trackings'),
]
