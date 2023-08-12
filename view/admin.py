from django.contrib import admin

# Register your models here.
from .models import User, Label, Paper, CrossRefCache, Collection

admin.site.register(User)
admin.site.register(Label)
admin.site.register(Paper)
admin.site.register(CrossRefCache)
admin.site.register(Collection)
