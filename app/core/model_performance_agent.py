import pandas as pd
from sklearn.metrics import classification_report, accuracy_score
from typing import Dict, Any

class ModelPerformanceAgent:
    """
    An agent dedicated to evaluating a model's performance against a ground truth in the dataset.
    """
    def __init__(self):
        """Initializes the ModelPerformanceAgent."""
        print("ModelPerformanceAgent is ready.")

    def evaluate_performance(self, model, dataframe: pd.DataFrame, features: list, target_column: str) -> Dict[str, Any]:
        """
        Calculates performance metrics for the given model and data.
        """
        print("\n--- Running Model Performance Evaluation ---")
        
        # *** FIX IS HERE: Added robust try-except block for error handling ***
        try:
            if target_column not in dataframe.columns:
                return {"status": "FAILURE", "message": f"Ground truth column '{target_column}' not found in dataset."}
            
            if not all(f in dataframe.columns for f in features):
                missing = [f for f in features if f not in dataframe.columns]
                return {"status": "FAILURE", "message": f"Data is missing features the model requires: {missing}"}

            X_test = dataframe[features]
            y_true = dataframe[target_column]

            # Generate predictions
            y_pred = model.predict(X_test)

            # Calculate metrics
            accuracy = accuracy_score(y_true, y_pred)
            report_dict = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
            
            print("Performance evaluation complete.")
            
            performance_report = {
                "status": "SUCCESS",
                "accuracy": accuracy,
                "classification_report": report_dict
            }
            return performance_report

        except Exception as e:
            error_message = f"An error occurred during performance evaluation: {e}"
            print(error_message)
            return {"status": "FAILURE", "message": error_message}
