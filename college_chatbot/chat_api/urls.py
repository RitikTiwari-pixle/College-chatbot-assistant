from django.urls import path
from . import views

# This file maps URLs for the 'chat_api' app

urlpatterns = [
    # This line tells Django:
    # When a request comes to '/api/ask/',
    # run the 'ask_question_api' function from views.py
    path('ask/', views.ask_question_api, name='ask_question_api'),
]