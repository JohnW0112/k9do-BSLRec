import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

def load_and_preprocess_data():
    # Load the datasets
    print("Loading datasets...")
    one_hand_data = pd.read_csv('one_hand_landmark_modified.csv')
    two_hand_data = pd.read_csv('two_hand_landmark_modified.csv')
    
    # Combine the datasets
    combined_data = pd.concat([one_hand_data, two_hand_data], ignore_index=True)
    
    # Separate features and target
    X = combined_data.drop('label', axis=1)  # Assuming 'label' is the target column
    y = combined_data['label']
    
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    
    return X_train_scaled, X_test_scaled, y_train, y_test

def train_model(X_train, y_train):
    print("Training the model...")
    # Initialize and train the Random Forest Classifier
    model = RandomForestClassifier(
        n_estimators=100,      # Reduce trees to prevent overfitting
        max_depth=5,          # Limit depth to prevent learning noise
        min_samples_split=5,  # Require more samples per split
        min_samples_leaf=3,   # Ensure each leaf has sufficient samples
        max_features='sqrt',  # Limit features considered for splits
        random_state=42
)
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    print("Evaluating the model...")
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Print classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Print confusion matrix
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

def main():
    # Create a directory for saving models if it doesn't exist
  
    
    # Load and preprocess data
    X_train, X_test, y_train, y_test = load_and_preprocess_data()
    
    # Train the model
    model = train_model(X_train, y_train)
    
    # Evaluate the model
    evaluate_model(model, X_test, y_test)
    
    # Save the model
    print("\nSaving the model...")
    joblib.dump(model, 'hand_landmark_model.joblib')
    print("Model saved successfully!")

if __name__ == "__main__":
    main() 