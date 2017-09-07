
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class NameSlugBase(models.Model):
    name = models.CharField(max_length=128, verbose_name=_('Name'))
    slug = models.SlugField(max_length=128, blank=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return u'%s' % (self.name)
