from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator

class Resume(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to='resumes/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'])]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    analyzed = models.BooleanField(default=False)

class ResumeAnalysis(models.Model):
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE)
    skills = models.JSONField(default=dict)
    education = models.JSONField(default=dict)
    experience = models.JSONField(default=dict)
    recommendations = models.JSONField(default=dict)
    ats_score = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analysis for {self.resume.user.username}'s resume"
