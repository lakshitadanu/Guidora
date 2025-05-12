from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Base user model with common fields"""
    username = None
    STUDENT_TYPE_CHOICES = [
        ('12th', '12th Student'),
        ('college', 'College Student'),
    ]
    
    # Common fields
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100, default='')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    student_type = models.CharField(max_length=10, choices=STUDENT_TYPE_CHOICES, default='12th')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    # Progress tracking
    career_percentage = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )
    personality_percentage = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )
    skills_percentage = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )

    def __str__(self):
        return self.email

class SchoolStudent(models.Model):
    """Model for 12th standard students"""
    STREAM_CHOICES = [
        ('pcm', 'Science (PCM)'),
        ('pcb', 'Science (PCB)'),
        ('commerce', 'Commerce'),
        ('humanities', 'Humanities'),
    ]
    
    BOARD_CHOICES = [
        ('cbse', 'CBSE'),
        ('icse', 'ICSE'),
        ('state', 'State Board'),
        ('nios', 'NIOS'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='school_profile')
    school_name = models.CharField(max_length=200)
    board = models.CharField(max_length=10, choices=BOARD_CHOICES)
    stream = models.CharField(max_length=20, choices=STREAM_CHOICES)
    
    # Academic details
    tenth_marks = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Enter percentage between 0 and 100"
    )
    twelfth_marks = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Enter percentage between 0 and 100"
    )

    def __str__(self):
        return f"{self.user.full_name} - {self.get_stream_display()}"

    class Meta:
        verbose_name = "School Student Profile"
        verbose_name_plural = "School Student Profiles"

class CollegeStudent(models.Model):
    """Model for college students"""
    COLLEGE_COURSE_CHOICES = [
        ('btech', 'B.Tech'),
        ('be', 'B.E'),
        ('bsc', 'B.Sc'),
        ('bcom', 'B.Com'),
        ('ba', 'B.A'),
        ('bba', 'BBA'),
        ('mbbs', 'MBBS'),
        ('other', 'Other'),
    ]
    
    SPECIALIZATION_CHOICES = [
        ('cs', 'Computer Science'),
        ('it', 'Information Technology'),
        ('mech', 'Mechanical Engineering'),
        ('civil', 'Civil Engineering'),
        ('electrical', 'Electrical Engineering'),
        ('electronics', 'Electronics Engineering'),
        ('chemical', 'Chemical Engineering'),
        ('biotech', 'Biotechnology'),
        ('physics', 'Physics'),
        ('chemistry', 'Chemistry'),
        ('mathematics', 'Mathematics'),
        ('economics', 'Economics'),
        ('finance', 'Finance'),
        ('marketing', 'Marketing'),
        ('hr', 'Human Resources'),
        ('psychology', 'Psychology'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='college_profile')
    college_name = models.CharField(max_length=200)
    course = models.CharField(max_length=20, choices=COLLEGE_COURSE_CHOICES)
    specialization = models.CharField(max_length=20, choices=SPECIALIZATION_CHOICES)
    
    # Academic details
    college_cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Enter CGPA between 0 and 10"
    )
    graduation_year = models.IntegerField(
        validators=[MinValueValidator(2020), MaxValueValidator(2030)],
        help_text="Expected year of graduation"
    )

    def __str__(self):
        return f"{self.user.full_name} - {self.get_course_display()} ({self.get_specialization_display()})"

    class Meta:
        verbose_name = "College Student Profile"
        verbose_name_plural = "College Student Profiles" 