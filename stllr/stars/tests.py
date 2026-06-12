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


class TogglePageStarTests(StarTestBase):

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

    def test_authenticated_user_can_unstar_a_page(self):
        Star.objects.create(user=self.user, object_ct=self.page_ct, object_id=self.page.id)
        self.client.login(username='stella', password='pass')
        self.client.post(
            reverse('stars:toggle_star'),
            {'action': 'unstar', 'object_ct': 'page', 'object_id': self.page.id}
        )
        self.assertFalse(self.page.stars.filter(user=self.user).exists())

    def test_invalid_action_returns_400(self):
        self.client.login(username='stella', password='pass')
        response = self.client.post(
            reverse('stars:toggle_star'),
            {'action': 'invalid', 'object_ct': 'page', 'object_id': self.page.id}
        )
        self.assertEqual(response.status_code, 400)


class TogglePostStarTests(StarTestBase):

    def test_unauthenticated_user_is_redirected(self):
        response = self.client.post(
            reverse('stars:toggle_star'),
            {'action': 'star', 'object_ct': 'post', 'object_id': self.post.id}
        )
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_can_star_a_post(self):
        self.client.login(username='stella', password='pass')
        self.client.post(
            reverse('stars:toggle_star'),
            {'action': 'star', 'object_ct': 'post', 'object_id': self.post.id}
        )
        self.assertTrue(self.post.stars.filter(user=self.user).exists())

    def test_authenticated_user_can_unstar_a_post(self):
        Star.objects.create(user=self.user, object_ct=self.post_ct, object_id=self.post.id)
        self.client.login(username='stella', password='pass')
        self.client.post(
            reverse('stars:toggle_star'),
            {'action': 'unstar', 'object_ct': 'post', 'object_id': self.post.id}
        )
        self.assertFalse(self.post.stars.filter(user=self.user).exists())

    def test_invalid_action_returns_400(self):
        self.client.login(username='stella', password='pass')
        response = self.client.post(
            reverse('stars:toggle_star'),
            {'action': 'invalid', 'object_ct': 'post', 'object_id': self.post.id}
        )
        self.assertEqual(response.status_code, 400)


class TotalStarsSignalTests(StarTestBase):

    def test_page_total_stars_increments_on_star(self):
        Star.objects.create(user=self.user, object_ct=self.page_ct, object_id=self.page.id)
        self.page.refresh_from_db()
        self.assertEqual(self.page.total_stars, 1)

    def test_page_total_stars_decrements_on_unstar(self):
        star = Star.objects.create(user=self.user, object_ct=self.page_ct, object_id=self.page.id)
        star.delete()
        self.page.refresh_from_db()
        self.assertEqual(self.page.total_stars, 0)

    def test_post_total_stars_increments_on_star(self):
        Star.objects.create(user=self.user, object_ct=self.post_ct, object_id=self.post.id)
        self.post.refresh_from_db()
        self.assertEqual(self.post.total_stars, 1)

    def test_post_total_stars_decrements_on_unstar(self):
        star = Star.objects.create(user=self.user, object_ct=self.post_ct, object_id=self.post.id)
        star.delete()
        self.post.refresh_from_db()
        self.assertEqual(self.post.total_stars, 0)
