from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    """Форма для создания отзыва. Позволяет оставить отзыв анонимно или с контактами, выбрать оценку и написать текст."""
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль', required=False)
    email = forms.EmailField(label='Почта', required=False)
    anonymous = forms.BooleanField(label='Оставить анонимно', required=False)
    rating = forms.ChoiceField(
        label='Оценка',
        choices=[(i, '★' * i + '☆' * (5 - i)) for i in range(1, 6)],
        widget=forms.RadioSelect,
        required=True
    )
    class Meta:
        model = Feedback
        fields = ['nickname', 'email', 'password', 'anonymous', 'rating', 'text']
        labels = {
            'nickname': 'Ник',
            'email': 'Почта',
            'password': 'Пароль',
            'text': 'Отзыв',
            'rating': 'Оценка',
        }
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        """Проверяет, что если отзыв не анонимный, то указаны почта и пароль, а рейтинг в диапазоне 1-5."""
        cleaned_data = super().clean()
        anonymous = cleaned_data.get('anonymous')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        rating = cleaned_data.get('rating')
        if rating and int(rating) not in range(1, 6):
            self.add_error('rating', 'Оценка должна быть от 1 до 5.')
        if not anonymous:
            if not email:
                self.add_error('email', 'Укажите почту или выберите анонимный отзыв.')
            if not password:
                self.add_error('password', 'Укажите пароль или выберите анонимный отзыв.')
        return cleaned_data 