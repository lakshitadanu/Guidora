from django.urls import path
from . import views

urlpatterns = [
    path('get-started/', views.SelectCategoryView.as_view(), name='get_started'),
    path('register/school/', views.SchoolStudentRegistrationView.as_view(), name='register_school'),
    path('register/college/', views.CollegeStudentRegistrationView.as_view(), name='register_college'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.UserProfileUpdateView.as_view(), name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
] 