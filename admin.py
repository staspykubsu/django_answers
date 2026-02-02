from django.contrib import admin
from django.db.models import Q
from .models import Speciality, Doctor, Review

class SpecialityAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

class DoctorAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'middle_name', 'get_specialities']
    search_fields = ['last_name', 'first_name', 'middle_name']
    filter_horizontal = ['specialities']
    
    def get_specialities(self, obj):
        return ", ".join([s.name for s in obj.specialities.all()])
    get_specialities.short_description = 'Специальности'

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'doctor', 'review_date', 'ip_address', 'user']
    list_display_links = ['id', 'doctor']
    search_fields = ['original_text', 'processed_text', 'doctor__last_name', 
                    'doctor__first_name', 'doctor__middle_name']
    readonly_fields = ['review_date', 'original_text_display', 'processed_text_display']
    list_per_page = 50
    
    fieldsets = (
        (None, {
            'fields': ('doctor', 'review_date')
        }),
        ('Отзыв', {
            'fields': ('original_text_display', 'processed_text_display', 'ip_address', 'user')
        }),
    )
    
    def original_text_display(self, obj):
        return f'<div style="white-space: pre-wrap;">{obj.original_text}</div>'
    original_text_display.short_description = 'Исходный отзыв'
    original_text_display.allow_tags = True
    
    def processed_text_display(self, obj):
        return f'<div style="white-space: pre-wrap;">{obj.processed_text}</div>'
    processed_text_display.short_description = 'Обработанный отзыв'
    processed_text_display.allow_tags = True
    
    def get_queryset(self, request):
        # Оптимизация для большого количества врачей
        return super().get_queryset(request).select_related('doctor', 'user')

admin.site.register(Speciality, SpecialityAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Review, ReviewAdmin)
