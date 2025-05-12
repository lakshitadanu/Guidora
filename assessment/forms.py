from django import forms
from .models import AssessmentQuestion, UserAssessment
from django.db.models import Q

class PersonalityAssessmentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        questions = AssessmentQuestion.objects.filter(assessment_type='personality')
        
        for question in questions:
            field_name = f'question_{question.id}'
            choices = [(str(i), str(i)) for i in range(1, 6)]  # 1-5 scale
            field = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                label=question.question_text,
                required=True,
                help_text='1 - Strongly Disagree, 2 - Disagree, 3 - Neutral, 4 - Agree, 5 - Strongly Agree'
            )
            field.category = question.category
            field.question = question
            self.fields[field_name] = field

class AptitudeAssessmentForm(forms.Form):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        categories = ['logical', 'numerical', 'verbal', 'spatial', 'mechanical']
        
        # Get first 3 questions from each category
        for category in categories:
            category_questions = AssessmentQuestion.objects.filter(
                assessment_type='aptitude',
                category=category
            ).order_by('id')[:3]  # Get first 3 questions per category
            
            for question in category_questions:
                self._add_question_field(question)
    
    def _add_question_field(self, question):
        field_name = f'question_{question.id}'
        choices = [(str(option), str(option)) for option in question.options]
        field = forms.ChoiceField(
            choices=choices,
            widget=forms.RadioSelect,
            label=question.question_text,
            required=True
        )
        field.category = question.category
        field.question = question
        self.fields[field_name] = field 