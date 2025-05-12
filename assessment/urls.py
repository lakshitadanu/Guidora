from django.urls import path
from . import views

app_name = 'assessment'

urlpatterns = [
    path('', views.assessment_list, name='assessment_list'),
    path('personality/', views.personality_assessment, name='personality_assessment'),
    path('aptitude/', views.aptitude_assessment, name='aptitude_assessment'),
    path('recommendations/', views.get_career_recommendations, name='career_recommendations'),
    path('generate-recommendations/', views.generate_recommendations, name='generate_recommendations'),
    path('retake/<str:assessment_type>/', views.retake_assessment, name='retake_assessment'),
] 