import joblib
import numpy as np
import pandas as pd

class CareerPredictor:
    def __init__(self):
        # Load all models and preprocessors
        self.models = {
            'career_1': joblib.load('ml_models/career_1_model.pkl'),
            'career_2': joblib.load('ml_models/career_2_model.pkl'),
            'career_3': joblib.load('ml_models/career_3_model.pkl')
        }
        
        self.preprocessors = {
            'career_1': joblib.load('ml_models/career_1_preprocessor.pkl'),
            'career_2': joblib.load('ml_models/career_2_preprocessor.pkl'),
            'career_3': joblib.load('ml_models/career_3_preprocessor.pkl')
        }
        
        # Load label encoders
        self.stream_encoder = joblib.load('ml_models/stream_encoder.pkl')
        self.career_encoder = joblib.load('ml_models/career_encoder.pkl')

    def prepare_input_features(self, input_data, previous_predictions=None):
        """
        Prepare input features in the same way as training data
        If previous_predictions is provided, include them as features
        """
        # Create a DataFrame from input data
        df = pd.DataFrame([input_data])
        
        # Encode stream
        df['stream_encoded'] = self.stream_encoder.transform([input_data['stream']])[0]
        
        # Calculate composite scores
        df['total_aptitude'] = (
            df['numerical_ability'] + 
            df['verbal_reasoning'] + 
            df['logical_thinking'] + 
            df['spatial_awareness'] + 
            df['problem_solving']
        )
        
        df['total_personality'] = (
            df['openness'] + 
            df['conscientiousness'] + 
            df['extraversion'] + 
            df['agreeableness'] + 
            df['neuroticism']
        )
        
        # Calculate stream-specific aptitude scores
        stream_code = df['stream_encoded'].iloc[0]
        df['science_aptitude'] = (df['numerical_ability'] + df['logical_thinking']) * (stream_code == 0)
        df['bio_aptitude'] = (df['verbal_reasoning'] + df['spatial_awareness']) * (stream_code == 1)
        df['commerce_aptitude'] = (df['numerical_ability'] + df['verbal_reasoning']) * (stream_code == 2)
        df['humanities_aptitude'] = (df['verbal_reasoning'] + df['spatial_awareness']) * (stream_code == 3)
        
        # If previous predictions are provided, add them as features
        if previous_predictions:
            for prev_field, prev_pred in previous_predictions.items():
                df[f'{prev_field}_prediction'] = self.career_encoder.transform([prev_pred])[0]
        
        # Select features in the same order as training
        features = [
            '12th_percentage',
            'numerical_ability',
            'verbal_reasoning',
            'logical_thinking',
            'spatial_awareness',
            'problem_solving',
            'openness',
            'conscientiousness',
            'extraversion',
            'agreeableness',
            'neuroticism',
            'total_aptitude',
            'total_personality',
            'science_aptitude',
            'bio_aptitude',
            'commerce_aptitude',
            'humanities_aptitude',
            'stream_encoded'
        ]
        
        # Add previous prediction features if they exist
        if previous_predictions:
            for prev_field in previous_predictions.keys():
                features.append(f'{prev_field}_prediction')
        
        return df[features]

    def predict_careers(self, input_data):
        """
        Predict careers using sequential prediction where each model knows about previous predictions
        """
        predictions = {}
        
        # First prediction (career_1)
        features = self.prepare_input_features(input_data)
        scaled_features = self.preprocessors['career_1'].transform(features)
        career_1_pred = self.models['career_1'].predict(scaled_features)[0]
        career_1_name = self.career_encoder.inverse_transform([career_1_pred])[0]
        predictions['career_1'] = career_1_name
        
        # Second prediction (career_2) - knows about career_1
        features = self.prepare_input_features(input_data, {'career_1': career_1_name})
        scaled_features = self.preprocessors['career_2'].transform(features)
        career_2_pred = self.models['career_2'].predict(scaled_features)[0]
        career_2_name = self.career_encoder.inverse_transform([career_2_pred])[0]
        predictions['career_2'] = career_2_name
        
        # Third prediction (career_3) - knows about career_1 and career_2
        features = self.prepare_input_features(
            input_data, 
            {
                'career_1': career_1_name,
                'career_2': career_2_name
            }
        )
        scaled_features = self.preprocessors['career_3'].transform(features)
        career_3_pred = self.models['career_3'].predict(scaled_features)[0]
        career_3_name = self.career_encoder.inverse_transform([career_3_pred])[0]
        predictions['career_3'] = career_3_name
        
        return predictions

    def predict_career_with_probabilities(self, input_data):
        """
        Predict careers with probabilities using sequential prediction
        """
        predictions = {}
        
        # First prediction (career_1)
        features = self.prepare_input_features(input_data)
        scaled_features = self.preprocessors['career_1'].transform(features)
        career_1_pred = self.models['career_1'].predict(scaled_features)[0]
        career_1_probs = self.models['career_1'].predict_proba(scaled_features)[0]
        career_1_name = self.career_encoder.inverse_transform([career_1_pred])[0]
        
        all_careers = self.career_encoder.classes_
        career_1_probs_dict = dict(zip(all_careers, career_1_probs))
        predictions['career_1'] = {
            'predicted_career': career_1_name,
            'probabilities': career_1_probs_dict
        }
        
        # Second prediction (career_2) - knows about career_1
        features = self.prepare_input_features(input_data, {'career_1': career_1_name})
        scaled_features = self.preprocessors['career_2'].transform(features)
        career_2_pred = self.models['career_2'].predict(scaled_features)[0]
        career_2_probs = self.models['career_2'].predict_proba(scaled_features)[0]
        career_2_name = self.career_encoder.inverse_transform([career_2_pred])[0]
        
        career_2_probs_dict = dict(zip(all_careers, career_2_probs))
        predictions['career_2'] = {
            'predicted_career': career_2_name,
            'probabilities': career_2_probs_dict
        }
        
        # Third prediction (career_3) - knows about career_1 and career_2
        features = self.prepare_input_features(
            input_data, 
            {
                'career_1': career_1_name,
                'career_2': career_2_name
            }
        )
        scaled_features = self.preprocessors['career_3'].transform(features)
        career_3_pred = self.models['career_3'].predict(scaled_features)[0]
        career_3_probs = self.models['career_3'].predict_proba(scaled_features)[0]
        career_3_name = self.career_encoder.inverse_transform([career_3_pred])[0]
        
        career_3_probs_dict = dict(zip(all_careers, career_3_probs))
        predictions['career_3'] = {
            'predicted_career': career_3_name,
            'probabilities': career_3_probs_dict
        }
        
        return predictions 