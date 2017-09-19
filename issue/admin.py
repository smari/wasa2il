from django.contrib import admin

from issue.models import Comment
from issue.models import DocumentContent
from issue.models import Issue


class IssueAdmin(admin.ModelAdmin):
    fieldsets = None
    list_display = ['name', 'slug', 'description', 'topics_str']
    exclude = ['votecount', 'votecount_yes', 'votecount_abstain', 'votecount_no']


class DocumentContentAdmin(admin.ModelAdmin):
    list_display = ['document', 'order', 'comments', 'user', 'created']


register = admin.site.register
register(Issue, IssueAdmin)
register(Comment)
register(DocumentContent, DocumentContentAdmin)
