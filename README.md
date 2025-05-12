# Guidora: AI-Powered Career Guidance Platform

Guidora is a comprehensive Django-based web application designed to empower students and professionals with personalized career guidance, skill gap analysis, resume evaluation, and actionable recommendations. Leveraging advanced machine learning models and the Ollama Mistral LLM, Guidora offers an interactive experience with features like a career counseling chatbot, college browsing, and detailed assessments.

## Project Modules & Features

### 1. Resume Analysis & Gap Detection
- **Resume Parsing:** Upload PDF/DOCX resumes for automatic extraction of education, experience, and skills.
- **Skill Gap Analysis:** Identify missing skills for your target role and receive personalized upskilling suggestions.
- **Certification Recommendations:** Get curated online courses and certifications to bridge your skill gaps.

### 2. Career Recommendation Engine
- **ML-Based Career Prediction:** Receive top career path recommendations based on your academic profile, personality, and aptitude assessments using custom-trained ML models.
- **Stream Suitability:** Recommendations are tailored to your academic stream (Science, Commerce, Humanities, etc.).
- **Confidence Scores:** Understand the rationale and confidence behind each career suggestion.

### 3. Assessments
- **Personality Assessment:** Take a Big Five personality test to discover your traits and how they align with various careers.
- **Aptitude Assessment:** Evaluate your logical, numerical, verbal, spatial, and mechanical reasoning skills.
- **Integrated Recommendations:** Assessment results directly inform your career and skill recommendations.

### 4. AI Career Counseling Chatbot
- **Conversational Guidance:** Chat with an AI-powered counselor trained on Indian education and job market norms.
- **Real-Time Q&A:** Get instant answers about career paths, entrance exams, scholarships, and more.
- **Personalized Advice:** The chatbot adapts its responses based on your profile and assessment results.

### 5. College & Course Browser
- **College Search:** Browse and filter Indian colleges by category, state, ranking etc .
- **Detailed Profiles:** View comprehensive information about each college, including programs, rankings, and admission criteria.

### 6. User Accounts & History
- **Profile Management:** Secure user registration, login, and profile editing.


## Technology Stack
- **Backend:** Django, PostgreSQL, Python
- **AI/ML:** Custom ML models (joblib/pickle), Ollama Mistral LLM (local API)
- **Frontend:** Django Templates, HTML/CSS/JS

## Prerequisites

1. Python 3.8 or higher
2. PostgreSQL
3. Ollama (for running Mistral model locally)

## Setup Instructions

### 1. Install Ollama

#### Windows:
1. Download Ollama from [https://ollama.ai/download](https://ollama.ai/download)
2. Run the installer
3. Open PowerShell and run:
```powershell
ollama pull mistral
```

#### Linux:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull mistral
```

#### macOS:
```bash
brew install ollama
ollama pull mistral
```

### 2. Set up the Python Environment

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
.\venv\Scripts\activate
```
- Linux/macOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configure the Database

1. Create a PostgreSQL database
2. Update the database settings in `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Start the Development Server

```bash
python manage.py runserver
```

## Usage

1. Start Ollama in a separate terminal:
```bash
ollama serve
```

2. Access the application at `http://localhost:8000`
3. Register or log in to your account
4. Upload your resume, take assessments, chat with the AI counselor, and explore colleges
5. View your personalized analysis, recommendations, and history

## Troubleshooting

1. If Ollama is not responding:
   - Ensure Ollama is running (`ollama serve`)
   - Check if Mistral model is downloaded (`ollama list`)
   - Verify the API endpoint in `views.py` matches your Ollama setup

2. If resume parsing fails:
   - Ensure the file is in PDF or DOCX format
   - Check file permissions
   - Verify all Python dependencies are installed

## Contributing

We welcome contributions! Please submit issues, feature requests, or pull requests to help improve Guidora. 