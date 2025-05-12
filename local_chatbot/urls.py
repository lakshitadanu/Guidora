from django.urls import path
from . import views

app_name = 'local_chatbot'
 
urlpatterns = [
    path('chat/', views.chat_ui, name='chat'),  # GET: chat UI for iframe
    path('chat-api/', views.chat, name='chat_api'),  # POST: chat API
    path('chat-history/', views.get_chat_history, name='chat_history'),
    path('chat-with-mistral/', views.chat_with_mistral, name='chat_with_mistral'),
] 