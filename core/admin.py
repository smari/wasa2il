
from django.contrib import admin
from django.contrib import auth


from models import (
    Issue,
    Comment, Vote,
    UserProfile,
    Document,
    DocumentContent,
    )


def getDerivedAdmin(base_admin, **kwargs):
    class DerivedAdmin(base_admin):
        pass
    derived = DerivedAdmin
    for k, v in kwargs.iteritems():
        setattr(derived, k, getattr(base_admin, k, []) + v)
    return derived


def save_model(self, request, obj, form, change):
    if getattr(obj, 'created_by', None) is None:
        obj.created_by = request.user
    obj.modified_by = request.user
    obj.save()


class NameSlugAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'slug']}),
    ]
    prepopulated_fields = {'slug': ['name']}
    list_display = ['name']
    search_fields = ['name']


BaseIssueAdmin = getDerivedAdmin(NameSlugAdmin,
        list_display=['description'],
        search_fields=['description'],
    )
BaseIssueAdmin.fieldsets = [
        NameSlugAdmin.fieldsets[0],
        (None, {'fields': ['description']}),
    ]
BaseIssueAdmin.save_model = save_model


class IssueAdmin(BaseIssueAdmin):
    fieldsets = None
    list_display = BaseIssueAdmin.list_display + ['topics_str']
    exclude = ['votecount', 'votecount_yes', 'votecount_abstain', 'votecount_no']


#class VoteOptionAdmin(NameSlugAdmin):
#    pass

class VoteAdmin(admin.ModelAdmin):
    list_display = ['user']  # , 'option']


class DocumentContentAdmin(admin.ModelAdmin):
    list_display = ['document', 'order', 'comments', 'user', 'created']


class CommentAdmin(admin.ModelAdmin):
    save_model = save_model


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


class UserAdmin(auth.admin.UserAdmin):
    inlines = (UserProfileInline, )


# Register the admins
register = admin.site.register
register(Issue, IssueAdmin)
# register(VoteOption, VoteOptionAdmin)
register(Comment, CommentAdmin)
#register(Vote, VoteAdmin)

# User profile mucking
admin.site.unregister(auth.models.User)
register(auth.models.User, UserAdmin)

register(UserProfile)

register(Document, NameSlugAdmin)
register(DocumentContent, DocumentContentAdmin)
