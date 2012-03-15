
from django.db import models
from fields import AutoUserField, CreatedField, ModifiedField

def getCreationBase(prefix):
	class CreationBase(models.Model):
		created_by		= AutoUserField(related_name='%s_created_by'%prefix)
		modified_by		= AutoUserField(related_name='%s_modified_by'%prefix)
		created			= CreatedField()
		modified		= ModifiedField()
		class Meta:
			abstract = True
	return CreationBase
