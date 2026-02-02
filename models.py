from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Speciality(models.Model):
    name = models.CharField('Название специальности', max_length=255)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Специальность'
        verbose_name_plural = 'Специальности'

class Doctor(models.Model):
    last_name = models.CharField('Фамилия', max_length=100)
    first_name = models.CharField('Имя', max_length=100)
    middle_name = models.CharField('Отчество', max_length=100, blank=True)
    specialities = models.ManyToManyField(Speciality, verbose_name='Специальности')
    
    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()
    
    def __str__(self):
        return self.full_name
    
    class Meta:
        verbose_name = 'Врач'
        verbose_name_plural = 'Врачи'

class Review(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name='Врач')
    original_text = models.TextField('Исходный отзыв')
    processed_text = models.TextField('Обработанный отзыв', blank=True)
    review_date = models.DateTimeField('Дата отзыва', auto_now_add=True)
    ip_address = models.GenericIPAddressField('IP-адрес', blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='Пользователь', 
                           blank=True, null=True)
    
    def clean(self):
        if len(self.original_text) < 100:
            raise ValidationError('Должно быть хотя бы 100 символов')
    
    def __str__(self):
        return f"Отзыв #{self.id} для {self.doctor}"
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-review_date']
