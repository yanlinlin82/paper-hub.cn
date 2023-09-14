from django.contrib import admin

# Register your models here.
from .models import Group, CustomCheckInInterval

admin.site.register(Group)
admin.site.register(CustomCheckInInterval)
