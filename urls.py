from django.urls import path
from .views import AddReviewView

urlpatterns = [
    path('add-review/<int:doctor_id>/', AddReviewView.as_view(), name='add_review'),
]
