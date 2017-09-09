from django.contrib import admin

from models import Topic

class TopicAdmin(admin.ModelAdmin):
    fieldsets = None
    list_display = ['name', 'slug', 'description', 'polity']


register = admin.site.register
register(Topic)
