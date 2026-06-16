from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from pages.models import Page, Domain
from crews.models import Crew
from forums.models import Post, Mention

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
            'content': '@stella Reply post',
            'parent': self.post.id,
        })
        reply = Post.objects.get(content='@stella Reply post')
        self.assertEqual(reply.thread_level, 1)

    def test_reply_with_parent_author_mention_is_created(self):
        self.client.login(username='stella', password='pass')
        response = self.client.post(reverse('forums:create_post'), {
            'page': self.page.id,
            'content': '@stella great post!',
            'parent': self.post.id,
        })
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Post.objects.filter(content='@stella great post!').exists())

    def test_reply_must_start_with_parent_author_mention(self):
        self.client.login(username='stella', password='pass')
        response = self.client.post(reverse('forums:create_post'), {
            'page': self.page.id,
            'content': 'Reply without mention',
            'parent': self.post.id,
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Post.objects.filter(content='Reply without mention').exists())

    def test_reply_mention_must_be_at_start(self):
        self.client.login(username='stella', password='pass')
        response = self.client.post(reverse('forums:create_post'), {
            'page': self.page.id,
            'content': 'Reply to @stella',
            'parent': self.post.id,
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Post.objects.filter(content='Reply to @stella').exists())

    def test_reply_requires_content_beyond_mention(self):
        self.client.login(username='stella', password='pass')
        for content in ('@stella ', '@stella   ', '@stella\t'):
            with self.subTest(content=content):
                response = self.client.post(reverse('forums:create_post'), {
                    'page': self.page.id,
                    'content': content,
                    'parent': self.post.id,
                })
                self.assertEqual(response.status_code, 400)
                self.assertFalse(Post.objects.filter(content=content).exists())

    def test_reply_mention_must_be_parent_author(self):
        other = User.objects.create_user(username='cosmo', password='pass')
        self.client.login(username='stella', password='pass')
        response = self.client.post(reverse('forums:create_post'), {
            'page': self.page.id,
            'content': f'@{other.username} wrong mention',
            'parent': self.post.id,
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Post.objects.filter(content=f'@{other.username} wrong mention').exists())

    def test_invalid_post_is_not_created(self):
        self.client.login(username='stella', password='pass')
        response = self.client.post(reverse('forums:create_post'), {
            'page': self.page.id,
            'content': ''
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Post.objects.filter(content='').exists())

    def test_post_content_cannot_be_only_whitespace(self):
        self.client.login(username='stella', password='pass')
        response = self.client.post(reverse('forums:create_post'), {
            'page': self.page.id,
            'content': '   ',
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Post.objects.filter(content='   ').exists())


class RemovePostTests(PostTestBase):

    def test_author_can_remove_their_own_post(self):
        self.client.login(username='stella', password='pass')
        self.client.post(reverse('forums:remove_post', args=[self.post.id]))
        self.post.refresh_from_db()
        self.assertTrue(self.post.removed)

    # TODO: Test posts correctly marked as removed by the author

    # TODO: Test removed posts do not display any author information

    def test_only_author_can_remove_their_own_post(self):
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


class MentionSignalTests(PostTestBase):

    def test_mention_created_for_existing_user(self):
        other = User.objects.create_user(username='cosmo', password='pass')
        post = Post.objects.create(author=self.user, page=self.page, content='Hello @cosmo!')
        self.assertTrue(Mention.objects.filter(post=post, user=other).exists())

    def test_mention_created_for_existing_crew(self):
        crew = Crew.objects.create(handle='nebula', name='Nebula Crew', creator=self.user)
        post = Post.objects.create(author=self.user, page=self.page, content='Hello @nebula!')
        self.assertTrue(Mention.objects.filter(post=post, crew=crew).exists())

    def test_unknown_handle_is_ignored(self):
        post = Post.objects.create(author=self.user, page=self.page, content='Hello @nobody!')
        self.assertFalse(Mention.objects.filter(post=post).exists())

    def test_multiple_mentions_in_one_post(self):
        other = User.objects.create_user(username='cosmo', password='pass')
        crew = Crew.objects.create(handle='nebula', name='Nebula Crew', creator=self.user)
        post = Post.objects.create(author=self.user, page=self.page, content='Hi @cosmo and @nebula!')
        self.assertTrue(Mention.objects.filter(post=post, user=other).exists())
        self.assertTrue(Mention.objects.filter(post=post, crew=crew).exists())

    def test_mentions_synced_on_edit(self):
        other = User.objects.create_user(username='cosmo', password='pass')
        new_user = User.objects.create_user(username='nova', password='pass')
        post = Post.objects.create(author=self.user, page=self.page, content='Hi @cosmo!')
        self.assertTrue(Mention.objects.filter(post=post, user=other).exists())
        post.content = 'Hi @nova!'
        post.save()
        self.assertFalse(Mention.objects.filter(post=post, user=other).exists())
        self.assertTrue(Mention.objects.filter(post=post, user=new_user).exists())

    def test_duplicate_handle_in_content_creates_one_mention(self):
        other = User.objects.create_user(username='cosmo', password='pass')
        post = Post.objects.create(author=self.user, page=self.page, content='@cosmo @cosmo again!')
        self.assertEqual(Mention.objects.filter(post=post, user=other).count(), 1)

    def test_no_mentions_in_plain_post(self):
        post = Post.objects.create(author=self.user, page=self.page, content='No mentions here.')
        self.assertEqual(Mention.objects.filter(post=post).count(), 0)


class MentionCompletionsTests(PostTestBase):

    def test_unauthenticated_user_is_redirected(self):
        response = self.client.get(reverse('forums:mention_completions'), {'q': 'ste'})
        self.assertEqual(response.status_code, 302)

    def test_empty_query_returns_empty_list(self):
        self.client.login(username='stella', password='pass')
        response = self.client.get(reverse('forums:mention_completions'), {'q': ''})
        self.assertEqual(response.json(), [])

    def test_returns_matching_user(self):
        self.client.login(username='stella', password='pass')
        response = self.client.get(reverse('forums:mention_completions'), {'q': 'ste'})
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['type'], 'user')
        self.assertEqual(data[0]['handle'], 'stella')

    def test_returns_matching_crew(self):
        Crew.objects.create(handle='stardust', name='Stardust Crew', creator=self.user)
        self.client.login(username='stella', password='pass')
        response = self.client.get(reverse('forums:mention_completions'), {'q': 'star'})
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['type'], 'crew')
        self.assertEqual(data[0]['handle'], 'stardust')
        self.assertEqual(data[0]['name'], 'Stardust Crew')

    def test_matching_is_case_insensitive(self):
        self.client.login(username='stella', password='pass')
        response = self.client.get(reverse('forums:mention_completions'), {'q': 'STE'})
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['handle'], 'stella')

    def test_non_matching_query_returns_empty_list(self):
        self.client.login(username='stella', password='pass')
        response = self.client.get(reverse('forums:mention_completions'), {'q': 'zzz'})
        self.assertEqual(response.json(), [])

    def test_results_capped_at_five_per_type(self):
        for i in range(7):
            User.objects.create_user(username=f'alpha{i}', password='pass')
        self.client.login(username='stella', password='pass')
        response = self.client.get(reverse('forums:mention_completions'), {'q': 'alpha'})
        self.assertLessEqual(len(response.json()), 5)
