from datetime import timedelta
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from pages.models import Page, Domain
from forums.models import Post
from stars.models import Star
from stars.tasks import delete_old_stars

User = get_user_model()


class StarTestBase(TestCase):
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
        self.post = Post.objects.create(
            author=self.user,
            page=self.page,
            content='Hello world',
        )
        self.page_ct = ContentType.objects.get_for_model(Page)
        self.post_ct = ContentType.objects.get_for_model(Post)


class ToggleStarTests(StarTestBase):

    def test_unauthenticated_user_is_redirected(self):
        response = self.client.post(
            reverse('stars:toggle_star'),
            {'action': 'star', 'object_ct': 'page', 'object_id': self.page.id}
        )
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_can_star_a_page(self):
        self.client.login(username='stella', password='pass')
        self.client.post(
            reverse('stars:toggle_star'),
            {'action': 'star', 'object_ct': 'page', 'object_id': self.page.id}
        )
        self.assertTrue(self.page.stars.filter(user=self.user).exists())

    def test_authenticated_user_can_only_star_once(self):
        self.client.login(username='stella', password='pass')
        payload = {'action': 'star', 'object_ct': 'page', 'object_id': self.page.id}
        self.client.post(reverse('stars:toggle_star'), payload)
        response = self.client.post(reverse('stars:toggle_star'), payload)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(self.page.stars.filter(user=self.user).count(), 1)

    def test_authenticated_user_can_unstar_a_page(self):
        Star.objects.create(user=self.user, object_ct=self.page_ct, object_id=self.page.id)
        self.client.login(username='stella', password='pass')
        self.client.post(
            reverse('stars:toggle_star'),
            {'action': 'unstar', 'object_ct': 'page', 'object_id': self.page.id}
        )
        self.assertFalse(self.page.stars.filter(user=self.user).exists())

    def test_unstar_returns_404_if_star_does_not_exist(self):
        self.client.login(username='stella', password='pass')
        response = self.client.post(
            reverse('stars:toggle_star'),
            {'action': 'unstar', 'object_ct': 'page', 'object_id': self.page.id}
        )
        self.assertEqual(response.status_code, 404)

    def test_invalid_object_ct_returns_400(self):
        self.client.login(username='stella', password='pass')
        response = self.client.post(
            reverse('stars:toggle_star'),
            {'action': 'star', 'object_ct': 'user', 'object_id': self.user.id}
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_action_returns_400(self):
        self.client.login(username='stella', password='pass')
        response = self.client.post(
            reverse('stars:toggle_star'),
            {'action': 'invalid', 'object_ct': 'page', 'object_id': self.page.id}
        )
        self.assertEqual(response.status_code, 400)

    def test_view_works_with_post_content_type(self):
        self.client.login(username='stella', password='pass')
        self.client.post(
            reverse('stars:toggle_star'),
            {'action': 'star', 'object_ct': 'post', 'object_id': self.post.id}
        )
        self.assertTrue(self.post.stars.filter(user=self.user).exists())


class StarDecayTests(StarTestBase):

    def test_stars_older_than_7_days_are_deleted(self):
        star = Star.objects.create(user=self.user, object_ct=self.page_ct, object_id=self.page.id)
        Star.objects.filter(pk=star.pk).update(created=timezone.now() - timedelta(days=8))
        delete_old_stars()
        self.assertFalse(Star.objects.filter(pk=star.pk).exists())

    def test_stars_newer_than_7_days_are_kept(self):
        star = Star.objects.create(user=self.user, object_ct=self.page_ct, object_id=self.page.id)
        delete_old_stars()
        self.assertTrue(Star.objects.filter(pk=star.pk).exists())


class StarSignalsTests(StarTestBase):

    def test_page_total_stars_increments_on_star(self):
        Star.objects.create(user=self.user, object_ct=self.page_ct, object_id=self.page.id)
        self.page.refresh_from_db()
        self.assertEqual(self.page.total_stars, 1)

    def test_page_total_stars_decrements_on_unstar(self):
        star = Star.objects.create(user=self.user, object_ct=self.page_ct, object_id=self.page.id)
        star.delete()
        self.page.refresh_from_db()
        self.assertEqual(self.page.total_stars, 0)

    def test_page_brightness_updated_on_star(self):
        Star.objects.create(user=self.user, object_ct=self.page_ct, object_id=self.page.id)
        self.page.refresh_from_db()
        self.assertGreater(self.page.brightness, 0)

    def test_update_page_brightness_index_and_rise(self):
        from pages.tasks import update_rising_scores
        from stars.utils import calculate_brightness

        user_count = User.objects.count()
        page_b = Page.objects.create(canonical='example.com/page-b', title='Page B', domain=self.domain)

        # Invert the ranks: self.page has 1 star (higher brightness) but rank 2, page_b has 0 stars but rank 1
        self.page.total_stars = 1
        self.page.brightness = calculate_brightness(1, user_count)
        self.page.brightness_index = 2
        self.page.save(update_fields=['total_stars', 'brightness', 'brightness_index'])
        page_b.total_stars = 0
        page_b.brightness = calculate_brightness(0, user_count)
        page_b.brightness_index = 1
        page_b.save(update_fields=['total_stars', 'brightness', 'brightness_index'])

        update_rising_scores()

        self.page.refresh_from_db()
        page_b.refresh_from_db()
        self.assertEqual(self.page.brightness_index, 1)
        self.assertEqual(page_b.brightness_index, 2)
        self.assertGreater(self.page.rising_score, 0)
        self.assertLess(page_b.rising_score, 0)

    def test_update_forging_scores(self):
        from pages.tasks import update_forging_scores

        page_b = Page.objects.create(canonical='example.com/page-b', title='Page B', domain=self.domain)
        # self.page has one post from setUp; page_b has none

        update_forging_scores()

        self.page.refresh_from_db()
        page_b.refresh_from_db()
        self.assertEqual(self.page.forging_score, 1.0)
        self.assertEqual(page_b.forging_score, 0.0)

    def test_update_poppin_scores(self):
        from pages.tasks import update_poppin_scores
        from unittest.mock import patch

        page_b = Page.objects.create(canonical='example.com/page-b', title='Page B', domain=self.domain)

        def fake_cache_get(key):
            if key == f'presence:room_{self.page.pk}':
                return {'channel1': 'user1', 'channel2': 'user2'}
            return None

        with patch('pages.tasks.cache.get', side_effect=fake_cache_get):
            update_poppin_scores()

        self.page.refresh_from_db()
        page_b.refresh_from_db()
        self.assertEqual(self.page.poppin_score, 1.0)
        self.assertEqual(page_b.poppin_score, 0.0)

    def test_signal_works_with_post(self):
        Star.objects.create(user=self.user, object_ct=self.post_ct, object_id=self.post.id)
        self.post.refresh_from_db()
        self.assertEqual(self.post.total_stars, 1)
        self.assertGreater(self.post.brightness, 0)
