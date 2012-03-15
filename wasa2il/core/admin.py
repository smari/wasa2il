
from django.contrib import admin

from models import Polity, Topic, Issue

def save_model(self, request, obj, form, change):
	if getattr(obj, 'created_by', None) is None:
		obj.created_by = request.user
	obj.modified_by = request.user
	obj.save()

class BaseIssueAdmin(admin.ModelAdmin):
	list_display = ['name', 'description']
	search_fields = ['name', 'description']
	prepopulated_fields = { 'slug': ['name'] }

class PolityAdmin(BaseIssueAdmin):
	list_display = BaseIssueAdmin.list_display + ['parent']

class TopicAdmin(BaseIssueAdmin):
	list_display = BaseIssueAdmin.list_display + ['polity']

class IssueAdmin(BaseIssueAdmin):
	list_display = BaseIssueAdmin.list_display + ['topics_str']

class Delegate(admin.ModelAdmin):
	list_display = ['user', 'delegate', 'base_issue']

register = admin.site.register

register(Polity, PolityAdmin)
register(Topic, TopicAdmin)
register(Issue, IssueAdmin)
