import pandas as pd
import shap
import lime
import lime.lime_tabular
import sklearn
import sklearn.ensemble
import matplotlib.pyplot as plt
import os
from typing import Dict, Any, List

class XAIInspectorAgent:
    """
    An agent that explains the patterns in the data by training a surrogate model
    and using SHAP and LIME to assess feature importance and local explanations.
    """

    def __init__(self):
        """Initializes the XAI agent."""
        self.reports_dir = 'reports'
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
        print("XAIInspectorAgent is ready.")

    def _train_surrogate_model(self, dataframe: pd.DataFrame, features: List[str], target: str):
        """Trains a RandomForest model to act as a surrogate for explaining data patterns."""
        print("Training surrogate model...")
        le = sklearn.preprocessing.LabelEncoder()
        y = le.fit_transform(dataframe[target])
        X = dataframe[features]
        model = sklearn.ensemble.RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        print("Surrogate model trained successfully.")
        return model, X, y, le

    def generate_global_explanation(self, model, feature_data: pd.DataFrame) -> str:
        """Generates and saves a SHAP summary plot for global feature importance."""
        print("Generating global explanation (SHAP)...")
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(feature_data)
        
        if isinstance(shap_values, list):
            shap_values_summary = abs(shap_values[0])
            for i in range(1, len(shap_values)):
                shap_values_summary += abs(shap_values[i])
            shap_values_summary /= len(shap_values)
        else:
            shap_values_summary = shap_values

        plt.figure()
        shap.summary_plot(shap_values_summary, feature_data, plot_type="bar", show=False)
        plot_path = os.path.join(self.reports_dir, 'shap_summary_plot.png')
        plt.savefig(plot_path, bbox_inches='tight')
        plt.close()
        print(f"SHAP summary plot saved to {plot_path}")
        return plot_path

    def generate_local_explanation(self, model, X_train: pd.DataFrame, instance_index: int, le: sklearn.preprocessing.LabelEncoder):
        """Generates a LIME explanation for a single data instance."""
        print(f"Generating local explanation (LIME) for instance {instance_index}...")
        explainer = lime.lime_tabular.LimeTabularExplainer(
            training_data=X_train.values,
            feature_names=X_train.columns,
            class_names=le.classes_,
            mode='classification'
        )
        explanation = explainer.explain_instance(
            data_row=X_train.iloc[instance_index],
            predict_fn=model.predict_proba
        )
        return explanation.as_list()

    def run_inspector(self, processed_dataframe: pd.DataFrame) -> Dict[str, Any]:
        """
        Runs the full XAI inspection pipeline on the processed dataframe.
        """
        target_col = next((col for col in processed_dataframe.columns if col.endswith('_Category')), None)
        if not target_col:
            return {"status": "FAILURE", "message": "No compliance category column found to use as a target for XAI."}

        feature_cols = [col for col in processed_dataframe.columns if col not in [target_col] and processed_dataframe[col].dtype in ['int64', 'float64']]
        
        model, X, y, label_encoder = self._train_surrogate_model(processed_dataframe, feature_cols, target_col)
        shap_plot_path = self.generate_global_explanation(model, X)
        lime_explanation = self.generate_local_explanation(model, X, 0, label_encoder)

        xai_report = {
            "status": "SUCCESS",
            "message": "XAI analysis completed.",
            "global_explanation": { "tool": "SHAP", "summary_plot_path": shap_plot_path },
            "local_explanation_sample": { "tool": "LIME", "instance_index": 0, "explanation": lime_explanation }
        }
        return xai_report
