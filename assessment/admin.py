from django.contrib import admin
from .models import (
    PersonalityAssessment,
    AptitudeAssessment,
    AssessmentQuestion,
    UserAssessment,
    AssessmentResult,
    CareerRecommendation
)

@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'assessment_type', 'category')
    list_filter = ('assessment_type', 'category')
    search_fields = ('question_text', 'category')
    ordering = ('assessment_type', 'category')

@admin.register(PersonalityAssessment)
class PersonalityAssessmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'completed_at', 'openness_score', 'conscientiousness_score',
                   'extraversion_score', 'agreeableness_score', 'neuroticism_score')
    list_filter = ('completed_at',)
    search_fields = ('user__username', 'user__email')
    ordering = ('-completed_at',)

@admin.register(AptitudeAssessment)
class AptitudeAssessmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'completed_at', 'logical_score', 'numerical_score',
                   'verbal_score', 'spatial_score', 'mechanical_score')
    list_filter = ('completed_at',)
    search_fields = ('user__username', 'user__email')
    ordering = ('-completed_at',)

@admin.register(UserAssessment)
class UserAssessmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'answer', 'score', 'created_at')
    list_filter = ('created_at', 'question__assessment_type', 'question__category')
    search_fields = ('user__username', 'question__question_text')
    ordering = ('-created_at',)

@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'assessment_type', 'completed_at')
    list_filter = ('assessment_type', 'completed_at')
    search_fields = ('user__username', 'user__email')
    ordering = ('-completed_at',)

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'assessment_type')
        }),
        ('Aptitude Scores', {
            'fields': ('logical_score', 'numerical_score', 'verbal_score',
                      'spatial_score', 'mechanical_score')
        }),
        ('Personality Scores', {
            'fields': ('openness_score', 'conscientiousness_score', 'extraversion_score',
                      'agreeableness_score', 'neuroticism_score')
        })
    )

@admin.register(CareerRecommendation)
class CareerRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'career_path', 'confidence_score', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'career_path')
    ordering = ('-confidence_score', '-created_at')
