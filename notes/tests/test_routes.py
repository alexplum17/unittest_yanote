from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class RoutesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser',
                                             password='testpassword')
        self.note = Note.objects.create(title='Тестовая заметка',
                                        text='Текст заметки', author=self.user)

    def test_home_page_accessible_to_anonymous_user(self):
        response = self.client.get(reverse('notes:home'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_accessible_to_authenticated_user(self):
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
        self.client.login(username=self.note.author.username,
                          password='testpassword')
        for url in [reverse('notes:detail', kwargs={'slug': self.note.slug}),
                    reverse('notes:edit', kwargs={'slug': self.note.slug}),
                    reverse('notes:delete', kwargs={'slug': self.note.slug})]:
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_note_detail_edit_and_delete_not_accessible_to_another_user(self):
        another_user = User.objects.create_user(username='anotheruser',
                                                password='anotherpassword')
        self.client.login(username='anotheruser', password='anotherpassword')
        for url in [reverse('notes:detail', kwargs={'slug': self.note.slug}),
                    reverse('notes:edit', kwargs={'slug': self.note.slug}),
                    reverse('notes:delete', kwargs={'slug': self.note.slug})]:
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_anonymous_user_redirects_to_login(self):
        for url in [reverse('notes:list'),
                    reverse('notes:add'),
                    reverse('notes:success'),
                    reverse('notes:detail', kwargs={'slug': self.note.slug}), 
                    reverse('notes:edit', kwargs={'slug': self.note.slug}), 
                    reverse('notes:delete', kwargs={'slug': self.note.slug})]:
            response = self.client.get(url)
            self.assertRedirects(response, f'/auth/login/?next={url}')

    def test_signup_login_logout_accessible_to_all(self):
        response = self.client.get(reverse('users:signup'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, HTTPStatus.OK)