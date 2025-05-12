# Resume Analyzer with Skill & Certification Recommendation

A Django-based web application that analyzes resumes and provides personalized career guidance, skill gap analysis, and certification recommendations using Ollama's Mistral model.

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

## Features

- Resume parsing (PDF/DOCX)
- Skill gap analysis
- Certification recommendations
- Career guidance
- Target role-based analysis
- Interactive UI with real-time feedback

## Usage

1. Start Ollama in a separate terminal:
```bash
ollama serve
```

2. Access the application at `http://localhost:8000`
3. Upload your resume and optionally specify a target role
4. View the analysis results with recommendations

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

Feel free to submit issues and enhancement requests! 