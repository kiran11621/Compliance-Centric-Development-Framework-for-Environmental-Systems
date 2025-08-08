import os
import json
from typing import Dict, Any

# You will need to install the Google AI Python SDK:
# pip install google-generativeai
import google.generativeai as genai

class VotingAgent:
    """
    An agent that combines results from all other agents, calculates a weighted
    compliance score, assigns a final grade, and uses an LLM to generate a summary.
    """

    def __init__(self):
        """Initializes the VotingAgent and configures the LLM."""
        self.final_report = {}
        try:
            # IMPORTANT: Set your Google API Key as an environment variable
            # For example: export GOOGLE_API_KEY="YOUR_API_KEY"
            api_key = ""
            if not api_key:
                print("Warning: GOOGLE_API_KEY environment variable not found. LLM summary will be skipped.")
                self.llm_configured = False
            else:
                genai.configure(api_key=api_key)
                # *** FIX IS HERE: Updated to a current, valid model name ***
                self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
                self.llm_configured = True
            print("VotingAgent is ready.")
        except Exception as e:
            print(f"Error initializing Google Gemini: {e}")
            self.llm_configured = False


    def _calculate_scores(self, validation_report: Dict, compliance_report: Dict) -> Dict[str, float]:
        """Calculates individual scores based on the reports from other agents."""
        scores = {}

        # 1. Feature Compliance Score (Weight: 40%)
        vr = validation_report['feature_presence']
        total_required = len(validation_report['required_features'])
        # Score is the percentage of required features that are present.
        scores['feature_compliance'] = (len(vr['present_features']) / total_required) * 100 if total_required > 0 else 0

        # 2. Threshold Accuracy Score (Weight: 30%)
        # This is the compliance score from the checker agent.
        score_str = compliance_report.get('compliance_score_percent', '0%').replace('%', '')
        scores['threshold_accuracy'] = float(score_str)

        # For the other scores, we would typically need a real ML model's performance metrics.
        # For this simulation, we'll assign placeholder scores.
        # 3. XAI Trust Score (Weight: 20%) - Placeholder
        scores['xai_trust_score'] = 85.0  # Placeholder

        # 4. Performance Metrics (Weight: 10%) - Placeholder
        scores['performance_metrics'] = 90.0 # Placeholder
        
        return scores

    def _calculate_final_grade(self, scores: Dict) -> (str, float):
        """Calculates the final weighted score and assigns a letter grade."""
        weights = {
            'feature_compliance': 0.40,
            'threshold_accuracy': 0.30,
            'xai_trust_score': 0.20,
            'performance_metrics': 0.10
        }
        
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

        print("Generating LLM summary...")
        try:
            # Create a simplified report for the prompt
            prompt_data = {
                "Final Grade": final_report['final_compliance_grade'],
                "Overall Score": f"{final_report['final_weighted_score']:.2f}%",
                "File Audited": final_report['audited_file'],
                "Agency Standard": final_report['agency'],
                "Key Findings": {
                    "Feature Compliance": f"{final_report['component_scores']['feature_compliance']:.2f}%",
                    "Threshold Accuracy": f"{final_report['component_scores']['threshold_accuracy']:.2f}%",
                    "Data Quality Issues": "None" if not final_report['validation_report']['schema_errors'] else "Present"
                }
            }

            prompt = f"""
            As an AI compliance auditor, analyze the following audit report summary and provide a brief, professional explanation.
            Explain the final grade and highlight the most important findings.

            Audit Report:
            {json.dumps(prompt_data, indent=2)}

            Your Summary:
            """
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"LLM summary generation failed. Error: {e}"

    def run_voter(self, validation_report: Dict, compliance_report: Dict, xai_report: Dict) -> Dict[str, Any]:
        """
        Runs the full voting and summarization pipeline.
        """
        print("\n--- Running Voting Agent ---")
        
        # 1. Calculate individual component scores
        scores = self._calculate_scores(validation_report, compliance_report)
        
        # 2. Calculate final grade
        grade, final_score = self._calculate_final_grade(scores)
        
        # 3. Assemble the final report object
        self.final_report = {
            "audited_file": validation_report['file_path'],
            "agency": validation_report['agency'],
            "final_compliance_grade": grade,
            "final_weighted_score": final_score,
            "component_scores": scores,
            "llm_summary": "Pending...",
            "validation_report": validation_report,
            "compliance_report": compliance_report,
            "xai_report": xai_report
        }
        
        # 4. Generate LLM Summary
        summary = self._generate_llm_summary(self.final_report)
        self.final_report["llm_summary"] = summary
        
        print("Voting Agent finished.")
        return self.final_report
