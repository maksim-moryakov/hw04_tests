from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='TestAuthor')
        cls.user = User.objects.create(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.groupSecond = Group.objects.create(
            title='Тестовая группа-2',
            slug='test_slug_2',
            description='Тестовое описание-2',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': self.author}),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}),
            'posts/create_post.html': reverse(
                'posts:post_edit', kwargs={'post_id': self.post.pk}),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Проверка контекста posts:index"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context.get('page_obj')[0]
        self.assertEqual(first_object.author.username, self.author.username)
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.group.title, self.group.title)

    def test_group_list_show_correct_context(self):
        """Проверка контекста posts:group_list"""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        expected = list(Post.objects.filter(group=self.group.pk))
        self.assertEqual(list(response.context.get('page_obj')), expected)

    def test_profile_show_correct_context(self):
        """Проверка контекста posts:profile"""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': self.author}))
        expected = list(Post.objects.filter(author=self.author))
        self.assertEqual(list(response.context.get('page_obj')), expected)

    def test_post_detail_show_correct_context(self):
        """Проверка контекста posts:post_detail"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}))
        post_odj = response.context.get('post')
        self.assertEqual(post_odj, self.post)

    form_fields = {
        'text': forms.fields.CharField,
        'group': forms.fields.ChoiceField,
    }

    def test_edit_post_show_correct_context(self):
        """Проверка контекста редактирование поста posts:post_create"""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}))
        self.assertTrue(response.context.get('is_edit'))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                field = response.context.get('form').fields[value]
                self.assertIsInstance(field, expected)

    def test_create_post_show_correct_context(self):
        """Проверка контекста создания поста posts:post_create"""
        response = self.authorized_client.get(
            reverse('posts:post_create', kwargs={}))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                field = response.context.get('form').fields[value]
                self.assertIsInstance(field, expected)

    def test_post_created_not_show_group_profile(self):
        """Проверка отсутстствия постов не в той группе"""
        urls = (
            reverse('posts:group_list', kwargs={
                'slug': self.groupSecond.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                page_obj = response.context.get('page_obj')
                self.assertEqual(len(page_obj), 0)

    def test_post_created_show_group_and_profile(self):
        """Проверка постов на странице группы и пользователя"""
        urls = (
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.author.username})
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                page_obj = response.context.get('page_obj')
                self.assertEqual(len(page_obj), 1)


class PaginatorViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='testUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        posts = (Post(
            text='Тестовый текст',
            group=cls.group,
            author=cls.author,
        ) for i in range(15))
        Post.objects.bulk_create(posts)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_paginator_index_page(self):
        """Проверяем выведение постов на index"""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context.get('page_obj')), 10
        )

    def test_paginator_index_page_two(self):
        """Проверяем выведение оставшихся постов на 2 странице"""
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page_obj')), 5)
