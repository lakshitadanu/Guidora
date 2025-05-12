from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User, SchoolStudent, CollegeStudent

class UserRegistrationForm(UserCreationForm):
    """Base form for user registration with common fields"""
    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone_number', 'password1', 'password2',
                 'address', 'city', 'state', 'pincode']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class UserProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile without password fields"""
    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone_number', 'address', 'city', 'state', 'pincode']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class SchoolStudentRegistrationForm(forms.ModelForm):
    """Form for 12th student specific fields"""
    class Meta:
        model = SchoolStudent
        fields = ['school_name', 'board', 'stream', 'tenth_marks', 'twelfth_marks']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes and placeholders
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Add specific placeholders
        self.fields['tenth_marks'].widget.attrs.update({
            'placeholder': 'Enter percentage (e.g., 85.5)',
            'min': '0',
            'max': '100',
            'step': '0.01'
        })
        self.fields['twelfth_marks'].widget.attrs.update({
            'placeholder': 'Enter percentage (e.g., 85.5)',
            'min': '0',
            'max': '100',
            'step': '0.01'
        })

class CollegeStudentRegistrationForm(forms.ModelForm):
    """Form for college student specific fields"""
    class Meta:
        model = CollegeStudent
        fields = ['college_name', 'course', 'specialization', 
                 'college_cgpa', 'graduation_year']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes and placeholders
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Add specific placeholders
        self.fields['college_cgpa'].widget.attrs.update({
            'placeholder': 'Enter CGPA (e.g., 8.5)',
            'min': '0',
            'max': '10',
            'step': '0.01'
        })
        self.fields['graduation_year'].widget.attrs.update({
            'placeholder': 'Expected graduation year (e.g., 2025)',
            'min': '2020',
            'max': '2030'
        })

class CombinedSchoolStudentForm:
    """Helper class to handle both user and school student forms"""
    def __init__(self, data=None, *args, **kwargs):
        self.user_form = UserRegistrationForm(data=data, *args, **kwargs) if data else UserRegistrationForm()
        self.profile_form = SchoolStudentRegistrationForm(data=data, *args, **kwargs) if data else SchoolStudentRegistrationForm()

    def is_valid(self):
        return all([
            self.user_form.is_valid(),
            self.profile_form.is_valid()
        ])

    def save(self, commit=True):
        user = self.user_form.save(commit=False)
        user.student_type = '12th'
        if commit:
            user.save()
            school_profile = self.profile_form.save(commit=False)
            school_profile.user = user
            school_profile.save()
            self.profile_form.save_m2m()  # Save many-to-many data
        return user

    @property
    def errors(self):
        errors = {}
        if self.user_form.errors:
            errors.update(self.user_form.errors)
        if self.profile_form.errors:
            errors.update(self.profile_form.errors)
        return errors

class CombinedCollegeStudentForm:
    """Helper class to handle both user and college student forms"""
    def __init__(self, data=None, *args, **kwargs):
        self.user_form = UserRegistrationForm(data=data, *args, **kwargs) if data else UserRegistrationForm()
        self.profile_form = CollegeStudentRegistrationForm(data=data, *args, **kwargs) if data else CollegeStudentRegistrationForm()

    def is_valid(self):
        return all([
            self.user_form.is_valid(),
            self.profile_form.is_valid()
        ])

    def save(self, commit=True):
        user = self.user_form.save(commit=False)
        user.student_type = 'college'
        if commit:
            user.save()
            college_profile = self.profile_form.save(commit=False)
            college_profile.user = user
            college_profile.save()
            self.profile_form.save_m2m()  # Save many-to-many data
        return user

    @property
    def errors(self):
        errors = {}
        if self.user_form.errors:
            errors.update(self.user_form.errors)
        if self.profile_form.errors:
            errors.update(self.profile_form.errors)
        return errors

class CombinedSchoolStudentUpdateForm:
    """Helper class to handle both user and school student profile updates"""
    def __init__(self, instance=None, data=None, *args, **kwargs):
        self.user_form = UserProfileUpdateForm(instance=instance, data=data, *args, **kwargs) if instance else UserProfileUpdateForm(data=data, *args, **kwargs)
        self.profile_form = SchoolStudentRegistrationForm(instance=instance.school_profile if instance else None, data=data, *args, **kwargs)

    def is_valid(self):
        return all([
            self.user_form.is_valid(),
            self.profile_form.is_valid()
        ])

    def save(self, commit=True):
        user = self.user_form.save(commit=False)
        if commit:
            user.save()
            school_profile = self.profile_form.save(commit=False)
            school_profile.user = user
            school_profile.save()
            self.profile_form.save_m2m()
        return user

    @property
    def errors(self):
        errors = {}
        if self.user_form.errors:
            errors.update(self.user_form.errors)
        if self.profile_form.errors:
            errors.update(self.profile_form.errors)
        return errors

class CombinedCollegeStudentUpdateForm:
    """Helper class to handle both user and college student profile updates"""
    def __init__(self, instance=None, data=None, *args, **kwargs):
        self.user_form = UserProfileUpdateForm(instance=instance, data=data, *args, **kwargs) if instance else UserProfileUpdateForm(data=data, *args, **kwargs)
        self.profile_form = CollegeStudentRegistrationForm(instance=instance.college_profile if instance else None, data=data, *args, **kwargs)

    def is_valid(self):
        return all([
            self.user_form.is_valid(),
            self.profile_form.is_valid()
        ])

    def save(self, commit=True):
        user = self.user_form.save(commit=False)
        if commit:
            user.save()
            college_profile = self.profile_form.save(commit=False)
            college_profile.user = user
            college_profile.save()
            self.profile_form.save_m2m()
        return user

    @property
    def errors(self):
        errors = {}
        if self.user_form.errors:
            errors.update(self.user_form.errors)
        if self.profile_form.errors:
            errors.update(self.profile_form.errors)
        return errors 