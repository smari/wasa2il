
from django.contrib import admin

from models import (
	Polity, Topic, Issue,
	VoteOption, Comment, Vote,
	Delegate, MembershipRequest,
	MembershipVote, UserProfile
	)


def getDerivedAdmin(base_admin, **kwargs):
	class DerivedAdmin(base_admin):
		pass
	derived = DerivedAdmin
	for k,v in kwargs.iteritems():
		setattr(derived, k, getattr(base_admin, k, []) + v)
	return derived


def save_model(self, request, obj, form, change):
	if getattr(obj, 'created_by', None) is None:
		obj.created_by = request.user
	obj.modified_by = request.user
	obj.save()


class NameSlugAdmin(admin.ModelAdmin):
	fieldsets = [
		(None, { 'fields': ['name', 'slug'] }),
	]
	prepopulated_fields = { 'slug': ['name'] }
	list_display = ['name', 'get_url']
	search_fields = ['name']


BaseIssueAdmin = getDerivedAdmin(NameSlugAdmin,
		list_display=['description'],
		search_fields=['description'],
	)
BaseIssueAdmin.fieldsets = [
		NameSlugAdmin.fieldsets[0],
		(None, { 'fields': ['description'] }),
	]
BaseIssueAdmin.save_model = save_model

class PolityAdmin(BaseIssueAdmin):
	fieldsets = None
	list_display = BaseIssueAdmin.list_display + ['parent']


class TopicAdmin(BaseIssueAdmin):
	fieldsets = None
	list_display = BaseIssueAdmin.list_display + ['polity']


class IssueAdmin(BaseIssueAdmin):
	fieldsets = None
	list_display = BaseIssueAdmin.list_display + ['topics_str']


class DelegateAdmin(admin.ModelAdmin):
	list_display = ['user', 'delegate', 'base_issue']


class VoteOptionAdmin(NameSlugAdmin):
	pass

class VoteAdmin(admin.ModelAdmin):
	list_display = ['user', 'option']

class CommentAdmin(admin.ModelAdmin):
	save_model = save_model

# Register the admins
register = admin.site.register
register(Polity, PolityAdmin)
register(Topic, TopicAdmin)
register(Issue, IssueAdmin)
register(VoteOption, VoteOptionAdmin)
register(Comment, CommentAdmin)
register(Delegate, DelegateAdmin)
register(Vote, VoteAdmin)
register(MembershipRequest)
register(MembershipVote)
register(UserProfile)
