from django.contrib import admin

from .models import User, Permission

admin.site.register(User)
admin.site.register(Permission)