import datetime

from django.utils import timezone
from django.test import TestCase, Client
from django.urls import reverse

client = Client()

from .models import Question

def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionModelTest(TestCase):

    def test_no_question(self):

        response = client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No Polls happening right now')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_past_question(self):
        create_question('Past Question', -30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                 ['<Question: Past Question>']
                                 )

    def test_future_question(self):
        create_question('Future Question', 30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No Polls happening right now")
        self.assertQuerysetEqual(response.context['latest_question_list'],[])

    def test_future_and_past_question(self):
        create_question('Past Question', -30)
        create_question('Future Question', 30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                 ['<Question: Past Question>']
                                )

    def test_future_question_in_detail_view(self):
        future_question = create_question('Future Question', 5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question_in_detail_view(self):
        past_question = create_question('Past Question', -5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

