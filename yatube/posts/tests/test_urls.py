from django.test import Client, TestCase

from http import HTTPStatus

from ..models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        """Созданим запись в БД для проверки доступности
        адреса user/test-slug/"""
        cls.author = User.objects.create(username='TestAuthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
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

    def test_guest_urls(self):
        """Проверяем общедоступные страницы"""
        urls_names = {
            '/': HTTPStatus.OK.value,
            '/group/test_slug/': HTTPStatus.OK.value,
            '/profile/TestAuthor/': HTTPStatus.OK.value,
            f'/posts/{self.post.pk}/': HTTPStatus.OK.value,
            '/unexisting_page/': HTTPStatus.NOT_FOUND.value,
        }
        for address, status in urls_names.items():
            with self.subTest(status=status):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_autorized_urls(self):
        """Проверяем страницы доступные автору поста"""
        urls_names = {
            f'/posts/{self.post.pk}/edit/': HTTPStatus.OK.value,
            '/create/': HTTPStatus.OK.value,
        }
        for address, status in urls_names.items():
            with self.subTest(status=status):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_url_to_template(self):
        """Проверка соответсвия url и template"""
        urls_template = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/TestAuthor/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in urls_template.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_post_edit_no_author(self):
        """Проверка редактирования поста не автором"""
        response = self.guest_client.get(
            f"/posts/{self.post.pk}/edit/")
        self.assertRedirects(response, (
            f'/auth/login/?next=/posts/{self.post.id}/edit/'))
