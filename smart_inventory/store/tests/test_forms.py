from django.test import TestCase
from django.contrib.auth.models import User
from ..forms import CustomUserCreationForm, ReviewForm, PostForm, CommentForm

class CustomUserCreationFormTest(TestCase):
    def test_valid_user_creation_form(self):
        form = CustomUserCreationForm(data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'password2': 'password123',
        })
        self.assertTrue(form.is_valid())

    def test_invalid_user_creation_form_mismatched_passwords(self):
        form = CustomUserCreationForm(data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'password2': 'password456',
        })
        self.assertFalse(form.is_valid())
        self.assertIn("The two password fields didn't match.", form.non_field_errors())

    def test_invalid_user_creation_form_existing_username(self):
        User.objects.create_user(username='existinguser', password='password123')
        form = CustomUserCreationForm(data={
            'username': 'existinguser',
            'email': 'new@example.com',
            'password': 'password123',
            'password2': 'password123',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)



class ReviewFormTest(TestCase):
    def test_valid_review_form(self):
        form = ReviewForm(data={
            'rating': 5,
            'comment': 'Много добра книга, хареса ми!',
        })
        self.assertTrue(form.is_valid())

    def test_review_form_invalid_rating_too_high(self):
        form = ReviewForm(data={
            'rating': 6,
            'comment': 'Оценка над допустимото.',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)

    def test_review_form_invalid_rating_too_low(self):
        form = ReviewForm(data={
            'rating': 0,
            'comment': 'Оценка под допустимото.',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)



class PostFormTest(TestCase):
    def test_valid_post_form(self):
        form = PostForm(data={
            'title': 'Ново заглавие на пост',
            'content': 'Съдържание на поста...',
            'status': 1,  # Published
        })
        self.assertTrue(form.is_valid())

    def test_invalid_post_form_missing_title(self):
        form = PostForm(data={
            'content': 'Съдържание на поста...',
            'status': 1,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_invalid_post_form_invalid_status(self):
        form = PostForm(data={
            'title': 'Заглавие',
            'content': 'Съдържание...',
            'status': 99,  # Несъществуващ статус
        })
        self.assertFalse(form.is_valid())
        self.assertIn('status', form.errors)



class CommentFormTest(TestCase):
    def test_valid_comment_form(self):
        form = CommentForm(data={
            'content': 'Това е един добър коментар.',
        })
        self.assertTrue(form.is_valid())

    def test_invalid_comment_form_empty_content(self):
        form = CommentForm(data={
            'content': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)


class ReviewFormTest(TestCase):
    def test_review_form_rating_widget_is_radioselect(self):
        form = ReviewForm()
        self.assertEqual(form.fields["rating"].widget.__class__.__name__, "RadioSelect")

    def test_review_form_comment_label(self):
        form = ReviewForm()
        self.assertEqual(form.fields["comment"].label, "Вашето ревю")