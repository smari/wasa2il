from django.db import models

from fields import NameField, NameSlugField, CreatedField, ModifiedField, AutoUserField

nullblank = { 'null': True, 'blank': True }


class CreationBase(models.Model):
	created_by		= AutoUserField()
	modified_by		= AutoUserField()
	created			= CreatedField()
	modified		= ModifiedField()
	class Meta:
		abstract = True

class BaseIssue(CreationBase):
	name			= NameField()
	slug			= NameSlugField()
	description		= models.TextField(**nullblank)
	class Meta:
		abstract = True

class Polity(BaseIssue):
	parent			= models.ForeignKey('Polity')
	invite_threshold	= models.IntegerField(default=3)


class Topic(BaseIssue):
	polity			= models.ForeignKey(Polity)

class Issue(BaseIssue):
	topic			= models.ManyToManyField(Topic)

class Comment(CreationBase):
	comment			= models.TextField()
	issue			= models.ForeignKey(Issue)

