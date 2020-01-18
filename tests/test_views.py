from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class ViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Runs once to set up non-modified data for all class methods.
        print('---- Running tests/test_views.py ----')
        pass

    def setUp(self):
        # Run once for every test method to setup clean data.
        user1 = User.objects.create_user(username='user1', password='password')
        user1.save()


    def test_non_endpoints(self):
        response = self.client.get('/this-is-not-an-endpoint', follow=True)
        self.assertEqual(response.status_code, 404)

    def test_root_endpoint(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_admin_endpoint(self):
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get('/accounts/profile/')
        self.assertRedirects(response, '/accounts/login/?next=/accounts/profile/')

    def test_user_can_log_in(self):
        login = self.client.login(username='user1', password='password')
        response = self.client.get(reverse('polities'))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'user1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/accounts/profile/')
        self.assertEqual(response.status_code, 200)
