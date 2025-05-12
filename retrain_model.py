import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE
import joblib
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_and_preprocess_data():
    """
    Load the dataset and perform initial preprocessing.
    Returns preprocessed DataFrame and target variables.
    """
    logger.info("Loading dataset...")
    df = pd.read_csv('indian_career_recommendations.csv')
    
    # Basic data cleaning
    logger.info("Performing basic data cleaning...")
    df = df.dropna()  # Remove rows with missing values
    df = df.drop_duplicates()  # Remove duplicate rows
    
    # Encode categorical variables
    logger.info("Encoding categorical variables...")
    le_stream = LabelEncoder()
    le_career = LabelEncoder()
    
    # Fit career encoder on all career fields to ensure consistent encoding
    all_careers = pd.concat([df['career_1'], df['career_2'], df['career_3']]).unique()
    le_career.fit(all_careers)
    
    df['stream_encoded'] = le_stream.fit_transform(df['stream'])
    df['career_1_encoded'] = le_career.transform(df['career_1'])
    df['career_2_encoded'] = le_career.transform(df['career_2'])
    df['career_3_encoded'] = le_career.transform(df['career_3'])
    
    # Save the label encoders
    os.makedirs('ml_models', exist_ok=True)
    joblib.dump(le_stream, 'ml_models/stream_encoder.pkl')
    joblib.dump(le_career, 'ml_models/career_encoder.pkl')
    
    return df, le_career

def feature_engineering(df):
    """
    Create relevant features based on aptitude and personality scores.
    """
    logger.info("Performing feature engineering...")
    
    # Create composite aptitude score
    df['total_aptitude'] = df['numerical_ability'] + df['verbal_reasoning'] + df['logical_thinking'] + df['spatial_awareness'] + df['problem_solving']
    
    # Create composite personality score
    df['total_personality'] = df['openness'] + df['conscientiousness'] + df['extraversion'] + df['agreeableness'] + df['neuroticism']
    
    # Create stream-specific aptitude scores using encoded stream values
    df['science_aptitude'] = (df['numerical_ability'] + df['logical_thinking']) * (df['stream_encoded'] == 0)  # PCM
    df['bio_aptitude'] = (df['verbal_reasoning'] + df['spatial_awareness']) * (df['stream_encoded'] == 1)  # PCB
    df['commerce_aptitude'] = (df['numerical_ability'] + df['verbal_reasoning']) * (df['stream_encoded'] == 2)  # Commerce
    df['humanities_aptitude'] = (df['verbal_reasoning'] + df['spatial_awareness']) * (df['stream_encoded'] == 3)  # Humanities
    
    return df

def prepare_features_and_target(df, career_field, previous_predictions=None):
    """
    Prepare features and target variable for model training.
    If previous_predictions is provided, include them as features.
    """
    logger.info(f"Preparing features and target variable for {career_field}...")
    
    # Define base feature sets
    numerical_features = [
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
    
    # If previous predictions are provided, add them as features
    if previous_predictions:
        for prev_field, prev_pred in previous_predictions.items():
            df[f'{prev_field}_prediction'] = prev_pred
            numerical_features.append(f'{prev_field}_prediction')
    
    # Create preprocessing pipeline for numerical features only
    preprocessor = StandardScaler()
    
    return preprocessor, df[numerical_features], df[f'{career_field}_encoded']

def train_model(X, y, preprocessor, career_field):
    """
    Train the model using cross-validation and hyperparameter tuning.
    """
    logger.info(f"Training model for {career_field} with cross-validation...")
    
    # Define parameter grid for hyperparameter tuning
    param_grid = {
        'n_estimators': [100, 200],
        'learning_rate': [0.1, 0.2],
        'max_depth': [3, 4],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2]
    }
    
    # Create classifier
    classifier = GradientBoostingClassifier(random_state=42)
    
    # Perform grid search with cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    grid_search = GridSearchCV(
        classifier, 
        param_grid, 
        cv=cv, 
        scoring='f1_weighted',
        n_jobs=-1,
        verbose=2
    )
    
    # Scale features and fit the model
    X_scaled = preprocessor.fit_transform(X)
    grid_search.fit(X_scaled, y)
    
    logger.info(f"Best parameters for {career_field}: {grid_search.best_params_}")
    logger.info(f"Best cross-validation score for {career_field}: {grid_search.best_score_:.4f}")
    
    return grid_search.best_estimator_, preprocessor

def evaluate_model(model, preprocessor, X_test, y_test, career_field):
    """
    Evaluate the model's performance on test data.
    """
    logger.info(f"Evaluating model performance for {career_field}...")
    
    # Scale features and make predictions
    X_test_scaled = preprocessor.transform(X_test)
    y_pred = model.predict(X_test_scaled)
    
    # Print classification report
    logger.info(f"\nClassification Report for {career_field}:")
    logger.info(classification_report(y_test, y_pred))
    
    # Print confusion matrix
    logger.info(f"\nConfusion Matrix for {career_field}:")
    logger.info(confusion_matrix(y_test, y_pred))

def main():
    """
    Main function to execute the model training pipeline.
    """
    # Load and preprocess data
    df, le_career = load_and_preprocess_data()
    
    # Perform feature engineering
    df = feature_engineering(df)
    
    # Split data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        df, 
        df['career_1_encoded'],  # We'll use career_1 for initial split
        test_size=0.2, 
        stratify=df['career_1_encoded'],
        random_state=42
    )
    
    # Train models sequentially
    models = {}
    preprocessors = {}
    
    # Train career_1 model (no previous predictions)
    preprocessor, X, y = prepare_features_and_target(X_train, 'career_1')
    model, preprocessor = train_model(X, y, preprocessor, 'career_1')
    models['career_1'] = model
    preprocessors['career_1'] = preprocessor
    
    # Get predictions from career_1 model for training career_2
    X_train_scaled = preprocessor.transform(X)
    career_1_predictions = model.predict(X_train_scaled)
    
    # Train career_2 model (with career_1 predictions)
    preprocessor, X, y = prepare_features_and_target(
        X_train, 
        'career_2', 
        {'career_1': career_1_predictions}
    )
    model, preprocessor = train_model(X, y, preprocessor, 'career_2')
    models['career_2'] = model
    preprocessors['career_2'] = preprocessor
    
    # Get predictions from career_1 and career_2 models for training career_3
    career_2_predictions = model.predict(preprocessor.transform(X))
    
    # Train career_3 model (with career_1 and career_2 predictions)
    preprocessor, X, y = prepare_features_and_target(
        X_train, 
        'career_3', 
        {
            'career_1': career_1_predictions,
            'career_2': career_2_predictions
        }
    )
    model, preprocessor = train_model(X, y, preprocessor, 'career_3')
    models['career_3'] = model
    preprocessors['career_3'] = preprocessor
    
    # Save all models and preprocessors
    logger.info("Saving models and preprocessors...")
    for career_field in ['career_1', 'career_2', 'career_3']:
        joblib.dump(models[career_field], f'ml_models/{career_field}_model.pkl')
        joblib.dump(preprocessors[career_field], f'ml_models/{career_field}_preprocessor.pkl')
    
    logger.info("Model training completed successfully!")

if __name__ == "__main__":
    main() 