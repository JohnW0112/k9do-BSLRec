import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

def load_and_preprocess_data(data):
    # Separate features and target
    X = data.drop('label', axis=1)  # Assuming 'label' is the target column
    y = data['label']
    
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Scale the features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler

def train_model(X_train, y_train):
    print("Training the model...")
    # Initialize and train the Random Forest Classifier
    model = RandomForestClassifier(
        n_estimators=5,       # Fewer trees to prevent overfitting
        max_depth=3,          # Shallower trees to reduce complexity
        max_features='sqrt',  # Limits feature usage per split
        min_samples_split=4,  # Prevents splitting on very small subsets
        min_samples_leaf=2,   # Ensures stability in leaf nodes
        bootstrap=True,       # Keeps some randomness to improve generalization
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

    # Load datasets
    one_hand_data = pd.read_csv('one_hand_landmark_modified.csv')
    two_hand_data = pd.read_csv('two_hand_landmark_modified.csv')
    
    # Process and train model for one-hand data
    X_train_1h, X_test_1h, y_train_1h, y_test_1h, scaler_1h = load_and_preprocess_data(one_hand_data)
    model_1h = train_model(X_train_1h, y_train_1h)
    evaluate_model(model_1h, X_test_1h, y_test_1h)
    y1_pred = model_1h.predict(X_test_1h)
    print("Testing score =", accuracy_score(y_test_1h, y1_pred))
    joblib.dump(model_1h, 'one_hand_model.joblib')
    print("One-hand model saved successfully!")
    
    # Process and train model for two-hand data
    X_train_2h, X_test_2h, y_train_2h, y_test_2h, scaler_2h = load_and_preprocess_data(two_hand_data)
    model_2h = train_model(X_train_2h, y_train_2h)
    evaluate_model(model_2h, X_test_2h, y_test_2h)
    y2_pred = model_2h.predict(X_test_2h)
    print("Testing score =", accuracy_score(y_test_2h, y2_pred))
    joblib.dump(model_2h, 'two_hand_model.joblib')
    print("Two-hand model saved successfully!")

if __name__ == "__main__":
    main()
