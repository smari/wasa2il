
from datetime import datetime, timedelta
import os.path
import json

# for Discourse SSO support
import base64
import hmac
import hashlib
import urllib
from urlparse import parse_qs
# SSO done

from django.shortcuts import render
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.http import Http404
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.template import RequestContext
from django.db.models import Q
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.template.context_processors import csrf
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.utils.encoding import force_bytes

# BEGIN - Copied from django.contrib.auth.views to accommodate the login() function
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
# END

from django.contrib.auth.models import User
from core.models import UserProfile
from core.forms import UserProfileForm
from core.saml import authenticate, SamlException
from election.models import Election
from issue.forms import DocumentForm
from issue.models import Document
from issue.models import DocumentContent
from issue.models import Issue
from polity.models import Polity
from gateway.icepirate import configure_external_member_db
from topic.models import Topic

from hashlib import sha1


def home(request):
    ctx = {}

    try:
        polity = Polity.objects.get(is_front_polity=True)
        return HttpResponseRedirect("/polity/%d/" % polity.id)
    except Polity.DoesNotExist:
        pass

    if request.user.is_authenticated():
        if request.user.is_staff and Polity.objects.count() == 0:
            return HttpResponseRedirect("/polity/new")
        else:
            polities = request.user.polities.all()
    else:
        polities = Polity.objects.filter(is_nonmembers_readable=True)

    ctx["votingissues"] = Issue.objects.order_by("deadline_votes").filter(deadline_proposals__lt=datetime.now(),deadline_votes__gt=datetime.now(),polity__in=polities)
    ctx["openissues"] = Issue.objects.order_by("deadline_votes").filter(deadline_proposals__gt=datetime.now(),deadline_votes__gt=datetime.now(),polity__in=polities)
    ctx["elections"] = Election.objects.order_by("deadline_votes").filter(deadline_votes__gt=datetime.now(),polity__in=polities)

    return render_to_response("entry.html", ctx, context_instance=RequestContext(request))


def help(request, page):
    ctx = {
        'language_code': settings.LANGUAGE_CODE
    }
    for locale in [settings.LANGUAGE_CODE, "is"]: # Icelandic fallback
      filename = "help/%s/%s.html" % (locale, page)
      if os.path.isfile(os.path.join(os.path.dirname(__file__), '..', 'wasa2il/templates', filename)):
          return render_to_response(filename, ctx, context_instance=RequestContext(request))

    raise Http404


@never_cache
def profile(request, username=None):
    ctx = {}

    # Determine if we're looking up the currently logged in user or someone else.
    if username:
        profile_user = get_object_or_404(User, username=username)
    elif request.user.is_authenticated():
        profile_user = request.user
    else:
        return HttpResponseRedirect(settings.LOGIN_URL)

    # Get the user's polities.
    if profile_user == request.user:
        polities = profile_user.polities.all()
    else:
        polities = [p for p in profile_user.polities.all() if p.is_member(request.user) or p.is_listed]

    # Get the user's profile object.
    profile = UserProfile.objects.get(user_id=profile_user.id)

    # Get documents and documentcontents which user has made
    documentdata = []
    contents = profile_user.documentcontent_set.select_related('document').order_by('document__name', 'order')
    last_doc_id = 0
    for c in contents:
        if c.document_id != last_doc_id:
            documentdata.append(c.document) # Template will detect the type as Document and show as heading
            last_doc_id = c.document_id

        documentdata.append(c)

    # Get running elections in which the user is currently a candidate
    now = datetime.now()
    current_elections = Election.objects.filter(candidate__user=profile_user, deadline_votes__gte=now)

    ctx = {
        'polities': polities,
        'current_elections': current_elections,
        'documentdata': documentdata,
        'profile_user': profile_user,
        'profile': profile,
    }
    return render(request, 'profile.html', ctx)


@login_required
def view_settings(request):
    ctx = {}
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request=request, instance=UserProfile.objects.get(user=request.user))
        if form.is_valid():
            request.user.email = form.cleaned_data['email']
            request.user.save()
            form.save()

            request.session[LANGUAGE_SESSION_KEY] = request.user.userprofile.language

            if 'picture' in request.FILES:
                f = request.FILES.get("picture")
                m = sha1()
                m.update(force_bytes(request.user.username))
                hash = m.hexdigest()
                ext = f.name.split(".")[1] # UserProfileForm.clean_picture() makes sure this is safe.
                filename = "userimg_%s.%s" % (hash, ext)
                path = settings.MEDIA_ROOT + "/" + filename
                #url = settings.MEDIA_URL + filename
                pic = open(path, 'wb+')
                for chunk in f.chunks():
                    pic.write(chunk)
                pic.close()
                p = request.user.userprofile
                p.picture.name = filename
                p.save()

            return HttpResponseRedirect("/accounts/profile/")
        else:
            print "FAIL!"
            ctx["form"] = form
            return render_to_response("settings.html", ctx, context_instance=RequestContext(request))

    else:
        form = UserProfileForm(initial={'email': request.user.email}, instance=UserProfile.objects.get(user=request.user))

    ctx["form"] = form
    return render_to_response("settings.html", ctx, context_instance=RequestContext(request))


@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.POST.get(redirect_field_name,
                                   request.GET.get(redirect_field_name, ''))

    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            # Make sure that profile exists
            try:
                UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                profile = UserProfile()
                profile.user = request.user
                profile.save()

            request.session[LANGUAGE_SESSION_KEY] = request.user.userprofile.language

            if hasattr(settings, 'SAML_1'): # Is SAML 1.2 support enabled?
                if not request.user.userprofile.user_is_verified():
                    return HttpResponseRedirect(settings.SAML_1['URL'])

            if hasattr(settings, 'ICEPIRATE'): # Is IcePirate support enabled?
                configure_external_member_db(request.user, create_if_missing=False)

            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


@login_required
def verify(request):

    try:
        auth = authenticate(request, settings.SAML_1['URL'])
    except SamlException as e:
        ctx = {'e': e}
        return render_to_response('registration/saml_error.html', ctx)

    if UserProfile.objects.filter(verified_ssn=auth['ssn']).exists():
        taken_user = UserProfile.objects.select_related('user').get(verified_ssn=auth['ssn']).user
        ctx = {
            'auth': auth,
            'taken_user': taken_user,
        }

        auth_logout(request)

        return render_to_response('registration/verification_duplicate.html', ctx)

    profile = request.user.userprofile  # It shall exist at this point
    profile.verified_ssn = auth['ssn']
    profile.verified_name = auth['name'].encode('utf8')
    profile.verified_token = request.GET['token']
    profile.verified_timing = datetime.now()
    profile.save()

    if hasattr(settings, 'ICEPIRATE'): # Is IcePirate support enabled?
        configure_external_member_db(request.user, create_if_missing=True)

    return HttpResponseRedirect('/')

@login_required
def sso(request):
    if not hasattr(settings, 'DISCOURSE'):
        raise Http404

    key = str(settings.DISCOURSE['secret'])
    return_url = '%s/session/sso_login' % settings.DISCOURSE['url']

    payload = request.GET.get('sso')
    their_signature = request.GET.get('sig')

    if None in [payload, their_signature]:
        return HttpResponseBadRequest('Required parameters missing.')

    try:
        payload = urllib.unquote(payload)
        decoded = base64.decodestring(payload)
        assert 'nonce' in decoded
        assert len(payload) > 0
    except:
        return HttpResponseBadRequest('Malformed payload.')

    our_signature = hmac.new(key, payload, digestmod=hashlib.sha256).hexdigest()

    if our_signature != their_signature:
        return HttpResponseBadRequest('Malformed payload.')

    nonce = parse_qs(decoded)['nonce'][0]
    outbound = {
        'nonce': nonce,
        'email': request.user.email,
        'external_id': request.user.id,
        'username': request.user.username,
    }

    out_payload = base64.encodestring(urllib.urlencode(outbound))
    out_signature = hmac.new(key, out_payload, digestmod=hashlib.sha256).hexdigest()
    out_query = urllib.urlencode({'sso': out_payload, 'sig' : out_signature})

    return HttpResponseRedirect('%s?%s' % (return_url, out_query))


def error500(request):
    return render_to_response('500.html')
