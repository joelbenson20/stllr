import json
from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache
from django.contrib.auth import get_user_model
from pages.models import Page, Domain

User = get_user_model()

class ExtensionViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='stella')
        self.user.set_password('pass')
        self.user.save()

    def _post_page(self, url='https://example.com/page', title='Example Page', version='2.0', tab='forum'):
        self.client.login(username='stella', password='pass')
        return self.client.post(
            reverse('extension:extension') + f'?tab={tab}',
            data=json.dumps({'page': {'data': {'url': url, 'title': title}}}),
            content_type='application/json',
            HTTP_X_EXTENSION_VERSION=version,
        )
    
    def test_unsupported_version_returns_426(self):
        response = self._post_page(version='1.0')
        self.assertEqual(response.status_code, 426)

    def test_unsupported_url_returns_405(self):
        response = self._post_page(url='http://localhost/anything')
        self.assertEqual(response.status_code, 405)

    def test_new_page_is_created(self):
        response = self._post_page()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Page.objects.filter(canonical='example.com/page').exists())

    def test_existing_page_is_not_duplicated(self):
        self._post_page()
        self._post_page()
        self.assertEqual(Page.objects.filter(canonical='example.com/page').count(), 1)

    def test_new_protocol_added_to_existing_page(self):
        self._post_page(url='https://example.com/page')
        self._post_page(url='http://example.com/page')
        page = Page.objects.get(canonical='example.com/page')
        self.assertIn('https', page.supported_protocols)
        self.assertIn('http', page.supported_protocols)

    def test_restricted_returns_html(self):
        response = self.client.get(reverse('extension:restricted'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('html', response.json())

class CSRFTokenTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='stella')
        self.user.set_password('pass')
        self.user.save()

    def test_authenticated_user_gets_403(self):
        response = self.client.get(reverse('extension:csrf_token'))
        self.assertEqual(response.status_code, 403)

    def test_authenticated_user_gets_token(self):
        self.client.login(username='stella', password='pass')
        response = self.client.get(reverse('extension:csrf_token'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('token', data)

class WSTicketTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='stella')
        self.user.set_password('pass')
        self.user.save()

    def test_unauthenticated_user_is_redirected(self):
        response = self.client.get(reverse('extension:ws_ticket'))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_gets_ticket(self):
        self.client.login(username='stella', password='pass')
        response = self.client.get(reverse('extension:ws_ticket'))
        self.assertEqual(response.status_code, 200)
        ticket = response.json().get('ticket')
        self.assertIsNotNone(ticket)
        self.assertEqual(cache.get(f'ws_ticket:{ticket}'), self.user.id)