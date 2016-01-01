from django.test import TestCase

# From https://jameswestby.net/weblog/tech/17-directly-logging-in-a-user-in-django-tests.html

from django.conf import settings
from django.contrib.auth import login
from django.http import HttpRequest
from django.test.client import Client
from importlib import import_module

class TestClient(Client):

    def login_user(self, user):
        """
        Login as specified user, does not depend on auth backend (hopefully)

        This is based on Client.login() with a small hack that does not
        require the call to authenticate()
        """
        if not 'django.contrib.sessions' in settings.INSTALLED_APPS:
            raise AssertionError("Unable to login without django.contrib.sessions in INSTALLED_APPS")
        user.backend = "%s.%s" % ("django.contrib.auth.backends",
                                  "ModelBackend")
        engine = import_module(settings.SESSION_ENGINE)

        # Create a fake request to store login details.
        request = HttpRequest()
        if self.session:
            request.session = self.session
        else:
            request.session = engine.SessionStore()
        login(request, user)

        # Set the cookie to represent the session.
        session_cookie = settings.SESSION_COOKIE_NAME
        self.cookies[session_cookie] = request.session.session_key
        cookie_data = {
            'max-age': None,
            'path': '/',
            'domain': settings.SESSION_COOKIE_DOMAIN,
            'secure': settings.SESSION_COOKIE_SECURE or None,
            'expires': None,
        }
        self.cookies[session_cookie].update(cookie_data)

        # Save the session values.
        request.session.save()


class APITestClient(TestClient):
    pass


class APITestCase(TestCase):
    def http_action(self, verb, urlname, user, urlargs={}, data={}):
        client = APITestClient()
        if user:
            client.login_user(user)
        url = reverse(urlname, kwargs=urlargs)
        fun = getattr(client, verb)
        if verb in ["post", "put", "delete", "patch"]:
            res = fun(url, json.dumps(data), content_type='application/json')
        else:
            res = fun(url, data)
        try:
            res.json = json.loads(res.content)
        except Exception, e:
            pass

        return res

    def post(self, urlname, user=None, urlargs={}, data={}):
        return self.http_action("post", urlname, user, urlargs, data)

    def get(self, urlname, user=None, urlargs={}, data={}):
        return self.http_action("get", urlname, user, urlargs, data)

    def put(self, urlname, user=None, urlargs={}, data={}):
        return self.http_action("put", urlname, user, urlargs, data)

    def delete(self, urlname, user=None, urlargs={}, data={}):
        return self.http_action("delete", urlname, user, urlargs, data)

    def patch(self, urlname, user=None, urlargs={}, data={}):
        return self.http_action("patch", urlname, user, urlargs, data)

    def assertInAndEqual(self, heystack, needle, value):
        self.assertIn(needle, heystack)
        self.assertEqual(heystack[needle], value)


class CoreAPIv2Test(APITestCase):
    def setUp(self):
        self.test_polity = Polity(name='Test Polity')
        self.test_polity.save()

    def test_create_polity_unauthorized(self):
        data = {
            'name': 'My Test Polity'
        }
        self.post('api_2_polity_create', data=data)

    def test_create_polity_authorized(self):
        data = {
            'name': 'My Test Polity'
        }
        self.post('api_2_polity_create', user=self.user, data=data)

    def test_join_polity(self):
        res = self.post('api_2_polity_join', user=self.user,
                  urlargs={'polity': self.test_polity.id})
        self.assertEqual(m.status_code, 200)
        self.assertInAndEqual(m.json, 'user', self.user.id)
        self.assertInAndEqual(m.json, 'polity', self.test_polity.id)
        self.assertInAndEqual(m.json, 'status', 'joined')

    def test_join_polity_notallowed(self):
        res = self.post('api_2_polity_join', user=self.user,
                  urlargs={'polity': self.test_polity.id})

    def test_leave_polity(self):
        res = self.post('api_2_polity_leave', user=self.user,
                  urlargs={'polity': self.test_polity.id})

    def test_create_issue(self):
        res = self.post('api_2_issue_create', user=self.user,
                  urlargs={'polity': self.test_polity.id},
                  data={'name': 'My issue'})

    #def test_vote_issue(self):
    #    pass
