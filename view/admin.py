from django.contrib import admin

# Register your models here.
from .models import UserProfile, UserAlias, UserSession, Paper, GroupProfile, CustomCheckInInterval

class UserAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'auth_user':
            kwargs['required'] = False
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'last_login_time':
            kwargs['required'] = False
        return super().formfield_for_dbfield(db_field, **kwargs)

admin.site.register(UserProfile, UserAdmin)
admin.site.register(UserAlias)
admin.site.register(UserSession)
admin.site.register(Paper)
admin.site.register(GroupProfile)
admin.site.register(CustomCheckInInterval)
