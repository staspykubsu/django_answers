from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from .models import Doctor, Review
from .forms import ReviewForm
import re

def process_review_text(text):
    """
    Обработка текста отзыва:
    1. Если встречено подряд 5 ЗАГЛАВНЫХ букв, весь текст к нижнему регистру
    2. Заглавные буквы в начале предложения
    3. Перед знаком препинания - только 1 пробел
    4. Заглавные буквы A-Z заменяются на цифры 0-9
    """
    # Проверяем наличие 5 подряд заглавных букв
    if re.search(r'[А-ЯA-Z]{5,}', text):
        text = text.lower()
    
    # Приводим к правильному регистру: первая буква предложения заглавная, остальные строчные
    sentences = re.split(r'([.!?]+)', text)
    processed_sentences = []
    
    for i in range(0, len(sentences), 2):
        if i < len(sentences):
            sentence = sentences[i].strip()
            if sentence:
                # Делаем первую букву заглавной
                sentence = sentence[0].upper() + sentence[1:].lower()
                processed_sentences.append(sentence)
            
            # Добавляем знак препинания, если есть
            if i + 1 < len(sentences):
                processed_sentences.append(sentences[i + 1])
    
    text = ''.join(processed_sentences)
    
    # Убираем лишние пробелы перед знаками препинания
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    
    # Заменяем заглавные английские буквы на цифры
    letter_to_digit = {
        'A': '0', 'B': '1', 'C': '2', 'D': '3', 'E': '4',
        'F': '5', 'G': '6', 'H': '7', 'I': '8', 'J': '9',
        'K': '0', 'L': '1', 'M': '2', 'N': '3', 'O': '4',
        'P': '5', 'Q': '6', 'R': '7', 'S': '8', 'T': '9',
        'U': '0', 'V': '1', 'W': '2', 'X': '3', 'Y': '4',
        'Z': '5'
    }
    
    for letter, digit in letter_to_digit.items():
        text = text.replace(letter, digit)
    
    return text

@method_decorator(csrf_exempt, name='dispatch')
class AddReviewView(View):
    def get(self, request, doctor_id):
        doctor = get_object_or_404(Doctor, id=doctor_id)
        form = ReviewForm()
        
        specialities = doctor.specialities.all()
        specialities_text = ", ".join([s.name for s in specialities])
        
        return render(request, 'reviews/add_review.html', {
            'doctor': doctor,
            'form': form,
            'specialities_text': specialities_text
        })
    
    def post(self, request, doctor_id):
        doctor = get_object_or_404(Doctor, id=doctor_id)
        form = ReviewForm(request.POST)
        
        if form.is_valid():
            review = form.save(commit=False)
            review.doctor = doctor
            
            # Получаем IP-адрес пользователя
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            review.ip_address = ip
            
            # Если пользователь авторизован
            if request.user.is_authenticated:
                review.user = request.user
            
            # Обрабатываем текст отзыва
            review.processed_text = process_review_text(review.original_text)
            
            review.save()
            
            # Возвращаем данные в формате таблицы
            reviews = Review.objects.filter(doctor=doctor).order_by('-review_date')[:5]
            
            data = {
                'success': True,
                'message': 'Отзыв успешно добавлен',
                'recent_reviews': [
                    {
                        'id': r.id,
                        'text': r.processed_text,
                        'date': r.review_date.strftime('%d.%m.%Y %H:%M')
                    }
                    for r in reviews
                ]
            }
            return JsonResponse(data)
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
