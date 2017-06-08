
import os
import markdown2

from PIL import Image

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

from core.models import UserTopic, Vote, ElectionVote


register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def sparkline(variable, skip_last=False):
    if isinstance(variable, dict):
        pairs = sorted([(k, v) for k, v in variable.iteritems()])
        sparkline = [0] * (pairs[-1][0] + 1)
        for i, v in pairs:
            sparkline[i] = v
        if 0 not in variable and '0' not in variable:
            variable = sparkline[1:]
        else:
            variable = sparkline
    if skip_last:
        variable = variable[:-1]
    return ','.join(str(v) for v in variable)


@register.filter(name='topicfavorited')
def topicfavorited(topic, user):
    try:
        UserTopic.objects.get(user=user, topic=topic)
        return True
    except UserTopic.DoesNotExist:
        return False


@register.filter(name='issuevoted')
def issuevoted(issue, user):
    try:
        ut = Vote.objects.get(user=user, issue=issue)
        if ut.value == 0:
            return False

        return True
    except Exception, e:
        print e
        return False


@register.filter(name='electionvoted')
def electionvoted(election, user):
    ut = 0
    try:
        ut = ElectionVote.objects.filter(user=user, election=election).count()
    except TypeError:
        pass

    return (ut > 0)

@register.filter(name="thumbnail")
def thumbnail(file, size='104x104'):
    try:
        # defining the size
        x, y = [int(x) for x in size.split('x')]
        # defining the filename and the miniature filename
        filehead, filetail = os.path.split(file.path)
        basename, format = os.path.splitext(filetail)
        miniature = basename + '_' + size + format
        filename = file.path
        miniature_filename = os.path.join(filehead, miniature)
        filehead, filetail = os.path.split(file.url)
        miniature_url = filehead + '/' + miniature
        if os.path.exists(miniature_filename) and os.path.getmtime(filename) > os.path.getmtime(miniature_filename):
            os.unlink(miniature_filename)
        # if the image wasn't already resized, resize it
        if not os.path.exists(miniature_filename):
            image = Image.open(filename)
            image.thumbnail([x, y], Image.ANTIALIAS)
            try:
                image.save(miniature_filename, image.format, quality=90, optimize=1)
            except Exception as e:
                print 'Error: %s' % e
                image.save(miniature_filename, image.format, quality=90)

        return miniature_url
    except Exception as e:
        print 'Error: %s' % e
        return ""

 
@register.filter(is_safe=True)
@stringfilter
def markdown(value):
    return mark_safe(markdown2.markdown(value, safe_mode='escape'))


@register.filter
def classname(obj):
    classname = obj.__class__.__name__
    return classname

