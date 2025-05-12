import joblib
import numpy as np
from django.conf import settings
import os
from .models import AssessmentResult, CareerRecommendation
from accounts.models import SchoolStudent, User
import logging
import traceback

logger = logging.getLogger(__name__)

class CareerRecommender:
    def __init__(self):
        model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'indian_career_recommendations.pkl')
        self.model = joblib.load(model_path)
        # Define career mapping based on complete training data
        self.career_mapping = {
            0: "Software Engineer",
            1: "Medical Doctor (MBBS)",
            2: "Chartered Accountant",
            3: "IAS Officer",
            4: "Business Development Manager",
            5: "Forensic Scientist",
            6: "Nuclear Engineer",
            7: "Social Worker",
            8: "Nutritionist",
            9: "Geneticist",
            10: "Naval Architect",
            11: "Automobile Engineer",
            12: "Archaeologist",
            13: "Historian",
            14: "Actuary",
            15: "Economist"
        }
        # Define stream suitability for each career
        self.stream_suitability = {
            "Software Engineer": ["pcm"],
            "Medical Doctor (MBBS)": ["pcb"],
            "Chartered Accountant": ["commerce"],
            "IAS Officer": ["pcm", "pcb", "commerce", "humanities"],
            "Business Development Manager": ["commerce"],
            "Forensic Scientist": ["pcm", "pcb"],
            "Nuclear Engineer": ["pcm"],
            "Social Worker": ["humanities"],
            "Nutritionist": ["pcb"],
            "Geneticist": ["pcb"],
            "Naval Architect": ["pcm"],
            "Automobile Engineer": ["pcm"],
            "Archaeologist": ["humanities"],
            "Historian": ["humanities"],
            "Actuary": ["pcm", "commerce"],
            "Economist": ["commerce", "humanities"]
        }
        logger.info(f"Loaded original model with {self.model.n_features_in_} features")
        logger.info(f"Available career paths: {list(self.career_mapping.values())}")

    def get_assessment_scores(self, user):
        """Get the latest assessment scores for a user."""
        try:
            aptitude_result = AssessmentResult.objects.filter(
                user=user, 
                assessment_type='aptitude'
            ).latest('completed_at')
            
            personality_result = AssessmentResult.objects.filter(
                user=user, 
                assessment_type='personality'
            ).latest('completed_at')

            scores = {
                # Aptitude scores (matching your CSV columns)
                'numerical_ability': aptitude_result.numerical_score,
                'verbal_reasoning': aptitude_result.verbal_score,
                'logical_thinking': aptitude_result.logical_score,
                'spatial_awareness': aptitude_result.spatial_score,
                'problem_solving': aptitude_result.mechanical_score,
                # Personality scores (matching your CSV columns)
                'openness': personality_result.openness_score,
                'conscientiousness': personality_result.conscientiousness_score,
                'extraversion': personality_result.extraversion_score,
                'agreeableness': personality_result.agreeableness_score,
                'neuroticism': personality_result.neuroticism_score
            }
            logger.info(f"Assessment scores: {scores}")
            return scores
        except AssessmentResult.DoesNotExist:
            logger.error("Assessment results not found for user")
            return None

    def get_student_profile(self, user):
        """Get the student's academic profile."""
        try:
            profile = SchoolStudent.objects.get(user=user)
            data = {
                'stream': profile.stream,
                'tenth_percentage': profile.tenth_marks,
                'twelfth_percentage': profile.twelfth_marks
            }
            logger.info(f"Student profile: {data}")
            return data
        except SchoolStudent.DoesNotExist:
            logger.error("School student profile not found for user")
            return None

    def encode_stream(self, stream):
        """Convert stream to numerical encoding matching original model"""
        # Map streams to numerical values matching the original encoding
        stream_mapping = {
            'pcm': 0,     # Science (PCM)
            'pcb': 1,     # Science (PCB)
            'commerce': 2, # Commerce
            'humanities': 3  # Humanities
        }
        encoded = stream_mapping.get(stream.lower(), 0)  # Default to PCM if unknown
        logger.info(f"Encoded stream {stream} as {encoded}")
        return encoded

    def prepare_features(self, assessment_scores, profile_data):
        """Prepare features for the model prediction."""
        if not assessment_scores or not profile_data:
            return None

        try:
            # Convert stream to numerical format
            stream_encoded = self.encode_stream(profile_data['stream'])
            
            # Create feature vector with exactly 12 features as expected by the model
            features = [
                float(stream_encoded),  # stream encoded as number
                float(profile_data['twelfth_percentage']),  # 12th percentage
                float(assessment_scores['numerical_ability']),
                float(assessment_scores['verbal_reasoning']), 
                float(assessment_scores['logical_thinking']),
                float(assessment_scores['spatial_awareness']),
                float(assessment_scores['problem_solving']),
                float(assessment_scores['openness']),
                float(assessment_scores['conscientiousness']),
                float(assessment_scores['extraversion']),
                float(assessment_scores['agreeableness']),
                float(assessment_scores['neuroticism'])
            ]

            logger.info(f"Prepared feature vector with {len(features)} features: {features}")
            return np.array(features).reshape(1, -1)
        except (ValueError, TypeError) as e:
            logger.error(f"Error preparing features: {str(e)}")
            return None

    def get_recommendations(self, user):
        """Get career recommendations for a user."""
        try:
            # Get assessment scores and profile data
            assessment_scores = self.get_assessment_scores(user)
            profile_data = self.get_student_profile(user)

            if not assessment_scores or not profile_data:
                logger.error("Missing assessment scores or profile data")
                return []

            # Prepare features for prediction
            features = self.prepare_features(assessment_scores, profile_data)
            if features is None:
                logger.error("Failed to prepare features")
                return []

            # Get predictions from model
            predictions = self.model.predict_proba(features)[0]
            
            # Sort predictions by probability
            sorted_indices = np.argsort(predictions)[::-1]  # Sort in descending order
            recommendations = []

            # Clear existing recommendations
            CareerRecommendation.objects.filter(user=user).delete()

            # Get user's stream
            user_stream = profile_data['stream'].lower()
            
            # Keep going through predictions until we find 3 suitable careers
            for idx in sorted_indices:
                career_path = self.career_mapping.get(idx, f"Career Path {idx}")
                
                # Check if career is suitable for user's stream
                if career_path in self.stream_suitability and user_stream in self.stream_suitability[career_path]:
                    # Get recommended courses for this career
                    courses = self.get_recommended_courses(career_path)
                    
                    recommendation = CareerRecommendation.objects.create(
                        user=user,
                        career_path=career_path,
                        confidence_score=0,  # Set to 0 to hide match score
                        recommended_courses=courses
                    )
                    recommendations.append(recommendation)
                    
                    # Stop once we have 3 suitable recommendations
                    if len(recommendations) >= 3:
                        break

            logger.info(f"Generated {len(recommendations)} stream-suitable recommendations for stream {user_stream}")
            return recommendations
        except Exception as e:
            logger.error(f"Error in get_recommendations: {str(e)}")
            traceback.print_exc()  # This will print the full error in your terminal
            return []

    def get_recommended_courses(self, career_path):
        """Get recommended courses for a career path."""
        course_mapping = {
            "Software Engineer": "B.Tech CSE, B.E. Computer Science, M.Tech, B.Sc Computer Science",
            "Medical Doctor (MBBS)": "MBBS, BDS, MD/MS, B.Sc Nursing",
            "Chartered Accountant": "CA Foundation, B.Com, M.Com, MBA Finance",
            "IAS Officer": "Any Graduation + UPSC Prep, Public Administration, Political Science",
            "Business Development Manager": "BBA, MBA, B.Com, Marketing Management",
            "Forensic Scientist": "B.Sc Forensic Science, M.Sc Forensic Science, Criminology",
            "Nuclear Engineer": "B.Tech Nuclear Engineering, M.Tech Nuclear Engineering",
            "Social Worker": "BSW, MSW, Sociology, Psychology",
            "Nutritionist": "B.Sc Nutrition, M.Sc Nutrition, Dietetics",
            "Geneticist": "B.Sc Genetics, M.Sc Genetics, Biotechnology",
            "Naval Architect": "B.Tech Naval Architecture, Marine Engineering",
            "Automobile Engineer": "B.Tech Automobile Engineering, Mechanical Engineering",
            "Archaeologist": "BA Archaeology, MA Archaeology, Ancient History",
            "Historian": "BA History, MA History, Archives Management",
            "Actuary": "Actuarial Science, Statistics, Mathematics",
            "Economist": "BA Economics, MA Economics, Econometrics"
        }
        return course_mapping.get(career_path, "")