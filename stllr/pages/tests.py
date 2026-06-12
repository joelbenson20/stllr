from datetime import timedelta
from django.utils import timezone
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from pages.utils import get_canonical, get_domain_name, verify_supported, UnsupportedURLError
from pages.models import Page, Domain, PageStar, PagePin
from pages.tasks import delete_old_page_stars


User = get_user_model()

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
        self.assertEqual(result, 'example.com/page')

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

class PageStarDecayTests(TestCase):

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

    def test_stars_older_than_7_days_are_deleted(self):
        star = PageStar.objects.create(user=self.user, page=self.page)
        PageStar.objects.filter(pk=star.pk).update(created=timezone.now() - timedelta(days=8))
        delete_old_page_stars()
        self.assertFalse(PageStar.objects.filter(pk=star.pk).exists())

    def test_stars_newer_than_7_days_are_kept(self):
        star = PageStar.objects.create(user=self.user, page=self.page)
        delete_old_page_stars()
        self.assertTrue(PageStar.objects.filter(pk=star.pk).exists())

class ToggleStarTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='stella') #TODO: create_user with a password argument is not working, had to use set_password on next line. Why??
        self.user.set_password('pass')
        self.user.save()
        self.domain = Domain.objects.create(name='example.com')
        self.page = Page.objects.create(
            canonical='example.com/page', #TODO: Consider changing 'canonical' to 'path', stripping the domain (redundant), and getting rid of its uniqueness
            title='Example Page',
            domain=self.domain
        )
    
    def test_unauthenticated_user_is_redirected(self):
        response = self.client.post(
            reverse('pages:toggle_star', args=[self.page.id]),
            {'action': 'star'}
        )
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_can_star_a_page(self):          #TODO: Apparently EmailAuthBackend "isn't even wired in" according to Claude
        self.client.login(username='stella', password='pass')
        self.client.post(
            reverse('pages:toggle_star', args=[self.page.id]),
            {'action': 'star'}
        )
        self.assertTrue(PageStar.objects.filter(user=self.user, page=self.page).exists())

    def test_authenticated_user_can_unstar_a_page(self):
        PageStar.objects.create(user=self.user, page=self.page)
        self.client.login(username='stella', password='pass')
        self.client.post(
            reverse('pages:toggle_star', args=[self.page.id]),
            {'action': 'unstar'}
        )
        self.assertFalse(PageStar.objects.filter(user=self.user, page=self.page).exists())
    
    def test_invalid_action_returns_400(self):
        self.client.login(username='stella', password='pass')
        response = self.client.post(
            reverse('pages:toggle_star', args=[self.page.id]),
            {'action': 'invalid'}
        )
        self.assertEqual(response.status_code, 400)

class TogglePinTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='stella')
        self.user.set_password('pass')
        self.user.save()
        self.domain = Domain.objects.create(name='example.com')
        self.page = Page.objects.create(
            canonical='example.com/page',
            title='Example Page',
            domain=self.domain
        )
    
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

class FeedTests(TestCase):

    def test_feed_is_publicly_accessible(self):
        response = self.client.get(reverse('pages:feed'))
        self.assertEqual(response.status_code, 200)

    def test_feed_returns_empty_response_past_last_page(self):
        response = self.client.get(reverse('pages:feed'), {'p': 99999})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')

    def test_feed_accepts_sort_parameters(self):            #TODO: Consider testing that sorting actually works (more complex, especially for 'firmament' which needs to test patterns over many runs)
        for sort in ['firmament', 'brightest', 'rising']:
            response = self.client.get(reverse('pages:feed'), {'sort': sort})
            self.assertEqual(response.status_code, 200)