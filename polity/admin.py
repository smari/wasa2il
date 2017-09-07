from django.contrib import admin

from polity.models import Polity
#from polity.models import PolityRuleset


class PolityAdmin(admin.ModelAdmin):
    fieldsets = None
    list_display = ['name', 'slug', 'description', 'parent']


register = admin.site.register
register(Polity, PolityAdmin)
#register(PolityRuleset)
