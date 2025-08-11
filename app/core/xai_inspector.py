import pandas as pd
import shap
import joblib
import matplotlib.pyplot as plt
import os
from typing import Dict, Any, List

class XAIInspectorAgent:
    """
    An agent that loads a user-provided, pre-trained model and uses SHAP
    to explain its predictions on a given dataset.
    """
    def __init__(self):
        """Initializes the XAI agent."""
        self.reports_dir = 'reports'
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
        print("XAIInspectorAgent is ready.")

    def _load_user_model(self, model_path: str):
        """Loads a pre-trained model from a file path."""
        print(f"Loading user model from: {model_path}")
        try:
            model = joblib.load(model_path)
            print("User model loaded successfully.")
            return model, None
        except FileNotFoundError:
            return None, f"Model file not found at {model_path}"
        except Exception as e:
            return None, f"Error loading model: {e}"

    def generate_global_explanation(self, model, feature_data: pd.DataFrame) -> str:
        """Generates and saves a SHAP summary plot for global feature importance."""
        print("Generating global explanation (SHAP)...")
        explainer = shap.Explainer(model.predict, feature_data)
        shap_values = explainer(feature_data)
        plt.figure()
        shap.summary_plot(shap_values, feature_data, plot_type="bar", show=False)
        plot_path = os.path.join(self.reports_dir, 'shap_summary_plot.png')
        plt.savefig(plot_path, bbox_inches='tight')
        plt.close()
        print(f"SHAP summary plot saved to {plot_path}")
        return plot_path

    def run_inspector(self, dataframe: pd.DataFrame, model_path: str, model_features: List[str]) -> Dict[str, Any]:
        """
        Runs the full XAI inspection pipeline using a user-provided model.
        """
        try:
            model, error_msg = self._load_user_model(model_path)
            if model is None:
                return {"status": "FAILURE", "message": error_msg}

            if not all(feature in dataframe.columns for feature in model_features):
                missing = [f for f in model_features if f not in dataframe.columns]
                return {"status": "FAILURE", "message": f"Data is missing features the model requires: {missing}"}

            X = dataframe[model_features]

            shap_plot_path = self.generate_global_explanation(model, X)

            xai_report = {
                "status": "SUCCESS",
                "message": "XAI analysis on user model completed.",
                "model_path": model_path,
                "global_explanation": {
                    "tool": "SHAP",
                    "summary_plot_path": shap_plot_path,
                    "description": "This plot shows the overall importance of each feature for the provided model's predictions."
                }
            }
            return xai_report
        except Exception as e:
            error_message = f"An error occurred during XAI inspection: {e}"
            print(error_message)
            return {"status": "FAILURE", "message": error_message}
