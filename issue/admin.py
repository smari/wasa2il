from django.contrib import admin

from issue.models import Issue


class IssueAdmin(admin.ModelAdmin):
    fieldsets = None
    list_display = ['name', 'slug', 'description', 'topics_str']
    exclude = ['votecount', 'votecount_yes', 'votecount_abstain', 'votecount_no']


register = admin.site.register
register(Issue, IssueAdmin)
