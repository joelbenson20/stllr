from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from pages.utils import get_canonical, get_domain_name, verify_supported, UnsupportedURLError
from pages.models import Page, Domain, PagePin
from unittest.mock import patch, MagicMock

User = get_user_model()

class PageTestBase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='stella')
        self.user.set_password('pass')
        self.user.save()
        self.domain = Domain.objects.create(name='example.com')
        self.page = Page.objects.create(
            canonical='example.com/page',
            title='Example Page',
            domain=self.domain,
        )

class GetCanonicalTests(TestCase):

    def test_strips_www(self):
        result = get_canonical('https://www.example.com/page')
        self.assertNotIn('www.', result)

    def test_strips_protocol(self):
        result = get_canonical('https://www.example.com/page')
        self.assertNotIn('https://', result)

    def test_strips_tracking_params_but_keeps_allowed(self):
        result = get_canonical('https://www.example.com/article?utm_source=twitter&id=42')
        self.assertNotIn('utm_source', result)
        self.assertIn('id=42', result)

    def test_strips_fragment(self):
        result = get_canonical('https://example.com/page#section')
        self.assertNotIn('#section', result)

class GetDomainNameTests(TestCase):

    def test_strips_www(self):
        self.assertEqual(get_domain_name('https://www.example.com/page'), 'example.com')

    def test_returns_bare_host(self):
        self.assertEqual(get_domain_name('https://example.com/page'), 'example.com')

    def test_lowercases_host(self):
        self.assertEqual(get_domain_name('https://Example.COM/page'), 'example.com')

    def test_ignores_path_and_query(self):
        self.assertEqual(get_domain_name('https://example.com/a/b?q=1#frag'), 'example.com')

    def test_handles_subdomain(self):
        self.assertEqual(get_domain_name('https://blog.example.com/post'), 'blog.example.com')

class PageLinkTests(PageTestBase):

    def test_returns_https_when_https_in_supported_protocols(self):
        self.page.supported_protocols = [Page.Protocol.HTTPS]
        self.assertEqual(self.page.get_absolute_url(), 'https://' + self.page.canonical)

    def test_returns_http_when_only_http_in_supported_protocols(self):
        self.page.supported_protocols = [Page.Protocol.HTTP]
        self.assertEqual(self.page.get_absolute_url(), 'http://' + self.page.canonical)

    def test_falls_back_to_https_when_supported_protocols_is_empty(self):
        self.page.supported_protocols = []
        self.assertEqual(self.page.get_absolute_url(), 'https://' + self.page.canonical)


class VerifySupportedTests(TestCase):

    def test_blocks_localhost(self):
        with self.assertRaises(UnsupportedURLError):
            verify_supported('http://localhost/anything')

    def test_blocks_private_ip(self):
        with self.assertRaises(UnsupportedURLError):
            verify_supported('http://192.168.1.1/internal')

    def test_blocks_unsupported_protocol(self):
        with self.assertRaises(UnsupportedURLError):
            verify_supported('ftp://example.com/file')

    def test_passes_normal_url(self):
        verify_supported('https://example.com/page')


class TogglePinTests(PageTestBase):

    def test_unauthenticated_user_is_redirected(self):
        response = self.client.post(
            reverse('pages:toggle_pin', args=[self.page.id]),
            {'action': 'pin'}
        )
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_can_pin_a_page(self):
        self.client.login(username='stella', password='pass')
        self.client.post(
            reverse('pages:toggle_pin', args=[self.page.id]),
            {'action': 'pin'}
        )
        self.assertTrue(PagePin.objects.filter(user=self.user, page=self.page).exists())

    def test_authenticated_user_can_unpin_a_page(self):
        PagePin.objects.create(user=self.user, page=self.page)
        self.client.login(username='stella', password='pass')
        self.client.post(
            reverse('pages:toggle_pin', args=[self.page.id]),
            {'action': 'unpin'}
        )
        self.assertFalse(PagePin.objects.filter(user=self.user, page=self.page).exists())

    def test_invalid_action_returns_400(self):
        self.client.login(username='stella', password='pass')
        response = self.client.post(
            reverse('pages:toggle_pin', args=[self.page.id]),
            {'action': 'invalid'}
        )
        self.assertEqual(response.status_code, 400)

    def test_pin_is_idempotent(self):
        self.client.login(username='stella', password='pass')
        url = reverse('pages:toggle_pin', args=[self.page.id])
        self.client.post(url, {'action': 'pin'})
        self.client.post(url, {'action': 'pin'})
        self.assertEqual(PagePin.objects.filter(user=self.user, page=self.page).count(), 1)

    def test_get_request_is_rejected(self):
        self.client.login(username='stella', password='pass')
        response = self.client.get(reverse('pages:toggle_pin', args=[self.page.id]))
        self.assertEqual(response.status_code, 405)


class FeedTests(TestCase):

    def test_feed_is_publicly_accessible(self):  #TODO: Write the feed view to also allow sort by users that starred or similar_pages
        response = self.client.get(reverse('pages:feed'))
        self.assertEqual(response.status_code, 200)

    def test_feed_returns_empty_response_past_last_page(self):
        response = self.client.get(reverse('pages:feed'), {'p': 99999})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')

    def test_feed_accepts_sort_parameters(self):
        for sort in ['firmament', 'brightest', 'rising']:
            response = self.client.get(reverse('pages:feed'), {'sort': sort})
            self.assertEqual(response.status_code, 200)


class SignalsTest(PageTestBase):

    def test_search_vector_populated_on_create(self):
        page = Page.objects.create(canonical='example.com/page2', title='Hello', domain=self.domain)
        page.refresh_from_db()
        self.assertIsNotNone(page.search_vector)

    def test_search_vector_not_updated_on_unrelated_save(self):
        Page.objects.filter(pk=self.page.pk).update(search_vector=None)
        self.page.save(update_fields=['brightness'])
        self.page.refresh_from_db()
        self.assertIsNone(self.page.search_vector)

    @patch('pages.signals.requests.get')
    def test_image_downloaded_on_create(self, mock_get):
        mock_get.return_value = MagicMock(content=b'imagedata')
        page = Page.objects.create(
            canonical='example.com/page2', image_url='https://example.com/img.jpg', domain=self.domain
        )
        mock_get.assert_called_once()
        page.refresh_from_db()
        self.assertTrue(page.image)

    @patch('pages.signals.requests.get')
    def test_image_not_downloaded_on_unrelated_save(self, mock_get):
        self.page.save()
        mock_get.assert_not_called()

