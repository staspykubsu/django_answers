from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['original_text']
        widgets = {
            'original_text': forms.Textarea(attrs={
                'rows': 10,
                'cols': 60,
                'placeholder': 'Введите ваш отзыв (минимум 100 символов)',
                'style': 'width: 100%; padding: 10px;'
            })
        }
    
    def clean_original_text(self):
        text = self.cleaned_data['original_text']
        if len(text) < 100:
            raise forms.ValidationError('Должно быть хотя бы 100 символов')
        return text
