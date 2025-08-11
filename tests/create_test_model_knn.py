import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import joblib
import os

def create_and_save_knn_model(
    data_output_path='noncompliant_data_50.xlsx', 
    model_output_path='knn_noncompliant_model.pkl'
):
    """
    Generates a larger dataset (50 records) and trains an intentionally non-compliant
    K-Nearest Neighbors (KNN) model on it. The model is non-compliant because it is
    trained on an incomplete set of features.
    """
    print(f"Generating a new 50-record dataset and a non-compliant KNN model...")

    # 1. Generate a larger, more realistic dataset with 50 records
    np.random.seed(42) # for reproducibility
    num_records = 100
    data = {
        'PM2_5': np.random.uniform(10, 300, num_records),
        'PM10': np.random.uniform(20, 500, num_records),
        'NO2': np.random.uniform(10, 450, num_records),
        'O3': np.random.uniform(20, 800, num_records),
        'CO': np.random.uniform(0.5, 40, num_records),
        'SO2': np.random.uniform(10, 1800, num_records),
        'NH3': np.random.uniform(100, 2000, num_records),
        'PB': np.random.uniform(0.1, 4.0, num_records),
        'Temperature': np.random.uniform(20, 35, num_records)
    }
    df = pd.DataFrame(data)
    
    # Create the ground truth column based on the generated PM2.5 values
    df['PM2_5_High'] = (df['PM2_5'] >= 90).astype(int)

    # Save the new, larger dataset to an Excel file
    df.to_excel(data_output_path, index=False)
    print(f"New 50-record dataset with ground truth saved to: '{data_output_path}'")

    # 2. Train the intentionally non-compliant model
    # --- INTENTIONAL NON-COMPLIANCE ---
    # This model is trained on only a small subset of the required features.
    # A proper audit should flag this model for missing critical pollutants.
    non_compliant_features = ['Temperature', 'CO', 'O3']
    target = 'PM2_5_High'

    print(f"Training a KNN model on a non-compliant, incomplete feature set: {non_compliant_features}")

    X = df[non_compliant_features]
    y = df[target]

    # Train a K-Nearest Neighbors model
    model = KNeighborsClassifier(n_neighbors=5)
    model.fit(X, y)
    print("Non-compliant KNN model training complete.")

    # 3. Save the trained model to a file
    joblib.dump(model, model_output_path)
    print(f"Non-compliant model successfully saved to: {model_output_path}")

if __name__ == "__main__":
    create_and_save_knn_model()
