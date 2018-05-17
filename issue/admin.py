from django.contrib import admin

from issue.models import Comment
from issue.models import Document
from issue.models import DocumentContent
from issue.models import Issue


class IssueAdmin(admin.ModelAdmin):
    fieldsets = None
    list_display = ['name', 'slug', 'description', 'topics_str']
    exclude = ['votecount', 'votecount_yes', 'votecount_abstain', 'votecount_no']


class DocumentAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'slug']}),
    ]
    prepopulated_fields = {'slug': ['name']}
    list_display = ['name']
    search_fields = ['name']


class DocumentContentAdmin(admin.ModelAdmin):
    list_display = ['document', 'order', 'comments', 'user', 'created']


register = admin.site.register
register(Issue, IssueAdmin)
register(Comment)
register(Document, DocumentAdmin)
register(DocumentContent, DocumentContentAdmin)
