
from django.db import models
from fields import AutoUserField
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class NameSlugBase(models.Model):
    name = models.CharField(max_length=128, verbose_name=_('Name'))
    slug = models.SlugField(max_length=128, blank=True)

    class Meta:
        abstract = True

    def get_url(self, anchor=True):
        if anchor:
            print type(mark_safe(u'<a href="%s">%s</a>' % (self.slug, self.name)))
            return mark_safe(u'<a href="%s">%s</a>' % (self.slug, self.name))
        return u'/slug/%s/' % self.slug
    get_url.allow_tags = True
    get_url.short_description = 'Slug-URL'

    def __unicode__(self):
        return u'%s' % (self.name)
