from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User

class PersonalityAssessment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    openness_score = models.DecimalField(max_digits=5, decimal_places=2)
    conscientiousness_score = models.DecimalField(max_digits=5, decimal_places=2)
    extraversion_score = models.DecimalField(max_digits=5, decimal_places=2)
    agreeableness_score = models.DecimalField(max_digits=5, decimal_places=2)
    neuroticism_score = models.DecimalField(max_digits=5, decimal_places=2)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Personality Assessment - {self.user.username}"

class AptitudeAssessment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    logical_score = models.DecimalField(max_digits=5, decimal_places=2)
    numerical_score = models.DecimalField(max_digits=5, decimal_places=2)
    verbal_score = models.DecimalField(max_digits=5, decimal_places=2)
    spatial_score = models.DecimalField(max_digits=5, decimal_places=2)
    mechanical_score = models.DecimalField(max_digits=5, decimal_places=2)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Aptitude Assessment - {self.user.username}"

class AssessmentQuestion(models.Model):
    ASSESSMENT_TYPES = [
        ('aptitude', 'Aptitude'),
        ('personality', 'Personality')
    ]
    
    APTITUDE_CATEGORIES = [
        ('logical', 'Logical'),
        ('numerical', 'Numerical'),
        ('verbal', 'Verbal'),
        ('spatial', 'Spatial'),
        ('mechanical', 'Mechanical')
    ]
    
    PERSONALITY_CATEGORIES = [
        ('openness', 'Openness'),
        ('conscientiousness', 'Conscientiousness'),
        ('extraversion', 'Extraversion'),
        ('agreeableness', 'Agreeableness'),
        ('neuroticism', 'Neuroticism')
    ]
    
    question_text = models.TextField()
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES, default='aptitude')
    category = models.CharField(max_length=20)
    options = models.JSONField(default=list)
    correct_answer = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.assessment_type} - {self.category}: {self.question_text[:50]}"

class UserAssessment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)
    score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'question']

class AssessmentResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assessment_type = models.CharField(max_length=20, choices=AssessmentQuestion.ASSESSMENT_TYPES)
    
    # Aptitude scores
    logical_score = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    numerical_score = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    verbal_score = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    spatial_score = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    mechanical_score = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Personality scores
    openness_score = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    conscientiousness_score = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    extraversion_score = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    agreeableness_score = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    neuroticism_score = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'assessment_type']

class CareerRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    career_path = models.CharField(max_length=100)
    confidence_score = models.FloatField()
    recommended_courses = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.career_path} ({self.confidence_score}%)"

    class Meta:
        ordering = ['-confidence_score']
