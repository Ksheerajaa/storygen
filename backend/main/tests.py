from django.test import TestCase
from django.contrib.auth.models import User
from .models import Story, StoryGeneration


class StoryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_story_creation(self):
        story = Story.objects.create(
            title='Test Story',
            content='This is a test story content.',
            author=self.user
        )
        self.assertEqual(story.title, 'Test Story')
        self.assertEqual(story.author, self.user)
        self.assertIsNotNone(story.created_at)


class StoryGenerationModelTest(TestCase):
    def test_generation_creation(self):
        generation = StoryGeneration.objects.create(
            prompt='Test prompt for story generation'
        )
        self.assertEqual(generation.prompt, 'Test prompt for story generation')
        self.assertEqual(generation.status, 'pending')
        self.assertIsNotNone(generation.created_at)
