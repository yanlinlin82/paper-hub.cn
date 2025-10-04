"""paperhub URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse
from config import settings

def baidu_verify_codeva(request):
    filename = os.path.join(settings.BASE_DIR, 'static', 'baidu_verify_codeva-NJa4iPMlSa.html')
    with open(filename, 'r') as f:
        return HttpResponse(f.read())

urlpatterns = [
    path('baidu_verify_codeva-NJa4iPMlSa.html', baidu_verify_codeva), # for baidu search engine verification
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('group/', include('group.urls')),
    path('library/', include('library.urls')),
    path('', include('view.urls')), # for global function pages, such as search, recommendations, trackings
]
