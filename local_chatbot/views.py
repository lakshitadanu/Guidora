import json
import requests
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import ChatHistory
from django.shortcuts import render

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

@csrf_exempt
@require_POST
@login_required
def chat(request):
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Prepare the prompt for Ollama
        prompt = f"{SYSTEM_PROMPT}\n\nStudent: {message}\nCounselor:"
        
        # Call Ollama API
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            response_data = response.json()
            bot_response = response_data.get('response', '')
            
            # Save chat history
            ChatHistory.objects.create(
                user=request.user,
                message=message,
                response=bot_response
            )
            
            return JsonResponse({
                'status': 'success',
                'response': bot_response
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to get response from AI model'
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def get_chat_history(request):
    """Get the user's chat history"""
    chats = ChatHistory.objects.filter(user=request.user)[:10]  # Get last 10 chats
    chat_history = [{
        'message': chat.message,
        'response': chat.response,
        'timestamp': chat.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for chat in chats]
    
    return JsonResponse({
        'status': 'success',
        'chat_history': chat_history
    })

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

def chat_ui(request):
    return render(request, 'local_chatbot/chat.html') 