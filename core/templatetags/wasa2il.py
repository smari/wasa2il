import os
import markdown2

from datetime import datetime
from PIL import Image
from pilkit.processors import SmartResize

from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
from django.utils.formats import dateformat
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from issue.models import Vote


register = template.Library()


@register.filter()
def may_expire(dt):
    now = datetime.now()

    css_class = 'expired' if dt < now else 'not-expired'
    formatted_datetime = dateformat.format(dt, settings.DATETIME_FORMAT)

    return mark_safe('<span class="%s">%s</span>' % (css_class, formatted_datetime))


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter(name='issuevoted')
def issuevoted(issue, user):
    try:
        ut = Vote.objects.get(user=user, issue=issue)
        if ut.value == 0:
            return False

        return True
    except Exception:
        return False


@register.filter(name="thumbnail")
def thumbnail(file, size='104x104'):
    try:

        # We will place the thumbnails in a directory alongside the image,
        # which will be named the same as the image except with "-thumbnail"
        # appended to it. Within that directory, there will be other images
        # named according to the requested size, for example "30x30.png" and
        # so forth. This way, the profile image names are entirely predictable
        # from the image names alone.
        thumb_dir = file.path + '-thumbnail'

        # Make sure that the thumbnail directory exists.
        if not os.path.isdir(thumb_dir):
            os.mkdir(thumb_dir)

        # Figure out the stand-alone filename ("30x30.png", for example) and
        # subsequently define the full local path name to the thumbnail and
        # its corresponding URL.
        thumb_filename = size + '.png'
        thumb_fullpath = os.path.join(thumb_dir, thumb_filename)
        thumb_url = file.url + '-thumbnail/' + thumb_filename

        # Check if the image is newer than the requested thumbnail, and if so,
        # remove the thumbnail so that it will be regenerated.
        if os.path.exists(thumb_fullpath) and os.path.getmtime(file.path) > os.path.getmtime(thumb_fullpath):
            os.unlink(thumb_fullpath)

        # Create the thumbnail if it does not already exist.
        if not os.path.exists(thumb_fullpath):
            width, height = [int(dimension) for dimension in size.split('x')]
            processor = SmartResize(width=width, height=height)
            image = processor.process(Image.open(file.path))
            image.save(thumb_fullpath, 'png', quality=90, optimize=True)

        return thumb_url

    except Exception as e:
        print('Error: %s' % e)
        return ""


@register.filter(is_safe=True)
@stringfilter
def markdown(value):
    return mark_safe(markdown2.markdown(value, extras=['break-on-newline']).replace('\\', ''))


@register.filter
def classname(obj):
    classname = obj.__class__.__name__
    return classname


@register.simple_tag
def repeater(string, count):
    # Making up for Django's inexplicable lack of ability to iterate from one
    # number to another in a template.
    return str(string) * count

@register.simple_tag(takes_context=True)
def add_breadcrumb(context, name=None, url=False, **kwargs):
    if not 'request' in context:
        return ""

    if not hasattr(context['request'], 'breadcrumbs'):
        context['request'].breadcrumbs = []
    breadcrumb = { "name": name, "url": url }
    if 'prepend' in kwargs:
        context['request'].breadcrumbs.insert(0, breadcrumb)
    else:
        context['request'].breadcrumbs.append(breadcrumb)
    return ""

@register.inclusion_tag('_breadcrumbs.html', takes_context=True)
def render_breadcrumbs(context):
    if not 'request' in context:
        return None

    request = context['request']
    if hasattr(request, 'breadcrumbs'):
        breadcrumbs = request.breadcrumbs
    else:
        breadcrumbs = []
    return {
        'breadcrumbs': breadcrumbs,
        'currentpath': request.path
    }

@register.inclusion_tag('_comments_section.html')
def comments_section(obj_key, obj_id, closed=False):
    return {
        'obj_id': obj_id,
        'obj_key': obj_key,
        'closed': closed,
        'btntext': _('Add comment')
    }


@register.filter(name='fromunixts')
def fromunixts(value):
    return datetime.fromtimestamp(int(value))


@register.filter(name='phoneformat')
def phoneformat(phone):

    # No whitespace, thank you.
    phone = phone.replace(' ', '').strip()

    # This is the only format we know so far. Feel free to add!
    if len(phone) == 7 and phone.isdigit():
        return '%s-%s' % (phone[0:3], phone[3:])

    # If we haven't figured out the format, leave as is.
    return phone
