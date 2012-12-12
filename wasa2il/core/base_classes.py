
from django.db import models
from fields import AutoUserField, CreatedField, ModifiedField, NameField, NameSlugField
from django.utils.safestring import mark_safe


class NameSlugBase(models.Model):
	name			= NameField()
	slug			= NameSlugField()

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


def getCreationBase(prefix):

	class CreationBase(models.Model):
		created_by		= AutoUserField(related_name='%s_created_by'%prefix)
		modified_by		= AutoUserField(related_name='%s_modified_by'%prefix)
		created			= CreatedField()
		modified		= ModifiedField()

		class Meta:
			abstract = True

	return CreationBase
