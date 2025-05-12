from django.db import migrations

def add_assessment_questions(apps, schema_editor):
    AssessmentQuestion = apps.get_model('assessment', 'AssessmentQuestion')
    
    # Personality Questions
    personality_questions = [
        # Extraversion
        {
            'question_text': 'I enjoy meeting new people.',
            'assessment_type': 'personality',
            'category': 'extraversion',
            'options': ['1', '2', '3', '4', '5']
        },
        {
            'question_text': 'I feel comfortable speaking in front of a group.',
            'assessment_type': 'personality',
            'category': 'extraversion',
            'options': ['1', '2', '3', '4', '5']
        },
        {
            'question_text': 'I tend to take the lead in group situations.',
            'assessment_type': 'personality',
            'category': 'extraversion',
            'options': ['1', '2', '3', '4', '5']
        },
        {
            'question_text': 'I enjoy social gatherings and parties.',
            'assessment_type': 'personality',
            'category': 'extraversion',
            'options': ['1', '2', '3', '4', '5']
        },
        
        # Agreeableness
        {
            'question_text': 'I try to be empathetic and understanding toward others.',
            'assessment_type': 'personality',
            'category': 'agreeableness',
            'options': ['1', '2', '3', '4', '5']
        },
        {
            'question_text': 'I find it easy to forgive others.',
            'assessment_type': 'personality',
            'category': 'agreeableness',
            'options': ['1', '2', '3', '4', '5']
        },
        {
            'question_text': 'I avoid conflicts and prefer harmony.',
            'assessment_type': 'personality',
            'category': 'agreeableness',
            'options': ['1', '2', '3', '4', '5']
        },
        {
            'question_text': 'I am willing to help others even if it means sacrificing my time.',
            'assessment_type': 'personality',
            'category': 'agreeableness',
            'options': ['1', '2', '3', '4', '5']
        },
        
        # Conscientiousness
        {
            'question_text': 'I prefer to plan things out rather than act spontaneously.',
            'assessment_type': 'personality',
            'category': 'conscientiousness',
            'options': ['1', '2', '3', '4', '5']
        },
        {
            'question_text': 'I am very organized and keep track of my tasks.',
            'assessment_type': 'personality',
            'category': 'conscientiousness',
            'options': ['1', '2', '3', '4', '5']
        },
        {
            'question_text': 'I am detail-oriented and pay attention to small things.',
            'assessment_type': 'personality',
            'category': 'conscientiousness',
            'options': ['1', '2', '3', '4', '5']
        },
        {
            'question_text': 'I find it easy to focus on long-term goals.',
            'assessment_type': 'personality',
            'category': 'conscientiousness',
            'options': ['1', '2', '3', '4', '5']
        },
        
        # Openness
        {
            'question_text': 'I enjoy trying new activities and exploring new ideas.',
            'assessment_type': 'personality',
            'category': 'openness',
            'options': ['1', '2', '3', '4', '5']
        },
        {
            'question_text': 'I enjoy exploring creative and artistic expressions.',
            'assessment_type': 'personality',
            'category': 'openness',
            'options': ['1', '2', '3', '4', '5']
        },
        {
            'question_text': 'I am curious about things and enjoy learning new concepts.',
            'assessment_type': 'personality',
            'category': 'openness',
            'options': ['1', '2', '3', '4', '5']
        },
        {
            'question_text': 'I tend to think outside the box and approach things in novel ways.',
            'assessment_type': 'personality',
            'category': 'openness',
            'options': ['1', '2', '3', '4', '5']
        },
        
        # Neuroticism
        {
            'question_text': 'I tend to get easily stressed or anxious.',
            'assessment_type': 'personality',
            'category': 'neuroticism',
            'options': ['1', '2', '3', '4', '5']
        },
        {
            'question_text': 'I often feel upset or worried about things in my life.',
            'assessment_type': 'personality',
            'category': 'neuroticism',
            'options': ['1', '2', '3', '4', '5']
        },
        {
            'question_text': 'I get easily irritated by minor issues.',
            'assessment_type': 'personality',
            'category': 'neuroticism',
            'options': ['1', '2', '3', '4', '5']
        },
        {
            'question_text': 'I have difficulty calming down when I am upset.',
            'assessment_type': 'personality',
            'category': 'neuroticism',
            'options': ['1', '2', '3', '4', '5']
        },
        
        # Aptitude Questions - Logical
        {
            'question_text': 'If all roses are flowers and some flowers fade quickly, which statement is true?',
            'assessment_type': 'aptitude',
            'category': 'logical',
            'options': [
                'All roses fade quickly',
                'Some roses may fade quickly',
                'No roses fade quickly',
                'Roses never fade'
            ],
            'correct_answer': 'Some roses may fade quickly'
        },
        {
            'question_text': 'In a sequence: 2, 6, 12, 20, 30, what comes next?',
            'assessment_type': 'aptitude',
            'category': 'logical',
            'options': ['42', '40', '36', '44'],
            'correct_answer': '42'
        },
        {
            'question_text': 'If FISH is coded as EHRG, how is BIRD coded?',
            'assessment_type': 'aptitude',
            'category': 'logical',
            'options': ['AHQC', 'CHQC', 'AHQD', 'BHQC'],
            'correct_answer': 'AHQC'
        },
        
        # Numerical
        {
            'question_text': 'If 15% of a number is 45, what is the number?',
            'assessment_type': 'aptitude',
            'category': 'numerical',
            'options': ['300', '250', '350', '400'],
            'correct_answer': '300'
        },
        {
            'question_text': 'What is the next number in the series: 1, 4, 9, 16, 25, __?',
            'assessment_type': 'aptitude',
            'category': 'numerical',
            'options': ['30', '36', '49', '64'],
            'correct_answer': '36'
        },
        {
            'question_text': 'If a train travels 360 kilometers in 4 hours, what is its speed in kilometers per hour?',
            'assessment_type': 'aptitude',
            'category': 'numerical',
            'options': ['80', '90', '85', '95'],
            'correct_answer': '90'
        },
        
        # Verbal
        {
            'question_text': 'Choose the word that is most nearly OPPOSITE in meaning to "benevolent".',
            'assessment_type': 'aptitude',
            'category': 'verbal',
            'options': ['Malevolent', 'Beneficial', 'Generous', 'Kind'],
            'correct_answer': 'Malevolent'
        },
        {
            'question_text': 'Complete the analogy: Book is to Reading as Fork is to ___.',
            'assessment_type': 'aptitude',
            'category': 'verbal',
            'options': ['Kitchen', 'Eating', 'Cooking', 'Utensil'],
            'correct_answer': 'Eating'
        },
        {
            'question_text': 'Which word is spelled incorrectly?',
            'assessment_type': 'aptitude',
            'category': 'verbal',
            'options': ['Accommodation', 'Occurrence', 'Perseverence', 'Necessary'],
            'correct_answer': 'Perseverence'
        },
        
        # Spatial
        {
            'question_text': 'If a cube is unfolded, how many faces will it have?',
            'assessment_type': 'aptitude',
            'category': 'spatial',
            'options': ['4', '5', '6', '8'],
            'correct_answer': '6'
        },
        {
            'question_text': 'Which shape would complete the pattern: Triangle, Square, Pentagon, ___?',
            'assessment_type': 'aptitude',
            'category': 'spatial',
            'options': ['Circle', 'Hexagon', 'Rectangle', 'Octagon'],
            'correct_answer': 'Hexagon'
        },
        {
            'question_text': 'If you rotate a capital letter "L" 90 degrees clockwise, what will it look like?',
            'assessment_type': 'aptitude',
            'category': 'spatial',
            'options': ['⊥', '7', '⌐', '┘'],
            'correct_answer': '⊥'
        },
        
        # Mechanical
        {
            'question_text': 'Which simple machine is a wheel and axle?',
            'assessment_type': 'aptitude',
            'category': 'mechanical',
            'options': ['Doorknob', 'Hammer', 'Screwdriver', 'Pliers'],
            'correct_answer': 'Doorknob'
        },
        {
            'question_text': 'If gear A turns clockwise, which way will gear B turn if they are meshed together?',
            'assessment_type': 'aptitude',
            'category': 'mechanical',
            'options': ['Clockwise', 'Counterclockwise', 'Neither', 'Both'],
            'correct_answer': 'Counterclockwise'
        },
        {
            'question_text': 'What happens to the speed of a pulley system when you add more pulleys?',
            'assessment_type': 'aptitude',
            'category': 'mechanical',
            'options': [
                'Speed increases',
                'Speed decreases',
                'Speed remains the same',
                'Speed becomes variable'
            ],
            'correct_answer': 'Speed decreases'
        }
    ]
    
    for question_data in personality_questions:
        AssessmentQuestion.objects.create(**question_data)

def remove_assessment_questions(apps, schema_editor):
    AssessmentQuestion = apps.get_model('assessment', 'AssessmentQuestion')
    AssessmentQuestion.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('assessment', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_assessment_questions, remove_assessment_questions),
    ] 