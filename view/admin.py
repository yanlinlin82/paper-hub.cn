from django.contrib import admin

# Register your models here.
from .models import User, Label, Paper, Collection

admin.site.register(User)
admin.site.register(Label)
admin.site.register(Paper)
admin.site.register(Collection)
