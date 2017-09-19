
from django.contrib import admin
from django.contrib import auth


from models import (
    UserProfile,
    Document,
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


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


class UserAdmin(auth.admin.UserAdmin):
    inlines = (UserProfileInline, )


# Register the admins
register = admin.site.register

# User profile mucking
admin.site.unregister(auth.models.User)
register(auth.models.User, UserAdmin)

register(UserProfile)

register(Document, NameSlugAdmin)
