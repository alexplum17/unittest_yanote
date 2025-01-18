from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class RoutesTests(TestCase):
    def setUp(self):
        """
        Метод, который выполняется перед каждым тестом.
        Создает пользователя и заметку, которая будет использована
        в тестах.
        """
        self.user = User.objects.create_user(username='testuser',
                                             password='testpassword')
        self.note = Note.objects.create(title='Тестовая заметка',
                                        text='Текст заметки',
                                        author=self.user)

    def test_home_page_accessible_to_anonymous_user(self):
        """
        Проверяет, что домашняя страница доступна анонимным пользователям.
        Ожидается код статуса 200 (OK).
        """
        response = self.client.get(reverse('notes:home'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_accessible_to_authenticated_user(self):
        """
        Проверяет, что определенные страницы доступны
        только для авторизованных пользователей.
        Ожидается код статуса 200 (OK) для каждой страницы.
        """
        self.client.login(username='testuser', password='testpassword')
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_detail_edit_and_delete_accessible_to_note_author(self):
        """
        Проверяет, что автор заметки может получить доступ к деталям,
        редактированию и удалению своей заметки.
        Ожидается код статуса 200 (OK).
        """
        self.client.login(username=self.note.author.username,
                          password='testpassword')
        for url in [
            reverse('notes:detail', kwargs={'slug': self.note.slug}),
            reverse('notes:edit', kwargs={'slug': self.note.slug}),
            reverse('notes:delete', kwargs={'slug': self.note.slug}),
        ]:
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_detail_edit_and_delete_not_accessible_to_another_user(self):
        """
        Проверяет, что другой пользователь не может получить
        доступ к деталям, редактированию и удалению заметки
        авторизованного пользователя.
        Ожидается код статуса 404 (NOT FOUND).
        """
        User.objects.create_user(username='anotheruser',
                                 password='anotherpassword')
        self.client.login(username='anotheruser', password='anotherpassword')
        for url in [
            reverse('notes:detail', kwargs={'slug': self.note.slug}),
            reverse('notes:edit', kwargs={'slug': self.note.slug}),
            reverse('notes:delete', kwargs={'slug': self.note.slug}),
        ]:
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_anonymous_user_redirects_to_login(self):
        """
        Проверяет, что анонимные пользователи перенаправляются
        на страницу входа, когда они пытаются получить доступ
        к защищенным страницам.
        """
        for url in [
            reverse('notes:list'),
            reverse('notes:add'),
            reverse('notes:success'),
            reverse('notes:detail', kwargs={'slug': self.note.slug}),
            reverse('notes:edit', kwargs={'slug': self.note.slug}),
            reverse('notes:delete', kwargs={'slug': self.note.slug}),
        ]:
            response = self.client.get(url)
            self.assertRedirects(response, f'/auth/login/?next={url}')

    def test_signup_login_logout_accessible_to_all(self):
        """
        Проверяет, что страницы регистрации, входа и выхода
        доступны всем пользователям.
        Ожидается код статуса 200 (OK) для каждой страницы.
        """
        response = self.client.get(reverse('users:signup'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
