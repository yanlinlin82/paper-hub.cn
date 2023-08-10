from django.urls import path
from django.http import HttpResponse

def user_list(request):
    return HttpResponse('user')

def user_view(request, user_name):
    return HttpResponse('user ' + user_name)

app_name = 'user'
urlpatterns = [
    path('', user_list, name='index'),
    path('<str:user_name>/', user_view, name='view')
]
