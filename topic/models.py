from datetime import datetime

from django.conf import settings
from django.db import models
from django.db.models import BooleanField
from django.db.models import Case
from django.db.models import Count
from django.db.models import IntegerField
from django.db.models import Q
from django.db.models import When
from django.utils.translation import ugettext_lazy as _

from core.models import UserProfile


class TopicQuerySet(models.QuerySet):
    def listing_info(self, user):
        '''
        Adds information relevant to listing of topics
        '''

        topics = self
        now = datetime.now()

        if not user.is_anonymous():
            if not UserProfile.objects.get(user=user).topics_showall:
                topics = topics.filter(usertopic__user=user)

            # Annotate the user's favoriteness of topics. Note that even though
            # it's intended as a boolean, it is actually produced as an integer.
            # So it's 1/0, not True/False.
            if not user.is_anonymous():
                topics = topics.annotate(
                    favorited=Count(
                        Case(
                            When(usertopic__user=user, then=True),
                            output_field=BooleanField
                        ),
                        distinct=True
                    )
                )

        # Annotate issue count.
        topics = topics.annotate(issue_count=Count('issue', distinct=True))

        # Annotate usertopic count.
        topics = topics.annotate(usertopic_count=Count('usertopic', distinct=True))

        # Annotate counts of issues that are open and/or being voted on.
        topics = topics.annotate(
            issues_open=Count(
                Case(
                    When(issue__deadline_votes__gte=now, then=True),
                    output_field=IntegerField()
                ),
                distinct=True
            ),
            issues_voting=Count(
                Case(
                    When(Q(issue__deadline_votes__gte=now, issue__deadline_proposals__lt=now), then=True),
                    output_field=IntegerField()
                ),
                distinct=True
            )
        )

        return topics


class Topic(models.Model):
    """A collection of issues unified categorically."""
    objects = TopicQuerySet.as_manager()

    name = models.CharField(max_length=128, verbose_name=_('Name'))
    slug = models.SlugField(max_length=128, blank=True)

    description = models.TextField(verbose_name=_("Description"), null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, null=True, blank=True, related_name='topic_created_by')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, null=True, blank=True, related_name='topic_modified_by')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    polity = models.ForeignKey('polity.Polity')

    class Meta:
        ordering = ["name"]

    def new_comments(self):
        return Comment.objects.filter(issue__topics=self).order_by("-created")[:10]

    def __unicode__(self):
        return u'%s' % (self.name)


class UserTopic(models.Model):
    """Whether a user likes a topic."""
    topic = models.ForeignKey('topic.Topic')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        unique_together = (("topic", "user"),)
