from django.urls import path
from . import views

urlpatterns = [
    path('pricing/', views.pricing_view, name='pricing'),
]
