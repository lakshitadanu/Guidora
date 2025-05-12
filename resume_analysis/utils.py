import os
import PyPDF2
from docx import Document
import re
from collections import defaultdict
from .models import ResumeAnalysis
import json

class TextProcessor:
    @staticmethod
    def tokenize(text):
        """Simple word tokenization using regex"""
        # Convert to lowercase and split on word boundaries
        words = re.findall(r'\b\w+\b', text.lower())
        return words
    
    @staticmethod
    def extract_contact_info(text):
        """Extract contact information using regex patterns"""
        patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'linkedin': r'linkedin\.com/\w+',
            'website': r'https?://(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/\S*)?'
        }
        
        contact_info = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                contact_info[key] = match.group()
        
        return contact_info
    
    @staticmethod
    def split_into_sentences(text):
        """Split text into sentences using regex"""
        # Split on period, exclamation mark, or question mark followed by space and capital letter
        sentences = re.split(r'[.!?]+\s+(?=[A-Z])', text)
        return [s.strip() for s in sentences if s.strip()]

def extract_sections(text):
    # Common section headers
    headers = [
        'education', 'academic background', 'qualifications',
        'experience', 'work experience', 'professional experience',
        'skills', 'technical skills', 'core competencies', 'expertise',
        'projects', 'certifications', 'extracurricular', 'language', 'summary', 'profile', 'contact'
    ]
    pattern = r'(^|\n)\s*(' + '|'.join([re.escape(h) for h in headers]) + r')\s*[:\-]?\s*(?=\n|$)'
    # Find all section headers and their positions
    matches = list(re.finditer(pattern, text, flags=re.IGNORECASE))
    sections = {}
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        header = match.group(2).strip().lower()
        sections[header] = text[start:end].strip()
    return sections

def extract_name(text):
    # Remove emails, phones, and section headers from the top
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    for line in lines[:10]:
        if (len(line.split()) >= 2 and
            not line.isupper() and
            not re.search(r'@|\d', line) and
            not re.match(r'^(education|experience|skills|projects|summary|profile|contact)$', line.strip().lower())):
            return line
    return 'Not found'

def extract_education(text):
    sections = extract_sections(text)
    edu = []
    for key in sections:
        if 'education' in key:
            # Split by blank lines or bullets
            entries = re.split(r'\n\s*[-•*]?\s*', sections[key])
            edu += [e.strip() for e in entries if e.strip()]
    if not edu:
        # Fallback: lines with degree/institution/year
        pattern = re.compile(r'(bachelor|master|phd|b\.tech|m\.tech|b\.e|m\.e|mba|b\.sc|m\.sc|school|university|college|institute)[^\n]{0,80}(\d{4})?', re.IGNORECASE)
        edu = [m.group(0).strip() for m in pattern.finditer(text)]
    return edu

def extract_experience(text):
    sections = extract_sections(text)
    exp = []
    for key in sections:
        if 'experience' in key:
            entries = re.split(r'\n\s*[-•*]?\s*', sections[key])
            exp += [e.strip() for e in entries if e.strip()]
    if not exp:
        # Fallback: lines with job/role/company/duration
        pattern = re.compile(r'(intern|engineer|developer|manager|consultant|analyst|lead|project|trainee|company|technologies|solutions|systems|labs)[^\n]{0,80}(\d{4})?', re.IGNORECASE)
        exp = [m.group(0).strip() for m in pattern.finditer(text)]
    return exp

def extract_skills_from_dict(text, skills_dict):
    # Try to extract from a Skills section first
    sections = extract_sections(text)
    skill_lines = []
    for key in sections:
        if 'skill' in key:
            skill_lines += re.split(r'[\n,;|]', sections[key])
    found = {}
    text_lower = text.lower()
    for category, skills in skills_dict.items():
        found[category] = []
        for s in skills:
            if any(re.search(r'\b' + re.escape(s.lower()) + r'\b', l.lower()) for l in skill_lines):
                found[category].append(s)
            elif re.search(r'\b' + re.escape(s.lower()) + r'\b', text_lower):
                found[category].append(s)
    return {k: v for k, v in found.items() if v}

def extract_skills(text):
    """Extract skills from text using pattern matching"""
    # Load skills data
    with open('resume_analysis/data/skills.json', 'r') as f:
        skill_categories = json.load(f)

    found_skills = defaultdict(list)
    text_lower = text.lower()
    
    # Extract skills using pattern matching
    for category, skills in skill_categories.items():
        for skill in skills:
            skill_lower = skill.lower()
            # Look for exact matches with word boundaries
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            if re.search(pattern, text_lower):
                found_skills[category].append(skill.title())
    
    return dict(found_skills)

def extract_education(text):
    """Extract education information using regex patterns"""
    education_data = []
    
    # Split text into sentences for better processing
    sentences = TextProcessor.split_into_sentences(text)
    
    # Education related patterns
    patterns = {
        'degree': r'(?i)(B\.?Tech|M\.?Tech|B\.?E|M\.?E|B\.?Sc|M\.?Sc|Ph\.?D|Bachelor|Master|MBA)(?:\s+(?:of|in|degree))?\s+([^.,]+)',
        'university': r'(?i)(University|College|Institute|School)\s+(?:of\s+)?([^.,]+)',
        'year': r'(?i)(20\d{2})',
        'gpa': r'(?i)(?:GPA|CGPA|Grade)[\s:]+([0-9.]+)',
        'major': r'(?i)(?:Major|Specialization|Branch)[\s:]+([^.,]+)'
    }
    
    for sentence in sentences:
        edu_info = {}
        
        # Check each pattern in the sentence
        for key, pattern in patterns.items():
            match = re.search(pattern, sentence)
            if match:
                if key in ['degree', 'university'] and match.group(2):
                    edu_info[key] = f"{match.group(1)} {match.group(2)}".strip()
                else:
                    edu_info[key] = match.group(1).strip()
        
        # If we found any education information, add it to the list
        if edu_info:
            education_data.append(edu_info)
    
    return education_data

def extract_experience(text):
    """Extract work experience using regex patterns"""
    experience_data = []
    
    # Split text into sentences
    sentences = TextProcessor.split_into_sentences(text)
    
    # Experience related patterns
    patterns = {
        'job_title': r'(?i)(Software|Developer|Engineer|Analyst|Consultant|Manager|Director|Lead|Architect|Designer)\s+(?:at|@|with)?\s+([A-Za-z\s&]+)',
        'company': r'(?i)(?:at|@|with)\s+([A-Z][A-Za-z\s&]+(?:Inc\.?|Ltd\.?|LLC|Corporation)?)',
        'duration': r'(?i)(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,]+20\d{2}\s*(?:-|to)\s*(?:Present|Current|Now|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,]+20\d{2})',
        'achievements': r'(?i)•\s*([^•\n]+)'  # Bullet points often indicate achievements
    }
    
    current_exp = {}
    
    for sentence in sentences:
        for key, pattern in patterns.items():
            matches = re.finditer(pattern, sentence)
            for match in matches:
                if key == 'achievements':
                    if 'achievements' not in current_exp:
                        current_exp['achievements'] = []
                    current_exp['achievements'].append(match.group(1).strip())
                else:
                    current_exp[key] = match.group().strip()
        
        # If we have enough info, save this experience entry
        if len(set(current_exp.keys()) - {'achievements'}) >= 2:  # At least job title and company/duration
            if current_exp not in experience_data:  # Avoid duplicates
                experience_data.append(current_exp.copy())
            current_exp = {}
    
    return experience_data

class ATSScorer:
    def __init__(self):
        # Common words to ignore
        self.stop_words = set([
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with'
        ])
    
    def calculate_keyword_density(self, text, keywords):
        """Calculate keyword density using simple word tokenization"""
        words = TextProcessor.tokenize(text)
        words = [w for w in words if w not in self.stop_words]
        total_words = len(words)
        
        keyword_count = sum(1 for word in words if word in keywords)
        return (keyword_count / total_words) * 100 if total_words > 0 else 0
    
    def analyze_resume_format(self, text):
        """Check for presence of important resume sections"""
        sections = ['education', 'experience', 'skills', 'projects']
        score = 0
        
        for section in sections:
            if re.search(rf'\b{section}\b', text.lower()):
                score += 25
        
        return score
    
    def check_contact_info(self, text):
        """Check for presence of contact information"""
        contact_info = TextProcessor.extract_contact_info(text)
        score = 0
        
        if 'email' in contact_info:
            score += 20
        if 'phone' in contact_info:
            score += 20
        if 'linkedin' in contact_info:
            score += 10
        
        return score
    
    def calculate_ats_score(self, text, job_keywords):
        """Calculate overall ATS score"""
        scores = {
            'keyword_match': self.calculate_keyword_density(text, job_keywords),
            'format_score': self.analyze_resume_format(text),
            'contact_info': self.check_contact_info(text)
        }
        
        weights = {'keyword_match': 0.5, 'format_score': 0.3, 'contact_info': 0.2}
        final_score = sum(scores[k] * weights[k] for k in scores)
        
        return {
            'total_score': min(final_score, 100),
            'breakdown': scores,
            'improvements': self.get_improvement_suggestions(scores)
        }
    
    def get_improvement_suggestions(self, scores):
        """Generate improvement suggestions based on scores"""
        suggestions = []
        
        if scores['keyword_match'] < 50:
            suggestions.append("Include more relevant keywords from the job description")
        if scores['format_score'] < 75:
            suggestions.append("Ensure all major sections (Education, Experience, Skills, Projects) are clearly labeled")
        if scores['contact_info'] < 40:
            suggestions.append("Add complete contact information including email, phone, and LinkedIn profile")
        
        return suggestions

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(docx_path):
    """Extract text from DOCX file"""
    doc = Document(docx_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def analyze_resume(resume):
    """Main function to analyze a resume"""
    # Get the file path
    file_path = resume.file.path
    
    # Extract text based on file type
    if file_path.endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format")
    
    # Initialize ATS Scorer
    ats_scorer = ATSScorer()
    
    # Extract information
    skills = extract_skills(text)
    education = extract_education(text)
    experience = extract_experience(text)
    
    # Get relevant keywords based on skills
    job_keywords = set()
    for skill_list in skills.values():
        job_keywords.update(map(str.lower, skill_list))
    
    # Calculate ATS score
    ats_analysis = ats_scorer.calculate_ats_score(text, job_keywords)
    
    # Create analysis object
    analysis = ResumeAnalysis.objects.create(
        resume=resume,
        skills=skills,
        education=education,
        experience=experience,
        recommendations={},  # Empty recommendations for now
        ats_score=ats_analysis
    )
    
    # Mark resume as analyzed
    resume.analyzed = True
    resume.save()
    
    return analysis 