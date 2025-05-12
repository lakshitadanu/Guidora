from django.urls import path
from . import views

app_name = 'resume_analysis'

urlpatterns = [
    path('', views.analyze_resume, name='analyze_resume'),
    path('upload/', views.upload_resume, name='upload_resume'),
    path('result/<int:analysis_id>/', views.analysis_result, name='analysis_result'),
    path('stream-analysis/', views.StreamAnalysisView.as_view(), name='stream_analysis'),
    path('chat-with-mistral/', views.chat_with_mistral, name='chat_with_mistral'),
] 