from django.db import models

# Create your models here.

class College(models.Model):
    CATEGORIES = [
        ('eng', 'Engineering'),
        ('medical', 'Medical'),
        ('dental', 'Dental'),
        ('pharmacy', 'Pharmacy'),
        ('law', 'Law'),
        ('management', 'Management'),
        ('architecture', 'Architecture & Planning'),
    ]

    STATES = [
        ('AN', 'Andaman and Nicobar Islands'),
        ('AP', 'Andhra Pradesh'),
        ('AR', 'Arunachal Pradesh'),
        ('AS', 'Assam'),
        ('BR', 'Bihar'),
        ('CH', 'Chandigarh'),
        ('CT', 'Chhattisgarh'),
        ('DN', 'Dadra and Nagar Haveli'),
        ('DD', 'Daman and Diu'),
        ('DL', 'Delhi'),
        ('GA', 'Goa'),
        ('GJ', 'Gujarat'),
        ('HR', 'Haryana'),
        ('HP', 'Himachal Pradesh'),
        ('JK', 'Jammu and Kashmir'),
        ('JH', 'Jharkhand'),
        ('KA', 'Karnataka'),
        ('KL', 'Kerala'),
        ('LA', 'Ladakh'),
        ('LD', 'Lakshadweep'),
        ('MP', 'Madhya Pradesh'),
        ('MH', 'Maharashtra'),
        ('MN', 'Manipur'),
        ('ML', 'Meghalaya'),
        ('MZ', 'Mizoram'),
        ('NL', 'Nagaland'),
        ('OR', 'Odisha'),
        ('PY', 'Puducherry'),
        ('PB', 'Punjab'),
        ('RJ', 'Rajasthan'),
        ('SK', 'Sikkim'),
        ('TN', 'Tamil Nadu'),
        ('TG', 'Telangana'),
        ('TR', 'Tripura'),
        ('UP', 'Uttar Pradesh'),
        ('UT', 'Uttarakhand'),
        ('WB', 'West Bengal'),
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORIES)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2, choices=STATES)
    ranking = models.IntegerField(null=True, blank=True)
    website = models.URLField(max_length=255, blank=True)
    established = models.IntegerField(null=True, blank=True)
    ownership = models.CharField(max_length=50, blank=True)
    approved_by = models.CharField(max_length=255, blank=True)
    affiliated_to = models.CharField(max_length=255, blank=True)
    facilities = models.TextField(blank=True)
    courses_offered = models.TextField(blank=True)

    class Meta:
        verbose_name = 'College'
        verbose_name_plural = 'Colleges'
        ordering = ['ranking', 'name']

    def __str__(self):
        return f"{self.name} - {self.city}, {self.get_state_display()}"
