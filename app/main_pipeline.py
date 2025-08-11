import pandas as pd
import json
import os
import sys
import joblib

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import all agents
from app.core.rkb_loader import RegulatoryKnowledgeBase
from app.core.data_validator import DataMappingAgent
from app.core.compliance_checker import ComplianceCheckerAgent
from app.core.xai_inspector import XAIInspectorAgent
from app.core.voting_agent import VotingAgent
from app.core.report_generator import ReportAgent
from app.core.model_performance_agent import ModelPerformanceAgent
from app.core.utils import CustomJSONEncoder

def run_full_audit_pipeline():
    """
    An interactive command-line tool to run the entire 6-agent audit pipeline.
    """
    # 1. Initialize all agents
    try:
        rkb_instance = RegulatoryKnowledgeBase()
        validator_agent = DataMappingAgent(rkb=rkb_instance)
        checker_agent = ComplianceCheckerAgent(rkb=rkb_instance)
        performance_agent = ModelPerformanceAgent()
        inspector_agent = XAIInspectorAgent()
        voting_agent = VotingAgent()
        report_agent = ReportAgent()
        print("\n--- All Agents Initialized and Ready ---")
    except Exception as e:
        print(f"Failed to initialize agents. Error: {e}")
        return

    # 2. Start the interactive loop
    while True:
        try:
            # --- Get User Inputs ---
            file_path = input("\nEnter the path to your data file (with ground truth) (or 'exit' to quit): ")
            if file_path.lower() == 'exit':
                print("Exiting tool.")
                break
            
            model_path = input("Enter the path to your pre-trained model file (.pkl): ")
            agency_key = input("Enter the agency key to audit against (e.g., cpcb_standards): ")
            target_column = input("Enter the name of the ground truth column in your data file (e.g., PM2_5_High): ")

            if not os.path.exists(file_path) or not os.path.exists(model_path):
                print(f"Error: One or more files not found. Please check paths and try again.")
                continue

            # --- Agent 1: Data Validation ---
            validation_report = validator_agent.run_validation(file_path, agency_key)
            if validation_report.get("status") != "SUCCESS":
                print("\nAudit failed at Validation stage.")
                print(json.dumps(validation_report, indent=2, cls=CustomJSONEncoder))
                continue

            # --- Load data and model once ---
            if file_path.endswith('.csv'): df = pd.read_csv(file_path)
            else: df = pd.read_excel(file_path)
            model = joblib.load(model_path)

            # --- Agent 2: Compliance Checking ---
            compliance_report, processed_df = checker_agent.run_checker(df, agency_key)
            if compliance_report.get("status") != "SUCCESS":
                print("\nAudit stopped at Compliance Checking stage.")
                print(json.dumps(compliance_report, indent=2, cls=CustomJSONEncoder))
                continue

            # --- Agent 3: Model Performance ---
            model_features = ['PM10', 'NO2', 'O3', 'CO', 'SO2', 'NH3', 'PB', 'Temperature']
            performance_report = performance_agent.evaluate_performance(model, df, model_features, target_column)
            if performance_report.get("status") != "SUCCESS":
                print("\nAudit stopped at Performance Evaluation stage.")
                print(json.dumps(performance_report, indent=2, cls=CustomJSONEncoder))
                continue

            # --- Agent 4: XAI Inspection ---
            xai_report = inspector_agent.run_inspector(df, model_path, model_features)
            if xai_report.get("status") != "SUCCESS":
                print("\nAudit stopped at XAI Inspection stage.")
                print(json.dumps(xai_report, indent=2, cls=CustomJSONEncoder))
                continue

            # --- Agent 5 & 6: Voting and Reporting ---
            final_report = voting_agent.run_voter(validation_report, compliance_report, xai_report, performance_report)
            report_file_path = report_agent.generate_report(final_report)
            
            print("\n--- AUDIT COMPLETE ---")
            print(f"Final Grade: {final_report['final_compliance_grade']}")
            print(f"A detailed HTML report has been saved to: {report_file_path}")
            print("----------------------\n")

        except Exception as e:
            print(f"\nAn unexpected error occurred in the main pipeline: {e}")
            print("Restarting audit loop...")
            continue


if __name__ == "__main__":
    run_full_audit_pipeline()
