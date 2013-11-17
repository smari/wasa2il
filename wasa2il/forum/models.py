
from django.db import models
from django.contrib.auth.models import User

from core.models import Polity


nullblank = {'null': True, 'blank': True}


class Forum(models.Model):
    polity = models.ForeignKey(Polity)
    name = models.CharField(max_length=200)
    nonmembers_post = models.BooleanField(default=False)


class Discussion(models.Model):
    forum = models.ForeignKey(Forum)
    name = models.CharField(max_length=200)
    started_by = models.ForeignKey(User)


class DiscussionPost(models.Model):
    user = models.ForeignKey(User)
    discussion = models.ForeignKey(Discussion)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    users_seen = models.ManyToManyField(User, related_name="seen")

    def format(self):
        import re
        text = self.text
        text = text.replace("\n", "<br/>\n")

        pat1 = re.compile(r"(^|[\n ])(([\w]+?://[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)", re.IGNORECASE | re.DOTALL)

        pat2 = re.compile(r"#(^|[\n ])(((www|ftp)\.[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)", re.IGNORECASE | re.DOTALL)

        text = pat1.sub(r'\1<a href="\2" target="_blank">\2</a>', text)
        text = pat2.sub(r'\1<a href="http:/\2" target="_blank">\2</a>', text)

        return text
