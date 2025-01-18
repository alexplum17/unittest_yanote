from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class NoteTests(TestCase):
    def setUp(self):
        """
        Метод, который выполняется перед каждым тестом.
        Создает двух пользователей и три заметки, ассоциированные
        с этими пользователями.
        """
        self.user1 = User.objects.create_user(username='user1',
                                               password='testpassword1')
        self.user2 = User.objects.create_user(username='user2',
                                               password='testpassword2')
        self.note1 = Note.objects.create(title='Первая заметка',
                                         text='Текст первой заметки',
                                         author=self.user1)
        self.note2 = Note.objects.create(title='Вторая заметка',
                                         text='Текст второй заметки',
                                         author=self.user1)
        self.note3 = Note.objects.create(title='Третья заметка',
                                         text='Текст третьей заметки',
                                         author=self.user2)

    def test_note_detail_in_object_list(self):
        """
        Проверяет, что заголовки заметок отображаются в
        списке заметок для авторизованного пользователя.
        """
        self.client.login(username='user1', password='testpassword1')
        response = self.client.get(reverse('notes:list'))
        self.assertContains(response, self.note1.title)
        self.assertContains(response, self.note2.title)
        self.assertNotContains(response, self.note3.title)

    def test_notes_visibility_by_user(self):
        """
        Проверяет, что пользователь видит только свои заметки
        в списке заметок.
        """
        self.client.login(username='user1', password='testpassword1')
        response = self.client.get(reverse('notes:list'))
        self.assertEqual(len(response.context['object_list']), 2)
        self.assertNotIn(self.note3, response.context['object_list'])

    def test_create_and_edit_note_form(self):
        """
        Проверяет, что форма создания и редактирования заметки
        представлена для авторизованного пользователя.
        """
        self.client.login(username='user1', password='testpassword1')
        for url in [reverse('notes:add'),
                    reverse('notes:edit', kwargs={'slug': self.note1.slug})]:
            response = self.client.get(url)
            self.assertIsInstance(response.context['form'], NoteForm)