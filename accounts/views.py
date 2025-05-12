from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView
from django.views import View
from assessment.models import AssessmentResult, CareerRecommendation
from assessment.career_recommender import CareerRecommender
from .forms import (
    CombinedSchoolStudentForm,
    CombinedCollegeStudentForm,
    UserRegistrationForm,
    SchoolStudentRegistrationForm,
    CollegeStudentRegistrationForm,
    CombinedSchoolStudentUpdateForm,
    CombinedCollegeStudentUpdateForm
)
from .models import User, SchoolStudent, CollegeStudent
from django.contrib.auth.mixins import LoginRequiredMixin

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Welcome back, {self.request.user.full_name}!')
        return response

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')

class SelectCategoryView(TemplateView):
    template_name = 'accounts/select_category.html'

class SchoolStudentRegistrationView(View):
    template_name = 'accounts/register_school.html'

    def get(self, request):
        form = CombinedSchoolStudentForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CombinedSchoolStudentForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, 'Registration successful! Welcome to Guidora.')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'An error occurred during registration: {str(e)}')
        return render(request, self.template_name, {'form': form})

class CollegeStudentRegistrationView(View):
    template_name = 'accounts/register_college.html'

    def get(self, request):
        form = CombinedCollegeStudentForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CombinedCollegeStudentForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, 'Registration successful! Welcome to Guidora.')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'An error occurred during registration: {str(e)}')
        return render(request, self.template_name, {'form': form})

class UserProfileUpdateView(LoginRequiredMixin, View):
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('profile')

    def get_form_class(self):
        if self.request.user.student_type == '12th':
            return CombinedSchoolStudentUpdateForm
        return CombinedCollegeStudentUpdateForm

    def get_form(self, *args, **kwargs):
        form_class = self.get_form_class()
        if 'data' in kwargs:
            return form_class(instance=self.request.user, data=kwargs['data'])
        return form_class(instance=self.request.user)

    def get(self, request):
        form = self.get_form()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.get_form(data=request.POST)
        if form.is_valid():
            try:
                form.save()  # This will save both user and profile data
                messages.success(request, 'Profile updated successfully!')
                return redirect(self.success_url)
            except Exception as e:
                messages.error(request, f'An error occurred while updating your profile: {str(e)}')
        return render(request, self.template_name, {'form': form})

@login_required
def dashboard(request):
    user = request.user
    context = {
        'user': user,
        'student_type': user.get_student_type_display()
    }
    
    # Get assessment completion status
    has_completed_aptitude = AssessmentResult.objects.filter(
        user=user, 
        assessment_type='aptitude'
    ).exists()
    
    has_completed_personality = AssessmentResult.objects.filter(
        user=user, 
        assessment_type='personality'
    ).exists()
    
    context.update({
        'has_completed_aptitude': has_completed_aptitude,
        'has_completed_personality': has_completed_personality
    })
    
    if user.student_type == '12th':
        try:
            profile = user.school_profile
            context.update({
                'profile': profile,
                'stream': profile.get_stream_display(),
                'board': profile.get_board_display()
            })
            
            # Get career recommendations if both assessments are completed
            if has_completed_aptitude and has_completed_personality:
                recommender = CareerRecommender()
                recommendations = recommender.get_recommendations(user)
                if recommendations:
                    context['career_recommendations'] = recommendations
                
        except SchoolStudent.DoesNotExist:
            pass
    else:
        try:
            profile = user.college_profile
            context.update({
                'profile': profile,
                'course': profile.get_course_display(),
                'specialization': profile.get_specialization_display()
            })
        except CollegeStudent.DoesNotExist:
            pass
    
    return render(request, 'accounts/dashboard.html', context) 