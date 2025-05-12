from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import Resume, ResumeAnalysis
from .forms import ResumeUploadForm
from .utils import analyze_resume, extract_name, extract_education, extract_experience, extract_skills, extract_skills_from_dict
import os
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .parser import ResumeParser
import requests
import json
import traceback
from django.utils.decorators import method_decorator
from django.views import View

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def get_analysis_prompt(resume_data: dict, target_role: str = None) -> str:
    # Get up to 3 skills (flattened)
    skills = []
    for skill_list in resume_data.get('skills', {}).values():
        skills.extend(skill_list)
    skills = skills[:3]
    base_prompt = (
        "You are an expert career coach. "
        "Given the following skills from a candidate's resume, "
        "identify 3 skill gaps for their target role, "
        "recommend 2-3 new skills to learn, and suggest 2 certifications or online courses (with links). "
        "Be concise and use bullet points.\n\n"
        f"Skills: {', '.join(skills)}\n"
    )
    if target_role:
        base_prompt += f"Target Role: {target_role}\n"
    else:
        base_prompt += "If no target role is specified, infer the most likely job role from the resume.\n"
    print(f"Prompt length: {len(base_prompt)} characters")
    print("Prompt being sent to Ollama:\n", base_prompt)
    return base_prompt

def extract_resume_info(file_path):
    """Extract resume info using robust regex/heuristics, separate from LLM logic."""
    # Extract text
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext == '.pdf':
        from .parser import ResumeParser
        text = ResumeParser()._extract_text_from_pdf(file_path)
    elif file_ext == '.docx':
        from .parser import ResumeParser
        text = ResumeParser()._extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")
    # Extract info
    from .parser import ResumeParser
    skills_dict = ResumeParser().common_skills
    return {
        'name': extract_name(text),
        'education': extract_education(text),
        'experience': extract_experience(text),
        'skills': extract_skills_from_dict(text, skills_dict),
    }

def stream_ollama_response(prompt, resume_data, resume_info=None):
    # First, yield the resume info as JSON (for separate display)
    if resume_info:
        yield json.dumps({"resume_info": resume_info}) + "\n"
    # Then, yield the resume_data as JSON (for legacy display)
    yield json.dumps({"resume_data": resume_data}) + "\n"
    # Then, stream the LLM response as before
    url = OLLAMA_API_URL
    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": True
    }
    try:
        response = requests.post(url, json=payload, stream=True, timeout=180)
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    chunk = data.get('response', '')
                    if chunk:
                        yield chunk
                except Exception:
                    continue
    except Exception as e:
        yield f"Error: {str(e)}"

# Create your views here.

@login_required
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume_file = request.FILES['resume']
            target_role = form.cleaned_data.get('target_role')
            
            # Save the file temporarily
            file_path = os.path.join(settings.MEDIA_ROOT, 'resumes', resume_file.name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'wb+') as destination:
                for chunk in resume_file.chunks():
                    destination.write(chunk)
            
            try:
                # Parse resume
                print("Received POST request")
                print("Form is valid")
                print("File saved to:", file_path)
                print("Parsing resume...")
                parser = ResumeParser()
                resume_data = parser.parse_resume(file_path)
                print("Resume parsed:", resume_data)
                print("Sending prompt to Ollama...")
                prompt = get_analysis_prompt(resume_data, target_role)
                print("Waiting for Ollama response...")
                response = requests.post(
                    OLLAMA_API_URL,
                    json={
                        "model": "mistral",
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=60
                )
                print("Ollama response status:", response.status_code)
                print("Ollama raw response:", response.text)
                
                if response.status_code == 200:
                    analysis = response.json().get('response', '')
                    
                    # Clean up temporary file
                    os.remove(file_path)
                    
                    return JsonResponse({
                        'status': 'success',
                        'analysis': analysis,
                        'resume_data': resume_data
                    })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Failed to analyze resume'
                    }, status=500)
                    
            except Exception as e:
                traceback.print_exc()  # Print the full error in your terminal
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=500)
    
    else:
        form = ResumeUploadForm()
    
    return render(request, 'resume_analysis/upload.html', {'form': form})

@login_required
def analysis_result(request, resume_id):
    try:
        resume = Resume.objects.get(id=resume_id, user=request.user)
        analysis = ResumeAnalysis.objects.get(resume=resume)
        return render(request, 'resume_analysis/result.html', {
            'resume': resume,
            'analysis': analysis
        })
    except (Resume.DoesNotExist, ResumeAnalysis.DoesNotExist):
        messages.error(request, 'Resume analysis not found.')
        return redirect('resume_analysis:upload_resume')

@method_decorator(csrf_exempt, name='dispatch')
class StreamAnalysisView(View):
    def post(self, request):
        try:
            form = ResumeUploadForm(request.POST, request.FILES)
            if not form.is_valid():
                return StreamingHttpResponse("Error: Invalid form data", content_type='text/plain')
                
            resume_file = request.FILES['resume']
            target_role = form.cleaned_data.get('target_role')
            
            # Save the file temporarily
            file_path = os.path.join(settings.MEDIA_ROOT, 'resumes', resume_file.name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            try:
                with open(file_path, 'wb+') as destination:
                    for chunk in resume_file.chunks():
                        destination.write(chunk)
                
                # Parse resume (for LLM)
                parser = ResumeParser()
                resume_data = parser.parse_resume(file_path)
                # Extract resume info (robust, for display)
                resume_info = extract_resume_info(file_path)
                # Generate prompt
                prompt = get_analysis_prompt(resume_data, target_role)
                # Return streaming response (resume_info, resume_data, then LLM)
                response = StreamingHttpResponse(
                    stream_ollama_response(prompt, resume_data, resume_info),
                    content_type='text/plain'
                )
                # Clean up temporary file AFTER response is created
                try:
                    os.remove(file_path)
                except Exception as cleanup_err:
                    print(f"Warning: Could not delete file {file_path}: {cleanup_err}")
                return response
                
            except Exception as e:
                print(f"Error processing file: {e}")
                return StreamingHttpResponse(f"Error processing file: {str(e)}", content_type='text/plain')
                
        except Exception as e:
            print(f"Unexpected error: {e}")
            return StreamingHttpResponse(f"Error: {str(e)}", content_type='text/plain')

@csrf_exempt
@require_POST
def chat_with_mistral(request):
    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        if not question:
            return StreamingHttpResponse('Please provide a question.', content_type='text/plain')

        # Use local Ollama Mistral endpoint
        ollama_url = "http://localhost:11434/api/generate"
        payload = {
            "model": "mistral",
            "prompt": question,
            "stream": True
        }

        response = requests.post(ollama_url, json=payload, stream=True)
        response.raise_for_status()

        def generate():
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        chunk = data.get('response', '')
                        if chunk:
                            yield chunk
                    except json.JSONDecodeError:
                        pass

        return StreamingHttpResponse(generate(), content_type='text/plain')
    except Exception as e:
        return StreamingHttpResponse(f'Error: {str(e)}', content_type='text/plain', status=500)
