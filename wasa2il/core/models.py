from django.db import models

from fields import NameField, NameSlugField, CreatedField, ModifiedField, AutoUserField

nullblank = { 'null': True, 'blank': True }

def getCreationBase(prefix=None):
	class CreationBase(models.Model):
		if prefix:
			created_by		= AutoUserField(related_name='%s_created_by'%prefix)
			modified_by		= AutoUserField(related_name='%s_modified_by'%prefix)
		else:
			created_by		= AutoUserField(related_name='created_by')
			modified_by		= AutoUserField(related_name='modified_by')
		created			= CreatedField()
		modified		= ModifiedField()
		class Meta:
			abstract = True
	return CreationBase

def getBaseIssue(prefix=None):
	class BaseIssue(getCreationBase(prefix)):
		name			= NameField()
		slug			= NameSlugField()
		description		= models.TextField(**nullblank)
		class Meta:
			abstract = True
	return BaseIssue

class Polity(getBaseIssue('polity')):
	parent			= models.ForeignKey('Polity')
	invite_threshold	= models.IntegerField(default=3)


class Topic(getBaseIssue('topic')):
	polity			= models.ForeignKey(Polity)

class Issue(getBaseIssue('issue')):
	topic			= models.ManyToManyField(Topic)

class Comment(getCreationBase('comment')):
	comment			= models.TextField()
	issue			= models.ForeignKey(Issue)

