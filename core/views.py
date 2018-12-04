

from datetime import datetime, timedelta
from xml.etree.ElementTree import ParseError
import contextlib
import json
import os
import shutil
import tempfile
import zipfile

# for Discourse SSO support
import base64
import hmac
import hashlib
import urllib
from urlparse import parse_qs
# SSO done

from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.http import Http404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.utils.encoding import force_bytes
from django.views.decorators.cache import never_cache
from termsandconditions.models import TermsAndConditions

from django.contrib.auth.models import User
from core.models import UserProfile
from core.forms import UserProfileForm
from core.forms import Wasa2ilRegistrationForm
from core.saml import authenticate, SamlException
from core.signals import user_verified
from core.utils import calculate_age_from_ssn
from core.utils import is_ssn_human_or_institution
from core.utils import random_word
from election.models import Election
from election.models import ElectionResult
from issue.forms import DocumentForm
from issue.models import Document
from issue.models import DocumentContent
from issue.models import Issue
from polity.models import Polity
from topic.models import Topic

from gateway.utils import get_member
from gateway.utils import update_member

from languagecontrol.utils import set_language

from hashlib import sha1

# BEGIN - Included for Wasa2ilRegistrationView and Wasa2ilActivationView
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from registration.backends.default.views import ActivationView
from registration.backends.default.views import RegistrationView
from registration import signals as registration_signals
# END


def home(request):
    # Redirect to main polity, if it exists.
    try:
        polity = Polity.objects.get(is_front_polity=True)
        return HttpResponseRedirect(reverse('polity', args=(polity.id,)))
    except Polity.DoesNotExist:
        pass

    # If no polities have been created yet...
    if Polity.objects.count() == 0:
        # ...create one, if we have the access.
        if request.user.is_authenticated() and request.user.is_staff:
            return HttpResponseRedirect(reverse('polity_add'))

        # If we're logged out or don't have staff access, display welcome page.
        return render(request, 'welcome.html')

    else:
        # If polities exists, but there is no main polity, redirect to the
        # polity listing.
        return HttpResponseRedirect(reverse('polities'))

def manifest(request):
    manifest = {
      "name": "%s" % (settings.INSTANCE_NAME),
      "short_name": "%s" % (settings.INSTANCE_NAME),
      "icons": [
        {
          "src": "/static/img/logo-32.png",
          "sizes": "32x32",
          "type": "image/png"
        },
        {
          "src": "/static/img/logo-100.png",
          "sizes": "100x100",
          "type": "image/png"
        },
        {
          "src": "/static/img/logo-101.png",
          "sizes": "101x101",
          "type": "image/png"
        },
        {
          "src": "/static/img/logo-192.png",
          "sizes": "192x192",
          "type": "image/png"
        },
        {
          "src": "/static/img/logo-256.png",
          "sizes": "256x256",
          "type": "image/png"
        },
      ],
      "start_url": "/",
      "background_color": "#ffffff",
      "theme_color": "#e9e9e9",
      "display": "standalone",
      "serviceworker": {
        "src": "/service-worker.js?ts=%s" % (settings.WASA2IL_HASH),
        "scope": "/",
        "use_cache": False
      },
      "gcm_sender_id": "%d" % (settings.GCM_SENDER_ID),
    }
    return JsonResponse(manifest)

def help(request, page):
    ctx = {
        'language_code': settings.LANGUAGE_CODE
    }
    for locale in [settings.LANGUAGE_CODE, "is"]: # Icelandic fallback
      filename = "help/%s/%s.html" % (locale, page)
      if os.path.isfile(os.path.join(os.path.dirname(__file__), '..', 'wasa2il/templates', filename)):
          return render(request, filename, ctx)

    raise Http404

@user_passes_test(lambda u: u.is_superuser)
def view_admintools(request):
    return render(request, 'admintools.html')

@never_cache
@login_required
def profile(request, username=None):
    ctx = {}

    # Determine if we're looking up the currently logged in user or someone else.
    if username:
        profile_user = get_object_or_404(User, username=username)
    elif request.user.is_authenticated():
        profile_user = request.user
    else:
        return HttpResponseRedirect(settings.LOGIN_URL)

    polities = profile_user.polities.all()
    profile = UserProfile.objects.get(user_id=profile_user.id)

    # Get running elections in which the user is currently a candidate
    now = datetime.now()
    elections = Election.objects.filter(candidate__user=profile_user)
    current_elections = elections.filter(deadline_votes__gte=now)

    ctx = {
        'polities': polities,
        'current_elections': current_elections,
        'elections': elections,
        'profile_user': profile_user,
        'profile': profile,
    }
    return render(request, 'profile/profile.html', ctx)


@login_required
def view_settings(request):

    # Short-hands.
    profile = request.user.userprofile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request=request, instance=profile)
        if form.is_valid():
            # FIXME/TODO: When a user changes email addresses, there is
            # currently no functionality to verify the new email address.
            # Therefore, the email field is disabled in UserProfileForm until
            # that functionality has been implemented.
            #request.user.email = form.cleaned_data['email']
            #request.user.save()
            form.save()

            set_language(request, form.cleaned_data['language'])

            if 'picture' in request.FILES:

                in_file = request.FILES.get('picture')

                # UserProfileForm makes sure that this works.
                extension = in_file.name.split('.')[-1]

                # A function for generating a new filename relative to upload
                # directory, returning both that and a full path as well.
                def new_full_name(extension):
                    # Filename relative to the uploads directory.
                    filename = os.path.join(
                        UserProfile.picture.field.upload_to,
                        'userimg_%s.%s' % (random_word(12), extension)
                    )

                    # Full path of the image on disk.
                    fullpath = os.path.join(settings.MEDIA_ROOT, filename)

                    return filename, fullpath

                # We'll generate a random filename until we find one that
                # isn't already in use. (Almost certainly, the first attempt
                # will do just fine.)
                filename, path = new_full_name(extension)
                while os.path.isfile(path):
                    filename, path = new_full_name(extension)

                # Write the picture to disk.
                pic = open(path, 'wb+')
                for chunk in in_file.chunks():
                    pic.write(chunk)
                pic.close()

                # Save the picture's name in the profile.
                profile.picture.name = filename
                profile.save()

                # Cleanup time!

                # First, find picture files used by any profile.
                db_pictures = [up['picture'] for up in UserProfile.objects.all().values('picture').distinct()]

                # Paths of profile pictures are denoted relative to the
                # settings.MEDIA_ROOT directory. The "upload_to" parameter
                # provided in the "picture" ImageField in the UserProfile
                # model tells us where exactly, inside settings.MEDIA_ROOT,
                # the profile pictures can be found. For example, when the
                # "upload_to" field is "profiles" (as should be the case
                # here), the filenames denoted in the user profiles should be
                # something like "profiles/userimg_something.png". This path
                # is relative to the settings.MEDIA_ROOT directory.
                upload_to = UserProfile.picture.field.upload_to

                # List the files that are actually in the profile picture
                # directory and delete them if they are no longer in use.
                items = os.listdir(os.path.join(settings.MEDIA_ROOT, upload_to))
                for item in items:

                    # Let's not delete the default image. That would be silly.
                    if item == 'default.jpg':
                        continue

                    # We'll use full disk paths for file operations.
                    item_fullpath = os.path.join(settings.MEDIA_ROOT, upload_to, item)

                    if os.path.isdir(item_fullpath):
                        # If this is a directory, we are slightly more shy of
                        # deleting the whole thing, so we'll explicitly check
                        # if it's a thumbnail directory (ending with
                        # "-thumbnail"). If it's some random directory of
                        # unknown origin, we'll leave it alone.
                        if item[-10:] == '-thumbnail' and os.path.join(upload_to, item[:-10]) not in db_pictures:
                            shutil.rmtree(item_fullpath)
                    elif os.path.isfile(item_fullpath):
                        # If this is a file, and it's not being used in a user
                        # profile, we'll delete it.
                        if os.path.join(upload_to, item) not in db_pictures:
                            os.unlink(item_fullpath)


            if hasattr(settings, 'ICEPIRATE'):
                # The request.user object doesn't yet reflect recently made
                # changes, so we need to ask the database explicitly.
                update_member(User.objects.get(id=request.user.id))

            return redirect(reverse('profile'))

    else:
        form = UserProfileForm(initial={'email': request.user.email}, instance=profile)

    ctx = {
        'form': form,
    }
    return render(request, 'accounts/settings.html', ctx)


@login_required
def personal_data(request):

    terms = TermsAndConditions.objects.filter(
        userterms__user=request.user
    ).order_by(
        '-userterms__date_accepted'
    ).first()

    ctx = {
        'terms': terms,
    }
    return render(request, 'accounts/personal_data.html', ctx)


@login_required
def personal_data_fetch(request):

    # First... a bunch of functions to make our lives easier.

    @contextlib.contextmanager
    def cd(newdir, cleanup=lambda: True):
        prevdir = os.getcwd()
        os.chdir(os.path.expanduser(newdir))
        try:
            yield
        finally:
            os.chdir(prevdir)
            cleanup()

    @contextlib.contextmanager
    def tempdir():
        dirpath = tempfile.mkdtemp()
        def cleanup():
            shutil.rmtree(dirpath)
        with cd(dirpath, cleanup):
            yield dirpath

    # Turns an issue model into JSON in a consistent manner.
    def jsonize_issue(issue):
        # It is wise to use .select_related('polity') in the input issue.
        issue_data = {
            'name': issue.name,
            'polity': issue.polity.slug,
            'polity_name': issue.polity.name,
            'issue_num': ('%d/%d' % (issue.issue_num, issue.issue_year)) if issue.issue_num else None,
            'state': issue.issue_state(),
            'created': issue.created.strftime(dt_format),
            'ended': issue.deadline_votes.strftime(dt_format),
            'archived': issue.archived,
        }

        # We only include this field if the issue has been processed because
        # otherwise it's misleading.
        if issue.is_processed:
            issue_data['majority_reached'] = issue.majority_reached()

        return issue_data

    # Helper function for writing the JSON in a consistent manner, preferably
    # in a way that is both machine-readable and human-readable.
    def write_json(filename, data):
        with open(filename, 'w') as f:

            output = json.dumps(
                data,
                indent=4,
                sort_keys=True,
                ensure_ascii=False
            ).encode('utf-8')

            f.write(output)
            f.close()

    # A function that imitates "zip -r <zipfile> <directory>".
    # Provided in an answer from George V. Reilly, here:
    # https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory
    def make_zipfile(output_filename, source_dir):
        relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
        with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zip:
            for root, dirs, files in os.walk(source_dir):
                zip.write(root, os.path.relpath(root, relroot))
                for file in files:
                    filename = os.path.join(root, file)
                    if os.path.isfile(filename):
                        arcname = os.path.join(os.path.relpath(root, relroot), file)
                        zip.write(filename, arcname)

    # Short-hands.
    user = request.user
    profile = user.userprofile

    # This is what we will eventually return, if everything goes well.
    package_data = None

    # The format we want for datetime objects. Note that a different format is
    # used in the resulting file name, because it needs to be filesystem-compatible.
    dt_format = '%Y-%m-%dT%H:%M:%S'

    # This temporary directory will be destroyed once we're done, even if
    # something fails, which is important because personal information is
    # being written to disk that should not stay there indefinitely. It should
    # only exist for the time needed to package it in a zip file and deliver
    # it to the user. This is a precaution; the file is still created in an
    # area that should be safe.
    with tempdir() as tmp_path:
        package_name = 'Personal-data.%s.%s' % (
            user.username,
            # Not the same datetime format as used in the files themselves,
            # because this needs to be filesystem-compatible.
            timezone.now().strftime('%Y-%m-%d.%H-%M-%S')
        )
        os.mkdir(package_name)
        os.chdir(package_name)

        # We are now working within the temporary package directory.

        # Compile information about user's participation in elections.
        elections = Election.objects.select_related(
            'polity'
        ).filter(
            candidate__user_id=user.id
        ).order_by(
            'deadline_candidacy'
        )
        election_export = []
        for election in elections:

            try:
                if election.results_are_ordered:
                    user_place = election.result.rows.get(candidate__user_id=user.id).order
                else:
                    if election.result.rows.filter(candidate__user_id=user.id).exists():
                        user_place = 'selected'
                    else:
                        user_place = 'not-selected'
            except ElectionResult.DoesNotExist:
                user_place = 'not-yet-determined'

            election_export.append({
                'name': election.name,
                'started': election.deadline_candidacy.strftime(dt_format),
                'ended': election.deadline_votes.strftime(dt_format),
                'polity_name': election.polity.name,
                'result_type': 'ordered' if election.results_are_ordered else 'not-ordered',
                'user_place': user_place,
            })
        write_json('elections.json', election_export)

        # Compile user information from Wasa2il itself.
        person_export = {
            'username': user.username,
            'email': user.email,
            'email_wanted': profile.email_wanted,
            'last_login': user.last_login.strftime(dt_format),
            'display_name': profile.displayname,
            'verified_ssn': profile.verified_ssn,
            'verified_name': profile.verified_name,
            'verified_timing': profile.verified_timing.strftime(dt_format),
            'polities': dict([(p.slug, p.name) for p in user.polities.exclude(is_front_polity=True)]),
            'date_joined': user.date_joined.strftime(dt_format),
            'bio': profile.bio,
        }
        write_json('voting_system_user.json', person_export)

        # Compile document contents that the user has authorship over. Note
        # that the content of the document contents are not necessarily from
        # the user, but is the aggregate result of whatever was before, plus
        # the work of the user.
        document_content_export = []
        for dc in user.documentcontent_set.select_related('document__polity').order_by('created'):

            try:
                issue = Issue.objects.select_related('polity').get(documentcontent=dc)
                issue_data = jsonize_issue(issue)

            except Issue.DoesNotExist:
                issue_data = None

            document_content_export.append({
                'name': dc.name,
                'order': dc.order,
                'author_comment': dc.comments,
                'status': dc.status,
                'created': dc.created.strftime(dt_format),
                'polity': dc.document.polity.slug,
                'polity_name': dc.document.polity.name,
                'issue': issue_data,
                'text': dc.text,
            })
        write_json('document_contents.json', document_content_export)

        # Compile comments made by user.
        comment_export = []
        for comment in user.comment_created_by.select_related('issue__polity').order_by('created'):
            comment_export.append({
                'issue': jsonize_issue(comment.issue),
                'created': comment.created.strftime(dt_format),
                'text': comment.comment,
            })
        write_json('comments.json', comment_export)

        # Include the user's picture, if available.
        try:
            filename = profile.picture.file.name
            ending = filename.split('.')[-1]
            shutil.copyfile(filename, 'picture.%s' % ending)
        except IOError:
            # File is unavailable for some reason. We'll move on.
            pass

        # Include data from IcePirate, if enabled.
        if hasattr(settings, 'ICEPIRATE'):
            success, member, error = get_member(profile.verified_ssn)
            write_json('member_registry.json', member)

        # Zip it!
        os.chdir('..')
        make_zipfile('%s.zip' % package_name, package_name)

        # Get the content for delivery, before it vanishes.
        with open('%s.zip' % package_name, 'r') as f:
            package_data = f.read()

    # At this point, the local temporary files should have been deleted, even
    # if an error has occurred.

    # Push the content to the user as a zip file for download.
    response = HttpResponse(package_data, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s.zip' % package_name
    return response


class Wasa2ilRegistrationView(RegistrationView):

    form_class = Wasa2ilRegistrationForm

    def register(self, form):

        site = get_current_site(self.request)

        new_user_instance = form.save()

        userprofile = new_user_instance.userprofile
        userprofile.email_wanted = form['email_wanted'].value() == 'True'
        userprofile.save()

        new_user = self.registration_profile.objects.create_inactive_user(
            new_user=new_user_instance,
            site=site,
            send_email=self.SEND_ACTIVATION_EMAIL,
            request=self.request,
        )

        registration_signals.user_registered.send(
            sender=self.__class__,
            user=new_user,
            request=self.request
        )

        return new_user


class Wasa2ilActivationView(ActivationView):

    def activate(self, *args, **kwargs):
        activation_key = kwargs.get('activation_key', '')
        site = get_current_site(self.request)
        user, activated = self.registration_profile.objects.activate_user(
            activation_key,
            site
        )

        if activated:
            registration_signals.user_activated.send(
                sender=self.__class__,
                user=user,
                request=self.request
            )

            login(self.request, user, 'django.contrib.auth.backends.ModelBackend')

        return user

    def get_success_url(self, user):
        return '%s?returnTo=%s' % (reverse('tc_accept_page'), reverse('login_or_saml_redirect'))


@login_required
def verify(request):

    try:
        auth = authenticate(request, settings.SAML_1['URL'])
    except SamlException as e:
        ctx = {'e': e}
        return render(request, 'registration/saml_error.html', ctx)
    except ParseError:
        logout(request)
        return redirect(reverse('auth_login'))

    # Make sure that the user is, in fact, human.
    if is_ssn_human_or_institution(auth['ssn']) != 'human':
        ctx = {
            'ssn': auth['ssn'],
            'name': auth['name'].encode('utf8'),
        }
        return render(request, 'registration/verification_invalid_entity.html', ctx)


    # Make sure that user has reached the minimum required age, if applicable.
    if hasattr(settings, 'AGE_LIMIT') and settings.AGE_LIMIT > 0:
        age = calculate_age_from_ssn(auth['ssn'])
        if age < settings.AGE_LIMIT:
            logout(request)
            ctx = {
                'age': age,
                'age_limit': settings.AGE_LIMIT,
            }
            return render(request, 'registration/verification_age_limit.html', ctx)

    if UserProfile.objects.filter(verified_ssn=auth['ssn']).exists():
        taken_user = UserProfile.objects.select_related('user').get(verified_ssn=auth['ssn']).user
        ctx = {
            'auth': auth,
            'taken_user': taken_user,
        }

        logout(request)

        return render(request, 'registration/verification_duplicate.html', ctx)

    profile = request.user.userprofile  # It shall exist at this point
    profile.verified_ssn = auth['ssn']
    profile.verified_name = auth['name'].encode('utf8')
    profile.verified_token = request.GET['token']
    profile.verified_timing = datetime.now()
    profile.save()

    user_verified.send(sender=request.user.__class__, user=request.user, request=request)

    return HttpResponseRedirect('/')


@login_required
def login_or_saml_redirect(request):
    '''
    Check if user is verified. If so, redirect to the specified login
    redirection page. Otherwise, redirect to the SAML login page for
    verification. This is done in a view instead of redirecting straight from
    SamlMiddleware so that other login-related middleware can be allowed to do
    their thing before the SAML page, most notably TermsAndConditions, which
    we want immediately following the login, before verification.
    '''
    if request.user.userprofile.verified:
        return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        return redirect(settings.SAML_1['URL'])


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
        'name': request.user.userprofile.displayname.encode('utf-8'),
    }

    out_payload = base64.encodestring(urllib.urlencode(outbound))
    out_signature = hmac.new(key, out_payload, digestmod=hashlib.sha256).hexdigest()
    out_query = urllib.urlencode({'sso': out_payload, 'sig' : out_signature})

    return HttpResponseRedirect('%s?%s' % (return_url, out_query))


def error500(request):
    return render(request, '500.html')
