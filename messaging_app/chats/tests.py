from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message

class MessageModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')

    def test_message_creation(self):
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Hello, this is a test message'
        )
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.receiver, self.user2)
        self.assertEqual(message.content, 'Hello, this is a test message')
        self.assertFalse(message.is_read)

class MessageViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')

    def test_message_str_representation(self):
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content='Test message'
        )
        self.assertEqual(str(message), f"Message from user1 to user2")
