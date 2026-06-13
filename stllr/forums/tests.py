from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from pages.models import Page, Domain
from forums.models import Post

User = get_user_model()


class PostTestBase(TestCase):
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
            content='Hello world.',
        )


class CreatePostTests(PostTestBase):

    def test_unauthenticated_user_is_redirected(self):
        response = self.client.post(reverse('forums:create_post'), {
            'page': self.page.id,
            'content': 'Hello world'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Post.objects.filter(content='Hello world').exists())

    def test_authenticated_user_can_create_a_post(self):
        self.client.login(username='stella', password='pass')
        response = self.client.post(reverse('forums:create_post'), {
            'page': self.page.id,
            'content': 'Hello world',
        })
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Post.objects.filter(page=self.page, content='Hello world').exists())

    def test_reply_has_correct_thread_level(self):
        self.client.login(username='stella', password='pass')
        self.client.post(reverse('forums:create_post'), {
            'page': self.page.id,
            'content': 'Reply post',
            'parent': self.post.id,
        })
        reply = Post.objects.get(content='Reply post')
        self.assertEqual(reply.thread_level, 1)

    def test_invalid_post_is_not_created(self):
        self.client.login(username='stella', password='pass')
        response = self.client.post(reverse('forums:create_post'), {
            'page': self.page.id,
            'content': ''
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Post.objects.filter(content='').exists())


class RemovePostTests(PostTestBase):

    def test_author_can_remove_their_own_post(self):
        self.client.login(username='stella', password='pass')
        self.client.post(reverse('forums:remove_post', args=[self.post.id]))
        self.post.refresh_from_db()
        self.assertTrue(self.post.removed)

    def test_stranger_cannot_remove_someone_elses_post(self):
        stranger = User.objects.create_user(username='stranger')
        stranger.set_password('pass')
        stranger.save()
        self.client.login(username='stranger', password='pass')
        response = self.client.post(reverse('forums:remove_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 403)
        self.post.refresh_from_db()
        self.assertFalse(self.post.removed)

    def test_unauthenticated_user_is_redirected(self):
        response = self.client.post(reverse('forums:remove_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertFalse(self.post.removed)


class MarkdownifyTests(PostTestBase):

    def test_unauthenticated_user_is_redirected(self):
        response = self.client.post(reverse('forums:markdownify'), {'content': 'Hello'})
        self.assertEqual(response.status_code, 302)

    def test_returns_rendered_markdown(self):
        self.client.login(username='stella', password='pass')
        response = self.client.post(reverse('forums:markdownify'), {'content': '**bold**'})
        self.assertIn(b'<strong>bold</strong>', response.content)
