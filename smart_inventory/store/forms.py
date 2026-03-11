from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from store.models import Review, Post, Comment


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")

        labels = {
            "username": "Потребителско име",
            "email": "Имейл",
        }

        help_texts = {
            "username": "Само букви, цифри и @/./+/-/_",
            "email": "Въведете валиден имейл адрес",
        }


class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ["rating", "comment"]

        widgets = {
            "rating": forms.RadioSelect(
                choices=[(i, str(i)) for i in range(1, 6)],
            ),
            "comment": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Оставете коментар тук..."
                }
            ),
        }

        labels = {
            "rating": "Вашата оценка",
            "comment": "Вашето ревю",
        }

    def clean_rating(self):
        rating = self.cleaned_data.get("rating")

        if rating < 1 or rating > 5:
            raise forms.ValidationError("Оценката трябва да е между 1 и 5.")

        return rating


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ["title", "content", "status"]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Заглавие"
            }),
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 6
            }),
            "status": forms.Select(attrs={
                "class": "form-select"
            }),
        }

        labels = {
            "title": "Заглавие на публикацията",
            "content": "Съдържание",
            "status": "Статус",
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ["content"]

        widgets = {
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Напишете вашия коментар..."
            }),
        }

        labels = {
            "content": "Вашият коментар",
        }
