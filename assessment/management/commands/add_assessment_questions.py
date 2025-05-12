from django.core.management.base import BaseCommand
from assessment.models import AssessmentQuestion

class Command(BaseCommand):
    help = 'Adds personality and aptitude assessment questions'

    def handle(self, *args, **kwargs):
        # Personality Questions
        personality_questions = [
            # Extraversion
            {
                'question_text': 'I enjoy meeting new people.',
                'category': 'extraversion',
                'assessment_type': 'personality',
                'options': [1, 2, 3, 4, 5]
            },
            {
                'question_text': 'I feel comfortable speaking in front of a group.',
                'category': 'extraversion',
                'assessment_type': 'personality',
                'options': [1, 2, 3, 4, 5]
            },
            {
                'question_text': 'I tend to take the lead in group situations.',
                'category': 'extraversion',
                'assessment_type': 'personality',
                'options': [1, 2, 3, 4, 5]
            },
            {
                'question_text': 'I enjoy social gatherings and parties.',
                'category': 'extraversion',
                'assessment_type': 'personality',
                'options': [1, 2, 3, 4, 5]
            },
            # Agreeableness
            {
                'question_text': 'I try to be empathetic and understanding toward others.',
                'category': 'agreeableness',
                'assessment_type': 'personality',
                'options': [1, 2, 3, 4, 5]
            },
            {
                'question_text': 'I find it easy to forgive others.',
                'category': 'agreeableness',
                'assessment_type': 'personality',
                'options': [1, 2, 3, 4, 5]
            },
            {
                'question_text': 'I avoid conflicts and prefer harmony.',
                'category': 'agreeableness',
                'assessment_type': 'personality',
                'options': [1, 2, 3, 4, 5]
            },
            {
                'question_text': 'I am willing to help others even if it means sacrificing my time.',
                'category': 'agreeableness',
                'assessment_type': 'personality',
                'options': [1, 2, 3, 4, 5]
            },
            # Conscientiousness
            {
                'question_text': 'I prefer to plan things out rather than act spontaneously.',
                'category': 'conscientiousness',
                'assessment_type': 'personality',
                'options': [1, 2, 3, 4, 5]
            },
            {
                'question_text': 'I am very organized and keep track of my tasks.',
                'category': 'conscientiousness',
                'assessment_type': 'personality',
                'options': [1, 2, 3, 4, 5]
            },
            {
                'question_text': 'I am detail-oriented and pay attention to small things.',
                'category': 'conscientiousness',
                'assessment_type': 'personality',
                'options': [1, 2, 3, 4, 5]
            },
            {
                'question_text': 'I find it easy to focus on long-term goals.',
                'category': 'conscientiousness',
                'assessment_type': 'personality',
                'options': [1, 2, 3, 4, 5]
            },
            # Openness
            {
                'question_text': 'I enjoy trying new activities and exploring new ideas.',
                'category': 'openness',
                'assessment_type': 'personality',
                'options': [1, 2, 3, 4, 5]
            },
            {
                'question_text': 'I enjoy exploring creative and artistic expressions.',
                'category': 'openness',
                'assessment_type': 'personality',
                'options': [1, 2, 3, 4, 5]
            },
            {
                'question_text': 'I am curious about things and enjoy learning new concepts.',
                'category': 'openness',
                'assessment_type': 'personality',
                'options': [1, 2, 3, 4, 5]
            },
            {
                'question_text': 'I tend to think outside the box and approach things in novel ways.',
                'category': 'openness',
                'assessment_type': 'personality',
                'options': [1, 2, 3, 4, 5]
            },
            # Neuroticism
            {
                'question_text': 'I tend to get easily stressed or anxious.',
                'category': 'neuroticism',
                'assessment_type': 'personality',
                'options': [1, 2, 3, 4, 5]
            },
            {
                'question_text': 'I often feel upset or worried about things in my life.',
                'category': 'neuroticism',
                'assessment_type': 'personality',
                'options': [1, 2, 3, 4, 5]
            },
            {
                'question_text': 'I get easily irritated by minor issues.',
                'category': 'neuroticism',
                'assessment_type': 'personality',
                'options': [1, 2, 3, 4, 5]
            },
            {
                'question_text': 'I have difficulty calming down when I am upset.',
                'category': 'neuroticism',
                'assessment_type': 'personality',
                'options': [1, 2, 3, 4, 5]
            },
        ]

        # Aptitude Questions
        aptitude_questions = [
            # Logical Questions
            {
                'question_text': 'If all roses are flowers and some flowers fade quickly, which of the following statements must be true?',
                'category': 'logical',
                'assessment_type': 'aptitude',
                'options': [
                    'All roses fade quickly',
                    'Some roses fade quickly',
                    'No roses fade quickly',
                    'Roses never fade'
                ],
                'correct_answer': 'Some roses fade quickly'
            },
            {
                'question_text': 'In a sequence: 2, 6, 12, 20, 30, what comes next?',
                'category': 'logical',
                'assessment_type': 'aptitude',
                'options': ['42', '40', '36', '44'],
                'correct_answer': '42'
            },
            {
                'question_text': 'If A is taller than B, and B is taller than C, who is the shortest?',
                'category': 'logical',
                'assessment_type': 'aptitude',
                'options': ['A', 'B', 'C', 'Cannot be determined'],
                'correct_answer': 'C'
            },
            # Numerical Questions
            {
                'question_text': 'If a shirt costs $45 and is on sale for 20% off, what is the final price?',
                'category': 'numerical',
                'assessment_type': 'aptitude',
                'options': ['$36', '$35', '$40', '$38'],
                'correct_answer': '$36'
            },
            {
                'question_text': 'What is 15% of 200?',
                'category': 'numerical',
                'assessment_type': 'aptitude',
                'options': ['30', '25', '35', '40'],
                'correct_answer': '30'
            },
            {
                'question_text': 'If 8 workers can complete a project in 10 days, how many days will it take 4 workers?',
                'category': 'numerical',
                'assessment_type': 'aptitude',
                'options': ['15', '20', '25', '30'],
                'correct_answer': '20'
            },
            # Verbal Questions
            {
                'question_text': 'Choose the word that is most nearly opposite in meaning to "BENEVOLENT"',
                'category': 'verbal',
                'assessment_type': 'aptitude',
                'options': ['Malevolent', 'Generous', 'Kind', 'Charitable'],
                'correct_answer': 'Malevolent'
            },
            {
                'question_text': 'Complete the analogy: Book is to Reader as Movie is to ___',
                'category': 'verbal',
                'assessment_type': 'aptitude',
                'options': ['Actor', 'Director', 'Viewer', 'Screen'],
                'correct_answer': 'Viewer'
            },
            {
                'question_text': 'Which word is a synonym for "DILIGENT"?',
                'category': 'verbal',
                'assessment_type': 'aptitude',
                'options': ['Lazy', 'Hardworking', 'Careless', 'Slow'],
                'correct_answer': 'Hardworking'
            },
            # Spatial Questions
            {
                'question_text': 'If a cube is unfolded, how many faces will it have?',
                'category': 'spatial',
                'assessment_type': 'aptitude',
                'options': ['4', '5', '6', '8'],
                'correct_answer': '6'
            },
            {
                'question_text': 'Which shape would complete the pattern: Triangle, Square, Pentagon, ___?',
                'category': 'spatial',
                'assessment_type': 'aptitude',
                'options': ['Circle', 'Hexagon', 'Rectangle', 'Octagon'],
                'correct_answer': 'Hexagon'
            },
            {
                'question_text': 'If you rotate a square 45 degrees, what shape appears to be formed?',
                'category': 'spatial',
                'assessment_type': 'aptitude',
                'options': ['Rectangle', 'Diamond', 'Triangle', 'Pentagon'],
                'correct_answer': 'Diamond'
            },
            # Mechanical Questions
            {
                'question_text': 'Which simple machine is a wheel and axle?',
                'category': 'mechanical',
                'assessment_type': 'aptitude',
                'options': ['Doorknob', 'Hammer', 'Screwdriver', 'Pliers'],
                'correct_answer': 'Doorknob'
            },
            {
                'question_text': 'In a pulley system, what happens to the force needed as you add more pulleys?',
                'category': 'mechanical',
                'assessment_type': 'aptitude',
                'options': ['Increases', 'Decreases', 'Stays the same', 'Becomes zero'],
                'correct_answer': 'Decreases'
            },
            {
                'question_text': 'Which way should gears turn if the first gear turns clockwise?',
                'category': 'mechanical',
                'assessment_type': 'aptitude',
                'options': [
                    'All gears turn clockwise',
                    'Adjacent gears turn counterclockwise',
                    'No gears will turn',
                    'Depends on gear size'
                ],
                'correct_answer': 'Adjacent gears turn counterclockwise'
            },
        ]

        # Add all questions
        for question in personality_questions + aptitude_questions:
            AssessmentQuestion.objects.get_or_create(
                question_text=question['question_text'],
                defaults={
                    'assessment_type': question['assessment_type'],
                    'category': question['category'],
                    'options': question['options'],
                    'correct_answer': question.get('correct_answer')
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully added all assessment questions')) 