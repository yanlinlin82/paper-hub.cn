from django.urls import path, re_path
from django.http import HttpResponseRedirect
from . import views

def redirect(request):
    # 重定向到前端应用
    return HttpResponseRedirect('http://localhost:5173')

urlpatterns = [
    path('', redirect, name='index'),
    path('api/data', views.api_data, name='api_data'),
    
    # 保留一些传统的Django页面（如果需要的话）
    path('search', views.search_page, name='search'),
    path('paper/<int:id>', views.single_page, name='paper'),
    path('recommendations', views.recommendations_page, name='recommendations'),
    path('trackings', views.trackings_page, name='trackings'),
    
    # 捕获所有其他路由，重定向到前端应用
    re_path(r'^.*$', views.redirect_to_frontend, name='redirect_to_frontend'),
]
