from django import forms

class ResumeUploadForm(forms.Form):
    resume = forms.FileField(
        label='Upload Resume',
        help_text='Upload your resume in PDF or DOCX format',
        widget=forms.FileInput(attrs={'accept': '.pdf,.docx'})
    )
    target_role = forms.CharField(
        label='Target Job Role (Optional)',
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., Software Engineer, Data Analyst, etc.',
            'class': 'form-control'
        })
    ) 