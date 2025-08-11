# import os
# import json
# from typing import Dict, Any
# import google.generativeai as genai


# import os
# import json
# from typing import Dict, Any
# import google.generativeai as genai

# class VotingAgent:
#     """
#     An agent that combines results from all other agents, calculates a weighted
#     compliance score, assigns a final grade, and uses an LLM to generate a deep analysis.
#     """
#     def __init__(self):
#         """Initializes the VotingAgent and configures the LLM."""
#         self.final_report = {}
#         try:
#             api_key = ""
#             if not api_key:
#                 print("Warning: GOOGLE_API_KEY environment variable not found. LLM summary will be skipped.")
#                 self.llm_configured = False
#             else:
#                 genai.configure(api_key=api_key)
#                 self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
#                 self.llm_configured = True
#             print("VotingAgent is ready.")
#         except Exception as e:
#             print(f"Error initializing Google Gemini: {e}")
#             self.llm_configured = False

#     def _calculate_scores(self, validation_report: Dict, compliance_report: Dict, performance_report: Dict) -> Dict[str, float]:
#         """Calculates individual scores based on the reports from other agents."""
#         scores = {}
#         vr = validation_report['feature_presence']
#         total_required = len(validation_report['required_features'])
#         scores['feature_compliance'] = (len(vr['present_features']) / total_required) * 100 if total_required > 0 else 0
#         score_str = compliance_report.get('compliance_score_percent', '0%').replace('%', '')
#         scores['threshold_accuracy'] = float(score_str)
#         scores['xai_trust_score'] = 85.0  # Placeholder
#         # NEW: Use the actual accuracy from the performance report
#         scores['performance_metrics'] = performance_report.get('accuracy', 0) * 100
#         return scores

#     def _calculate_final_grade(self, scores: Dict) -> (str, float):
#         """Calculates the final weighted score and assigns a letter grade."""
#         weights = { 'feature_compliance': 0.40, 'threshold_accuracy': 0.30, 'xai_trust_score': 0.20, 'performance_metrics': 0.10 }
#         final_score = sum(scores[key] * weights[key] for key in scores)
#         if final_score >= 90: grade = 'A'
#         elif final_score >= 80: grade = 'B'
#         elif final_score >= 70: grade = 'C'
#         elif final_score >= 60: grade = 'D'
#         else: grade = 'F'
#         return grade, final_score

#     def _generate_llm_summary(self, final_report: Dict) -> str:
#         """Generates a human-readable summary using the Gemini LLM."""
#         if not self.llm_configured:
#             return "LLM summary skipped because the Google API key is not configured."
#         print("Generating enhanced LLM analysis...")
#         try:
#             # Create a much more detailed report for the prompt
#             prompt_data = {
#                 "Final Grade": final_report['final_compliance_grade'],
#                 "Overall Score": f"{final_report['final_weighted_score']:.2f}%",
#                 "Model Performance": {
#                     "Accuracy": f"{final_report['performance_report']['accuracy']:.2%}",
#                     "Classification Report": final_report['performance_report']['classification_report']['weighted avg']
#                 },
#                 "Compliance Findings": {
#                     "Feature Compliance": f"{final_report['component_scores']['feature_compliance']:.2f}%",
#                     "Threshold Accuracy": f"{final_report['component_scores']['threshold_accuracy']:.2f}%",
#                     "Category Distribution": final_report['compliance_report']['category_distribution']
#                 },
#                 "XAI Insights": "SHAP plot generated, showing feature importances."
#             }
#             prompt = f"""
#             As an expert AI compliance auditor, provide a deep, analytical explanation of the following audit report.
#             Do not just summarize. Analyze the interplay between the model's performance (accuracy, precision, recall) and its regulatory compliance.
#             For example, does the model perform well but fail on compliance, or vice-versa?
#             What are the key risks and recommendations based on these combined findings?

#             Audit Report:
#             {json.dumps(prompt_data, indent=2)}

#             Your In-Depth Analysis:
#             """
#             response = self.model.generate_content(prompt)
#             return response.text
#         except Exception as e:
#             return f"LLM summary generation failed. Error: {e}"

#     def run_voter(self, validation_report: Dict, compliance_report: Dict, xai_report: Dict, performance_report: Dict) -> Dict[str, Any]:
#         """Runs the full voting and summarization pipeline."""
#         print("\n--- Running Voting Agent ---")
#         scores = self._calculate_scores(validation_report, compliance_report, performance_report)
#         grade, final_score = self._calculate_final_grade(scores)
#         self.final_report = {
#             "audited_file": validation_report['file_path'],
#             "agency": validation_report['agency'],
#             "final_compliance_grade": grade,
#             "final_weighted_score": final_score,
#             "component_scores": scores,
#             "llm_summary": "Pending...",
#             "validation_report": validation_report,
#             "compliance_report": compliance_report,
#             "xai_report": xai_report,
#             "performance_report": performance_report # Add new report
#         }
#         summary = self._generate_llm_summary(self.final_report)
#         self.final_report["llm_summary"] = summary
#         print("Voting Agent finished.")
#         return self.final_report

import os
import json
from typing import Dict, Any
import google.generativeai as genai
import markdown # <-- NEW: For converting Markdown to HTML

class VotingAgent:
    """
    An agent that combines results from all other agents, calculates a weighted
    compliance score, assigns a final grade, and uses an LLM to generate a deep analysis.
    """
    def __init__(self):
        """Initializes the VotingAgent and configures the LLM."""
        self.final_report = {}
        try:
            api_key = ""
            if not api_key:
                print("Warning: GOOGLE_API_KEY environment variable not found. LLM summary will be skipped.")
                self.llm_configured = False
            else:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
                self.llm_configured = True
            print("VotingAgent is ready.")
        except Exception as e:
            print(f"Error initializing Google Gemini: {e}")
            self.llm_configured = False

    def _calculate_scores(self, validation_report: Dict, compliance_report: Dict, performance_report: Dict) -> Dict[str, float]:
        """Calculates individual scores based on the reports from other agents."""
        scores = {}
        vr = validation_report['feature_presence']
        total_required = len(validation_report['required_features'])
        scores['feature_compliance'] = (len(vr['present_features']) / total_required) * 100 if total_required > 0 else 0
        score_str = compliance_report.get('compliance_score_percent', '0%').replace('%', '')
        scores['threshold_accuracy'] = float(score_str)
        scores['xai_trust_score'] = 85.0  # Placeholder
        scores['performance_metrics'] = performance_report.get('accuracy', 0) * 100
        return scores

    def _calculate_final_grade(self, scores: Dict) -> (str, float):
        """Calculates the final weighted score and assigns a letter grade."""
        weights = { 'feature_compliance': 0.40, 'threshold_accuracy': 0.30, 'xai_trust_score': 0.20, 'performance_metrics': 0.10 }
        final_score = sum(scores[key] * weights[key] for key in scores)
        if final_score >= 90: grade = 'A'
        elif final_score >= 80: grade = 'B'
        elif final_score >= 70: grade = 'C'
        elif final_score >= 60: grade = 'D'
        else: grade = 'F'
        return grade, final_score

    def _generate_llm_summary(self, final_report: Dict) -> str:
        """Generates a human-readable summary using the Gemini LLM."""
        if not self.llm_configured:
            return "LLM summary skipped because the Google API key is not configured."
        print("Generating enhanced LLM analysis...")
        try:
            prompt_data = {
                "Final Grade": final_report['final_compliance_grade'],
                "Overall Score": f"{final_report['final_weighted_score']:.2f}%",
                "Model Performance": {
                    "Accuracy": f"{final_report['performance_report']['accuracy']:.2%}",
                    "Classification Report (Weighted Avg)": final_report['performance_report']['classification_report']['weighted avg']
                },
                "Compliance Findings": {
                    "Feature Compliance": f"{final_report['component_scores']['feature_compliance']:.2f}%",
                    "Threshold Accuracy": f"{final_report['component_scores']['threshold_accuracy']:.2f}%",
                    "Data Category Distribution": final_report['compliance_report']['category_distribution']
                }
            }
            # *** NEW, ENHANCED PROMPT ***
            prompt = f"""
            As an expert AI compliance auditor, provide a deep, analytical explanation of the following audit report using Markdown for formatting (e.g., **bold** for headings).
            Do not just summarize. Analyze the interplay between the model's performance (accuracy, precision, recall) and its regulatory compliance.
            For example, does the model perform well but fail on compliance, or vice-versa?
            Based on all the data, identify the key risks and provide a numbered list of actionable recommendations.

            Audit Report Data:
            {json.dumps(prompt_data, indent=2)}

            Your In-Depth Analysis:
            """
            response = self.model.generate_content(prompt)
            # *** FIX IS HERE: Convert Markdown response to HTML ***
            return markdown.markdown(
                    response.text.strip(),
                    extensions=['nl2br']
                )

        except Exception as e:
            return f"LLM summary generation failed. Error: {e}"

    def run_voter(self, validation_report: Dict, compliance_report: Dict, xai_report: Dict, performance_report: Dict) -> Dict[str, Any]:
        """Runs the full voting and summarization pipeline."""
        print("\n--- Running Voting Agent ---")
        scores = self._calculate_scores(validation_report, compliance_report, performance_report)
        grade, final_score = self._calculate_final_grade(scores)
        self.final_report = {
            "audited_file": validation_report['file_path'], "agency": validation_report['agency'],
            "final_compliance_grade": grade, "final_weighted_score": final_score,
            "component_scores": scores, "llm_summary": "Pending...",
            "validation_report": validation_report, "compliance_report": compliance_report,
            "xai_report": xai_report, "performance_report": performance_report
        }
        summary = self._generate_llm_summary(self.final_report)
        self.final_report["llm_summary"] = summary
        print("Voting Agent finished.")
        return self.final_report
