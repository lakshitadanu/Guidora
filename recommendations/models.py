from django.db import models
from accounts.models import User

class CareerPath(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    required_skills = models.TextField()
    average_salary = models.CharField(max_length=100)
    growth_prospects = models.TextField()
    education_requirements = models.TextField()
    stream_suitability = models.JSONField()  # Stores which streams this career is suitable for

    def __str__(self):
        return self.name

class Institute(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    type = models.CharField(max_length=100)  # University, College, etc.
    website = models.URLField()
    description = models.TextField()
    courses_offered = models.TextField()
    admission_process = models.TextField()
    ranking = models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='institutes/', null=True, blank=True)

    def __str__(self):
        return self.name

class UserRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    career_path1 = models.ForeignKey(CareerPath, on_delete=models.CASCADE, related_name='first_recommendation')
    career_path2 = models.ForeignKey(CareerPath, on_delete=models.CASCADE, related_name='second_recommendation')
    career_path3 = models.ForeignKey(CareerPath, on_delete=models.CASCADE, related_name='third_recommendation')
    generated_at = models.DateTimeField(auto_now_add=True)
    confidence_scores = models.JSONField()  # Stores confidence scores for each recommendation

    def __str__(self):
        return f"Recommendations for {self.user.username}"
