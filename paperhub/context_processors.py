from django.conf import settings

def my_configures(request):
    return {
        'TIME_ZONE': settings.TIME_ZONE,
        'CONFIG_XIANGMA_GROUP_ONLY': settings.CONFIG_XIANGMA_GROUP_ONLY,
        'group_name': 'xiangma',
    }
