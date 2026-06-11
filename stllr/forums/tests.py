from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from pages.models import Page, Domain
from forums.models import Post, PostStar

User = get_user_model()

class CreatePostTests(TestCase):

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
    
    def test_unauthenticated_user_is_redirected(self):
        response = self.client.post(reverse('forums:create_post'), {
            'page': self.page.id,
            'content': 'Hello world'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Post.objects.exists())

    def test_authenticated_user_can_create_a_post(self):
        self.client.login(username='stella', password='pass')
        response = self.client.post(reverse('forums:create_post'), {
            'page': self.page.id,
            'content': 'Hello world',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Post.objects.filter(page=self.page, content='Hello world').exists())

    def test_reply_has_correct_thread_level(self):
        parent = Post.objects.create(
            author=self.user,
            page=self.page,
            content='Parent post',
        )
        self.client.login(username='stella', password='pass')
        self.client.post(reverse('forums:create_post'), {
            'page': self.page.id,
            'content': 'Reply post',
            'parent': parent.id,
        })
        reply = Post.objects.get(content='Reply post')
        self.assertEqual(reply.thread_level, 1)

    def test_invalid_post_is_not_created(self):            #TODO: Failing because Status Codes aren't yet properly implemented
        self.client.login(username='stella', password='pass')
        response = self.client.post(reverse('forums:create_post'), {
            'page': self.page.id,
            'content': ''
        })
        self.assertFalse(Post.objects.exists())

class RemovePostTests(TestCase):

    def setUp(self):
        self.author = User.objects.create_user(username='stella')
        self.author.set_password('pass')
        self.author.save()
        self.domain = Domain.objects.create(name='example.com')
        self.page = Page.objects.create(
            canonical='example.com/page',
            title='Example Page',
            domain=self.domain
        )
        self.post = Post.objects.create(
            author=self.author,
            page=self.page,
            content='Hello world.'
        )

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

    #TODO: Consider implementing 'moderator' permission that allows user to remove posts

    def test_unauthenticated_user_is_redirected(self):
        response = self.client.post(reverse('forums:remove_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertFalse(self.post.removed)

class PostToggleStarTests(TestCase):

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

    def test_unauthenticated_user_is_redirected(self):
        response = self.client.post(reverse('forums:toggle_star', args=[self.post.id]))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_can_star_a_post(self):
        self.client.login(username='stella', password='pass')
        self.client.post(reverse('forums:toggle_star', args=[self.post.id]), {'action': 'star'})
        self.assertTrue(PostStar.objects.filter(user=self.user, post=self.post).exists())

    def test_authenticated_user_can_unstar_a_post(self):
        PostStar.objects.create(user=self.user, post=self.post)
        self.client.login(username='stella', password='pass')
        self.client.post(reverse('forums:toggle_star', args=[self.post.id]), {'action': 'unstar'})
        self.assertFalse(PostStar.objects.filter(user=self.user, post=self.post).exists())

    def test_invalid_action_returns_400(self):
        self.client.login(username='stella', password='pass')
        response = self.client.post(reverse('forums:toggle_star', args=[self.post.id]), {'action': 'invalid'})
        self.assertEqual(response.status_code, 400)

class MarkdownifyTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='stella')
        self.user.set_password('pass')
        self.user.save()

    def test_unauthenticated_user_is_redirected(self):
        response = self.client.post(reverse('forums:markdownify'), {'content': 'Hello'})
        self.assertEqual(response.status_code, 302)

    def test_returns_rendered_markdown(self):
        self.client.login(username='stella', password='pass')
        response = self.client.post(reverse('forums:markdownify'), {'content': '**bold**'})
        self.assertIn(b'<strong>bold</strong>', response.content)