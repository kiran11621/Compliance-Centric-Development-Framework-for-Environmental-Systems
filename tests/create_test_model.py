import pandas as pd
import sklearn.ensemble
import joblib
import os

def create_and_save_model(data_path='sample_air_quality_data.xlsx', model_output_path='air_quality_model.pkl'):
    """
    Trains a model and saves both the model and the data with the ground truth column.
    This script will overwrite existing files to ensure they are always up-to-date.
    """
    print(f"Generating fresh sample data and model...")
    
    sample_data = {
        'PM2_5': [25.5, 65.1, 95.8, 130.2, 260.5, 15.2, 45.9, 80.3, 110.6, 200.1],
        'PM10': [55.2, 110.5, 260.1, 360.7, 440.3, 40.1, 80.7, 200.4, 300.9, 400.5],
        'NO2': [35.1, 75.3, 190.7, 290.4, 410.6, 25.8, 60.2, 150.9, 250.2, 350.8],
        'O3': [45.8, 95.2, 170.3, 210.1, 750.9, 30.5, 80.1, 150.6, 190.4, 500.3],
        'CO': [0.8, 1.5, 11.2, 18.5, 35.1, 0.5, 1.2, 8.9, 15.3, 25.6],
        'SO2': [35.6, 70.1, 390.8, 810.2, 1650.4, 25.3, 60.7, 350.1, 750.8, 1200.2],
        'NH3': [180.5, 350.2, 850.7, 1250.3, 1850.1, 150.9, 300.6, 750.4, 1100.9, 1600.5],
        'PB': [0.4, 0.9, 2.2, 3.1, 3.8, 0.2, 0.7, 1.9, 2.8, 3.4],
        'Temperature': [28.5, 29.1, 30.5, 31.2, 32.0, 27.8, 28.9, 30.1, 30.9, 31.5]
    }
    df = pd.DataFrame(sample_data)

    # Create the ground truth column
    df['PM2_5_High'] = (df['PM2_5'] >= 90).astype(int)
    
    # Save the complete dataframe WITH the ground truth column
    df.to_excel(data_path, index=False)
    print(f"Sample data with ground truth saved to '{data_path}'")
    
    features = ['PM10', 'NO2', 'O3', 'CO', 'SO2', 'NH3', 'PB', 'Temperature']
    target = 'PM2_5_High'
    X = df[features]
    y = df[target]

    print("Training a RandomForest model...")
    model = sklearn.ensemble.RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    print("Model training complete.")

    joblib.dump(model, model_output_path)
    print(f"Model successfully saved to: {model_output_path}")

if __name__ == "__main__":
    create_and_save_model()
