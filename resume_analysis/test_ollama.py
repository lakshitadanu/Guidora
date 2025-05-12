import requests
import json

def test_ollama_connection():
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "mistral",
        "prompt": "You are an expert career coach. Given the following skills: Python, SQL, Data Analysis. Target Role: Data Scientist. Identify skill gaps, recommend new skills, and suggest certifications.",
        "stream": True
    }
    
    try:
        print("Testing Ollama API connection...")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, stream=True, timeout=30)
        print(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            print("Connection successful! Reading response...")
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        print(f"Received: {data.get('response', '')}")
                    except json.JSONDecodeError:
                        print(f"Raw line: {line}")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_ollama_connection() 