from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from pages.models import Page, Domain
from forums.models import Post
from oversight.models import PageReport, PostReport

User = get_user_model()

class ReportPageTests(TestCase):

    def setUp(self):
        self.stella = User.objects.create_user(username='stella')
        self.stella.set_password('pass')
        self.stella.save()
        self.domain = Domain.objects.create(name='example.com')
        self.page = Page.objects.create(
            canonical='example.com/page',
            title='Example Page',
            domain=self.domain,
        )

    def test_unauthenticated_user_is_redirected(self):
        response = self.client.get(reverse('oversight:report_page', args=[self.page.id]))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_can_report_a_page(self):
        self.client.login(username='stella', password='pass')
        self.client.post(reverse('oversight:report_page', args=[self.page.id]), {
            'policy': 'spam',
        })
        self.assertTrue(PageReport.objects.filter(reporter=self.stella, page=self.page).exists())

    def test_user_cannot_report_same_page_twice(self):
        self.client.login(username='stella', password='pass')
        response = self.client.post(reverse('oversight:report_page', args=[self.page.id]), {'policy': 'spam'})
        response = self.client.post(reverse('oversight:report_page', args=[self.page.id]), {'policy': 'spam'})
        self.assertRedirects(response, reverse('oversight:report_page_already'))
        self.assertEqual(PageReport.objects.filter(reporter=self.stella, page=self.page).count(), 1)

class ReportPostTests(TestCase):

    def setUp(self):
        self.stella = User.objects.create(username='stella')
        self.stella.set_password('pass')
        self.stella.save()
        self.domain = Domain.objects.create(name='example.com')
        self.page = Page.objects.create(
            canonical='example.com/page',
            title='Example Page',
            domain=self.domain
        )
        self.post = Post.objects.create(
            author=self.stella,
            page = self.page,
            content="Hello world"
        )

    def test_unauthenticated_user_is_redirected(self):
        response = self.client.get(reverse('oversight:report_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_can_report_a_post(self):
        self.client.login(username='stella', password='pass')
        self.client.post(reverse('oversight:report_post', args=[self.post.id]), {'policy': 'harassment'})
        self.assertTrue(PostReport.objects.filter(reporter=self.stella, post=self.post).exists())

    def test_user_cannot_report_same_post_twice(self):
        self.client.login(username='stella', password='pass')
        self.client.post(reverse('oversight:report_post', args=[self.post.id]), {'policy': 'harassment'})
        response = self.client.post(reverse('oversight:report_post', args=[self.post.id]), {'policy': 'harassment'})
        self.assertRedirects(response, reverse('oversight:report_post_already'))
        self.assertEqual(PostReport.objects.filter(reporter=self.stella, post=self.post).count(), 1)