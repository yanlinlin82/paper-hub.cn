from django.conf import settings

def my_configures(request):
    return {'CONFIG_XIANGMA_GROUP_ONLY': settings.CONFIG_XIANGMA_GROUP_ONLY}
