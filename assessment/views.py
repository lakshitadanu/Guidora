from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PersonalityAssessmentForm, AptitudeAssessmentForm
from .models import PersonalityAssessment, AptitudeAssessment, AssessmentQuestion, UserAssessment, AssessmentResult, CareerRecommendation
import numpy as np
import pickle
import os
import joblib
from django.db.models import Avg
from collections import defaultdict
from django.http import JsonResponse
from .career_recommender import CareerRecommender
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

# Ollama API endpoint
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# System prompt to make the chatbot act like an Indian career counselor
SYSTEM_PROMPT = """You are an experienced Indian career counselor with deep knowledge of the Indian education system and job market. 
Your role is to guide students in making informed career decisions. You should:

1. Understand Indian education streams (Science, Commerce, Arts) and their career paths
2. Be familiar with Indian entrance exams (JEE, NEET, CLAT, etc.) and their cutoffs
3. Know about Indian colleges, universities, and their rankings
4. Consider Indian job market trends and opportunities
5. Be empathetic and encouraging while providing realistic advice
6. Ask follow-up questions to better understand the student's situation
7. Provide specific examples and actionable steps
8. Use simple, clear language suitable for students

Remember to:
- Be culturally sensitive to Indian education and career norms
- Consider financial aspects and family expectations
- Suggest both traditional and emerging career options
- Provide guidance on entrance exams and preparation strategies
- Mention scholarship opportunities when relevant
"""

# Create your views here.

@login_required
def personality_assessment(request):
    # Check if already completed
    if AssessmentResult.objects.filter(user=request.user, assessment_type='personality').exists():
        messages.warning(request, 'You have already completed the personality assessment.')
        return redirect('assessment:assessment_list')

    if request.method == 'POST':
        form = PersonalityAssessmentForm(request.POST)
        if form.is_valid():
            # Initialize scores for each trait
            trait_scores = defaultdict(list)
            
            # Process each question response
            for field_name, answer in form.cleaned_data.items():
                question_id = int(field_name.split('_')[1])
                question = AssessmentQuestion.objects.get(id=question_id)
                
                # Save user's response
                UserAssessment.objects.create(
                    user=request.user,
                    question=question,
                    answer=answer,
                    score=float(answer)  # For personality, score is the same as answer (1-5)
                )
                
                # Add score to appropriate trait
                trait_scores[question.category].append(float(answer))
            
            # Calculate average scores for each trait
            result = AssessmentResult(user=request.user, assessment_type='personality')
            for trait, scores in trait_scores.items():
                avg_score = sum(scores) / len(scores)
                # Convert to 0-100 scale
                normalized_score = (avg_score - 1) * 25  # Converts 1-5 to 0-100
                setattr(result, f'{trait}_score', normalized_score)
            
            result.save()
            
            messages.success(request, 'Personality assessment completed successfully!')
            return redirect('assessment:assessment_list')
    else:
        form = PersonalityAssessmentForm()

    # Calculate progress
    total_questions = len(form.fields)
    answered_questions = sum(1 for field in form if field.value())
    progress = int((answered_questions / total_questions) * 100) if total_questions > 0 else 0
    
    return render(request, 'assessment/personality_assessment.html', {
        'form': form,
        'progress': progress
    })

@login_required
def aptitude_assessment(request):
    # Check if already completed
    if AssessmentResult.objects.filter(user=request.user, assessment_type='aptitude').exists():
        messages.warning(request, 'You have already completed the aptitude assessment.')
        return redirect('assessment:assessment_list')

    if request.method == 'POST':
        form = AptitudeAssessmentForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                # Initialize scores for each category
                category_scores = defaultdict(list)
                
                # Process each question response
                for field_name, answer in form.cleaned_data.items():
                    question_id = int(field_name.split('_')[1])
                    question = AssessmentQuestion.objects.get(id=question_id)
                    
                    # Calculate score (1 if correct, 0 if incorrect)
                    score = 1.0 if str(answer) == str(question.correct_answer) else 0.0
                    
                    # Save user's response
                    UserAssessment.objects.create(
                        user=request.user,
                        question=question,
                        answer=answer,
                        score=score
                    )
                    
                    # Add score to appropriate category
                    category_scores[question.category].append(score)
                
                # Calculate average scores for each category
                result = AssessmentResult(user=request.user, assessment_type='aptitude')
                for category, scores in category_scores.items():
                    avg_score = (sum(scores) / len(scores)) * 100  # Convert to percentage
                    setattr(result, f'{category}_score', avg_score)
                
                result.save()
                
                messages.success(request, 'Aptitude assessment completed successfully!')
                return redirect('assessment:assessment_list')
            except Exception as e:
                messages.error(request, f'An error occurred while saving your assessment: {str(e)}')
                # Log the error for debugging
                print(f"Error in aptitude_assessment: {str(e)}")
    else:
        form = AptitudeAssessmentForm(user=request.user)

    # Calculate progress
    total_questions = len(form.fields)
    answered_questions = sum(1 for field in form if field.value())
    progress = int((answered_questions / total_questions) * 100) if total_questions > 0 else 0
    
    return render(request, 'assessment/aptitude_assessment.html', {
        'form': form,
        'progress': progress,
        'time_limit': 30  # 30 minutes time limit
    })

@login_required
def get_recommendations(request):
    # Get user's latest assessment results
    personality = PersonalityAssessment.objects.filter(user=request.user).latest('completed_at')
    aptitude = AptitudeAssessment.objects.filter(user=request.user).latest('completed_at')
    
    # Prepare input data for the model
    input_data = {
        'stream': request.user.stream,
        'twelfth_marks': float(request.user.twelfth_marks),
        'openness': float(personality.openness_score),
        'conscientiousness': float(personality.conscientiousness_score),
        'extraversion': float(personality.extraversion_score),
        'agreeableness': float(personality.agreeableness_score),
        'neuroticism': float(personality.neuroticism_score),
        'logical': float(aptitude.logical_score),
        'numerical': float(aptitude.numerical_score),
        'verbal': float(aptitude.verbal_score),
        'spatial': float(aptitude.spatial_score),
        'mechanical': float(aptitude.mechanical_score)
    }
    
    # Load the trained model
    model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'indian_career_recommendations.pkl')
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    # Get recommendations
    recommendations = model.predict([list(input_data.values())])
    
    context = {
        'recommendations': recommendations[0],  # Top 3 career paths
        'confidence_scores': model.predict_proba([list(input_data.values())])[0]
    }
    
    return render(request, 'assessment/recommendations.html', context)

@login_required
def assessment_list(request):
    # Check if user has completed assessments
    personality_completed = AssessmentResult.objects.filter(
        user=request.user, 
        assessment_type='personality'
    ).exists()
    
    aptitude_completed = AssessmentResult.objects.filter(
        user=request.user, 
        assessment_type='aptitude'
    ).exists()
    
    context = {
        'assessments': [
            {
                'title': 'Personality Assessment',
                'description': 'Discover your personality traits and how they align with different career paths.',
                'url': 'personality_assessment',
                'icon': 'fas fa-brain',
                'completed': personality_completed
            },
            {
                'title': 'Aptitude Assessment',
                'description': 'Test your skills and abilities to find careers that match your strengths.',
                'url': 'aptitude_assessment',
                'icon': 'fas fa-puzzle-piece',
                'completed': aptitude_completed
            }
        ]
    }
    return render(request, 'assessment/assessment_list.html', context)

@login_required
def start_assessment(request, assessment_type):
    # Check if assessment already completed
    if AssessmentResult.objects.filter(user=request.user, assessment_type=assessment_type).exists():
        messages.warning(request, f'You have already completed the {assessment_type} assessment.')
        return redirect('assessment_list')
    
    questions = AssessmentQuestion.objects.filter(assessment_type=assessment_type)
    context = {
        'assessment_type': assessment_type,
        'questions': questions,
    }
    return render(request, 'assessment/take_assessment.html', context)

@login_required
def submit_assessment(request, assessment_type):
    if request.method != 'POST':
        return redirect('assessment_list')
    
    questions = AssessmentQuestion.objects.filter(assessment_type=assessment_type)
    
    # Save user responses and calculate scores
    for question in questions:
        answer = request.POST.get(f'question_{question.id}')
        if answer:
            score = 1.0 if assessment_type == 'aptitude' and answer == question.correct_answer else 0.0
            UserAssessment.objects.create(
                user=request.user,
                question=question,
                answer=answer,
                score=score
            )
    
    # Calculate category scores
    result = AssessmentResult(user=request.user, assessment_type=assessment_type)
    
    if assessment_type == 'aptitude':
        for category in ['logical', 'numerical', 'verbal', 'spatial', 'mechanical']:
            category_score = UserAssessment.objects.filter(
                user=request.user,
                question__assessment_type='aptitude',
                question__category=category
            ).aggregate(Avg('score'))['score__avg'] * 100
            setattr(result, f'{category}_score', category_score)
    
    else:  # personality assessment
        for category in ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
            responses = UserAssessment.objects.filter(
                user=request.user,
                question__assessment_type='personality',
                question__category=category
            )
            # Calculate personality score based on responses
            category_score = calculate_personality_score(responses)
            setattr(result, f'{category}_score', category_score)
    
    result.save()
    
    # If both assessments are completed, generate career recommendations
    if AssessmentResult.objects.filter(user=request.user).count() == 2:
        generate_career_recommendations(request.user)
    
    messages.success(request, f'Successfully completed the {assessment_type} assessment!')
    return redirect('assessment_list')

def calculate_personality_score(responses):
    # Convert Likert scale responses to scores (1-5 scale)
    total_score = sum(int(response.answer) for response in responses)
    max_possible = len(responses) * 5
    return (total_score / max_possible) * 100

def generate_career_recommendations(user):
    # Load the trained model
    model = joblib.load('indian_career_recommendations.pkl')
    
    # Get user's academic details
    stream = user.stream
    marks_12th = float(user.twelfth_marks or 0)
    
    # Get assessment results
    aptitude_result = AssessmentResult.objects.get(user=user, assessment_type='aptitude')
    personality_result = AssessmentResult.objects.get(user=user, assessment_type='personality')
    
    # Prepare input features for the model
    features = np.array([
        marks_12th,
        aptitude_result.logical_score,
        aptitude_result.numerical_score,
        aptitude_result.verbal_score,
        aptitude_result.spatial_score,
        aptitude_result.mechanical_score,
        personality_result.openness_score,
        personality_result.conscientiousness_score,
        personality_result.extraversion_score,
        personality_result.agreeableness_score,
        personality_result.neuroticism_score
    ])
    
    # Get stream encoding (you'll need to match this with your model's training data)
    stream_encoding = encode_stream(stream)
    features = np.concatenate([features, stream_encoding])
    
    # Get predictions
    predictions = model.predict_proba(features.reshape(1, -1))
    top_3_indices = np.argsort(predictions[0])[-3:][::-1]
    
    # Save recommendations
    CareerRecommendation.objects.filter(user=user).delete()  # Remove old recommendations
    for idx in top_3_indices:
        career_path = decode_career_path(idx)  # You'll need to implement this based on your model
        confidence = predictions[0][idx] * 100
        CareerRecommendation.objects.create(
            user=user,
            career_path=career_path,
            confidence_score=confidence
        )

def encode_stream(stream):
    # Implement stream encoding based on your model's training data
    # This is a placeholder - adjust based on your actual encoding scheme
    encoding_map = {
        'pcm': [1, 0, 0, 0],
        'pcb': [0, 1, 0, 0],
        'commerce': [0, 0, 1, 0],
        'humanities': [0, 0, 0, 1]
    }
    return np.array(encoding_map.get(stream, [0, 0, 0, 0]))

def decode_career_path(index):
    # Implement career path decoding based on your model's training data
    # This is a placeholder - adjust based on your actual career paths
    career_paths = [
        "Software Engineer",
        "Data Scientist",
        "Doctor",
        "Financial Analyst",
        "Teacher",
        # Add more career paths based on your model
    ]
    return career_paths[index]

@login_required
def get_career_recommendations(request):
    # Check if both assessments are completed
    personality_result = AssessmentResult.objects.filter(
        user=request.user,
        assessment_type='personality'
    ).first()
    
    aptitude_result = AssessmentResult.objects.filter(
        user=request.user,
        assessment_type='aptitude'
    ).first()
    
    if not personality_result or not aptitude_result:
        messages.warning(request, 'Please complete both assessments to get career recommendations.')
        return redirect('assessment_list')
    
    try:
        # Get user's academic details
        stream = request.user.stream
        twelfth_marks = float(request.user.twelfth_marks)
        
        # Prepare input features for the model
        features = [
            twelfth_marks,
            aptitude_result.logical_score,
            aptitude_result.numerical_score,
            aptitude_result.verbal_score,
            aptitude_result.spatial_score,
            aptitude_result.mechanical_score,
            personality_result.openness_score,
            personality_result.conscientiousness_score,
            personality_result.extraversion_score,
            personality_result.agreeableness_score,
            personality_result.neuroticism_score
        ]
        
        # Add stream encoding
        stream_encoding = encode_stream(stream)
        features.extend(stream_encoding)
        
        # Load the model
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'indian_career_recommendations.pkl')
        model = joblib.load(model_path)
        
        # Get predictions and probabilities
        features_array = np.array(features).reshape(1, -1)
        probabilities = model.predict_proba(features_array)[0]
        
        # Get top 3 career paths
        top_3_indices = np.argsort(probabilities)[-3:][::-1]
        
        # Save recommendations
        CareerRecommendation.objects.filter(user=request.user).delete()  # Remove old recommendations
        recommendations = []
        
        for idx in top_3_indices:
            career_path = decode_career_path(idx)
            confidence = probabilities[idx] * 100
            recommendation = CareerRecommendation.objects.create(
                user=request.user,
                career_path=career_path,
                confidence_score=confidence
            )
            recommendations.append({
                'career_path': career_path,
                'confidence': confidence,
                'description': get_career_description(career_path),
                'skills_needed': get_required_skills(career_path)
            })
        
        # Prepare context with assessment scores
        context = {
            'recommendations': recommendations,
            'personality_scores': {
                'Openness': personality_result.openness_score,
                'Conscientiousness': personality_result.conscientiousness_score,
                'Extraversion': personality_result.extraversion_score,
                'Agreeableness': personality_result.agreeableness_score,
                'Neuroticism': personality_result.neuroticism_score
            },
            'aptitude_scores': {
                'Logical': aptitude_result.logical_score,
                'Numerical': aptitude_result.numerical_score,
                'Verbal': aptitude_result.verbal_score,
                'Spatial': aptitude_result.spatial_score,
                'Mechanical': aptitude_result.mechanical_score
            },
            'academic_info': {
                'stream': stream.upper(),
                'twelfth_marks': twelfth_marks
            }
        }
        
        return render(request, 'assessment/recommendations.html', context)
        
    except Exception as e:
        messages.error(request, f'Error generating recommendations: {str(e)}')
        return redirect('assessment_list')

def encode_stream(stream):
    """Encode the academic stream into one-hot encoding"""
    stream_mapping = {
        'pcm': [1, 0, 0, 0],
        'pcb': [0, 1, 0, 0],
        'commerce': [0, 0, 1, 0],
        'humanities': [0, 0, 0, 1]
    }
    return stream_mapping.get(stream.lower(), [0, 0, 0, 0])

def decode_career_path(index):
    """Map model output index to career path"""
    career_paths = [
        "Software Engineer",
        "Data Scientist",
        "Medical Professional",
        "Financial Analyst",
        "Business Consultant",
        "Research Scientist",
        "Digital Marketing Specialist",
        "Product Manager",
        "UX/UI Designer",
        "Systems Architect",
        "Biotechnology Researcher",
        "Investment Banker",
        "Management Consultant",
        "Clinical Psychologist",
        "Environmental Scientist"
    ]
    return career_paths[index] if index < len(career_paths) else "Other"

def get_career_description(career_path):
    """Get detailed description for each career path"""
    descriptions = {
        "Software Engineer": "Develops software applications and systems, working with various programming languages and technologies.",
        "Data Scientist": "Analyzes complex data sets to help guide business decisions using statistics and machine learning.",
        "Medical Professional": "Provides healthcare services, diagnoses and treats illnesses, and promotes public health.",
        "Financial Analyst": "Evaluates financial data to guide investment decisions and provide business insights.",
        "Business Consultant": "Helps organizations improve performance through business strategy and operations analysis.",
        "Research Scientist": "Conducts research to advance knowledge in specific scientific fields.",
        "Digital Marketing Specialist": "Creates and implements online marketing strategies across various digital platforms.",
        "Product Manager": "Oversees product development from conception to launch, balancing business needs with user requirements.",
        "UX/UI Designer": "Designs user interfaces and experiences for digital products and services.",
        "Systems Architect": "Designs and oversees implementation of complex IT systems and infrastructure.",
        "Biotechnology Researcher": "Develops new products and processes using biological systems and organisms.",
        "Investment Banker": "Provides financial services and advice for corporate transactions and investments.",
        "Management Consultant": "Advises organizations on strategy, structure, and operational improvements.",
        "Clinical Psychologist": "Assesses and treats mental, emotional, and behavioral disorders.",
        "Environmental Scientist": "Studies environmental problems and develops solutions to protect the environment."
    }
    return descriptions.get(career_path, "A professional career path with opportunities for growth and development.")

def get_required_skills(career_path):
    """Get key skills required for each career path"""
    skills = {
        "Software Engineer": ["Programming", "Problem Solving", "Software Design", "Debugging", "Team Collaboration"],
        "Data Scientist": ["Statistics", "Machine Learning", "Python/R", "Data Visualization", "SQL"],
        "Medical Professional": ["Clinical Knowledge", "Patient Care", "Diagnostic Skills", "Communication", "Decision Making"],
        "Financial Analyst": ["Financial Modeling", "Excel", "Data Analysis", "Research", "Report Writing"],
        "Business Consultant": ["Strategic Thinking", "Problem Solving", "Communication", "Project Management", "Analysis"],
        "Research Scientist": ["Research Methods", "Data Analysis", "Technical Writing", "Lab Skills", "Critical Thinking"],
        "Digital Marketing Specialist": ["SEO", "Social Media", "Content Creation", "Analytics", "Campaign Management"],
        "Product Manager": ["Product Strategy", "User Research", "Agile Methods", "Communication", "Leadership"],
        "UX/UI Designer": ["User Research", "Design Tools", "Wireframing", "Prototyping", "Visual Design"],
        "Systems Architect": ["System Design", "Technical Leadership", "Cloud Platforms", "Security", "Integration"],
        "Biotechnology Researcher": ["Lab Techniques", "Research", "Data Analysis", "Documentation", "Project Management"],
        "Investment Banker": ["Financial Analysis", "Valuation", "Modeling", "Negotiation", "Client Relations"],
        "Management Consultant": ["Business Analysis", "Strategy", "Problem Solving", "Communication", "Project Management"],
        "Clinical Psychologist": ["Assessment", "Therapy Skills", "Communication", "Ethics", "Research"],
        "Environmental Scientist": ["Research", "Data Analysis", "Field Work", "Report Writing", "Environmental Laws"]
    }
    return skills.get(career_path, ["Analytical Skills", "Communication", "Problem Solving", "Teamwork", "Adaptability"])

@login_required
def generate_recommendations(request):
    """Generate career recommendations for the user."""
    # Check if both assessments are completed
    has_completed_aptitude = AssessmentResult.objects.filter(
        user=request.user, 
        assessment_type='aptitude'
    ).exists()
    
    has_completed_personality = AssessmentResult.objects.filter(
        user=request.user, 
        assessment_type='personality'
    ).exists()
    
    if not (has_completed_aptitude and has_completed_personality):
        messages.error(request, 'Please complete both assessments before generating recommendations.')
        return redirect('dashboard')
    
    # Generate recommendations
    recommender = CareerRecommender()
    recommendations = recommender.get_recommendations(request.user)
    
    if recommendations:
        messages.success(request, 'Career recommendations have been generated successfully!')
    else:
        messages.error(request, 'Unable to generate recommendations. Please ensure your profile is complete.')
    
    return redirect('dashboard')

@login_required
def retake_assessment(request, assessment_type):
    """Allow user to retake an assessment."""
    if assessment_type not in ['aptitude', 'personality']:
        messages.error(request, 'Invalid assessment type.')
        return redirect('dashboard')
    
    # Delete previous assessment results
    AssessmentResult.objects.filter(
        user=request.user,
        assessment_type=assessment_type
    ).delete()
    
    # Delete previous user answers
    UserAssessment.objects.filter(
        user=request.user,
        question__assessment_type=assessment_type
    ).delete()
    
    # Delete career recommendations as they'll need to be regenerated
    CareerRecommendation.objects.filter(user=request.user).delete()
    
    messages.info(request, f'You can now retake the {assessment_type} assessment.')
    
    if assessment_type == 'aptitude':
        return redirect('assessment:aptitude_assessment')
    else:
        return redirect('assessment:personality_assessment')
