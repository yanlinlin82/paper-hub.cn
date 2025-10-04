from django.conf import settings

def my_configures(request):
    return {
        'TIME_ZONE': settings.TIME_ZONE,
        'group_name': 'xiangma',
    }
