from django.contrib import admin
from django.urls import path
from . import views
from .views import UserRegisterView

urlpatterns = [
    path('user/register/', UserRegisterView.as_view()),
]
