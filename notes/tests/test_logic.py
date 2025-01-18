from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note

User = get_user_model()


class NoteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser',
                                             password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.note = Note.objects.create(title='Моя заметка',
                                        text='Текст заметки',
                                        author=self.user,
                                        slug='test_note')

    def test_create_note_logged_in_user(self):
        title = 'Тестовая заметка'
        response = self.client.post(reverse('notes:add'), {
            'title': title,
            'text': 'Текст новой заметки.',
            'slug': slugify(title)
        })
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(Note.objects.filter(title=title).exists())

    def test_create_note_anonymous_user(self):
        self.client.logout()
        response = self.client.post(reverse('notes:add'), {
            'title': 'Анонимная заметка',
            'text': 'Это текст анонимной заметки.'
        })
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(Note.objects.filter(
            title='Анонимная заметка').exists())

    def test_create_note_unique_slug(self):
        title = 'Другая заметка'
        self.client.post(reverse('notes:add'), {
            'title': title,
            'text': 'Текст другой заметки.',
            'slug': self.note.slug
        })
        self.assertFalse(Note.objects.filter(title=title).exists())

    def test_create_note_auto_slug(self):
        title = 'Заметка без slug'
        response = self.client.post(reverse('notes:add'), {
            'title': title,
            'text': 'Текст новой заметки без slug.',
        })
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(Note.objects.filter(title=title).exists())
        created_note = Note.objects.get(title=title)
        self.assertEqual(created_note.slug, slugify(title))

    def test_edit_other_user_note_failure(self):
        User.objects.create_user(username='anotheruser',
                                 password='anotherpassword')
        self.client.logout()
        self.client.login(username='anotheruser', password='anotherpassword')
        response = self.client.post(reverse('notes:edit',
                                            args=[self.note.id]), {
            'title': 'Измененная заметка',
            'text': 'Текст измененной заметки.'
        })
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_delete_other_user_note_failure(self):
        User.objects.create_user(username='anotheruser',
                                 password='anotherpassword')
        self.client.logout()
        self.client.login(username='anotheruser', password='anotherpassword')
        response = self.client.post(reverse('notes:delete',
                                            args=[self.note.id]))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
