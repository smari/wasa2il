from django.db import models


class BaseIssue(models.Model):
	name			= models.CharField(max_length=200)
	description		= models.TextField()

	class Meta:
		abstract = True


class Polity(BaseIssue):
	parent			= models.ForeignKey(Polity)
	invite_threshold	= models.IntegerField(default=3)


class Topic(BaseIssue):
	polity			= models.ForeignKey(Polity)


class Issue(BaseIssue):
	topic			= models.ManyToManyField(Topic)
	
