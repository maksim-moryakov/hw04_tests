from http import HTTPStatus

from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

CREATE = reverse('posts:post_create')
PROFILE = reverse('posts:profile',
                  kwargs={'username': settings.USER_NAME})


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username=settings.USER_NAME
        )
        cls.group = Group.objects.create(
            title=settings.GROUP_TITLE,
            slug=settings.SLUG,
            description=settings.DESCRIPTION
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text=settings.POST_TEXT,
            group=cls.group
        )
        cls.POST_EDIT = reverse('posts:post_edit',
                                kwargs={'post_id': cls.post.pk})

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_post_form(self):
        """Проверка формы создание поста автора"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'text',
            'group': self.group.pk
        }
        response = self.authorized_client.post(
            CREATE,
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, PROFILE)
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            author=self.author,
            text=form_data['text']).exists()
        )

    def test_edit_post_form(self):
        """Проверка формы редактирования поста"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тесе edited_post, игнорировать',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            self.POST_EDIT,
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(Post.objects.filter(
            text=form_data['text']).exists())
