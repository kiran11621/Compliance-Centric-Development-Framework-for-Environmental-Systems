import pandas as pd
import json
import os

# Import all agents and the new custom encoder
from core.rkb_loader import RegulatoryKnowledgeBase
from core.data_validator import DataMappingAgent
from core.compliance_checker import ComplianceCheckerAgent
from core.xai_inspector import XAIInspectorAgent
from core.voting_agent import VotingAgent
from core.report_generator import ReportAgent
from core.utils import CustomJSONEncoder

def run_full_audit_pipeline():
    """
    An interactive command-line tool to run the entire 5-agent audit pipeline.
    """
    # 1. Initialize all agents
    try:
        rkb_instance = RegulatoryKnowledgeBase()
        validator_agent = DataMappingAgent(rkb=rkb_instance)
        checker_agent = ComplianceCheckerAgent(rkb=rkb_instance)
        inspector_agent = XAIInspectorAgent()
        voting_agent = VotingAgent()
        report_agent = ReportAgent()
        print("\n--- All Agents Initialized and Ready ---")
    except Exception as e:
        print(f"Failed to initialize agents. Error: {e}")
        return

    # 2. Start the interactive loop
    while True:
        file_path = input("\nEnter the path to your CSV or Excel file (or 'exit' to quit): ")
        if file_path.lower() == 'exit':
            print("Exiting tool.")
            break
        
        agency_key = input("Enter the agency key to audit against (e.g., cpcb_standards): ")

        if not os.path.exists(file_path):
            print(f"Error: File not found at '{file_path}'. Please check the path and try again.")
            continue

        # --- Agent 1: Data Validation ---
        validation_report = validator_agent.run_validation(file_path, agency_key)
        print("\n--- [Report 1/3] Validation Report ---")
        print(json.dumps(validation_report, indent=2, cls=CustomJSONEncoder))
        
        if validation_report.get("status") != "SUCCESS":
            print("\nAudit stopped due to validation failure.")
            continue

        # --- Agent 2: Compliance Checking ---
        if file_path.endswith('.csv'): df = pd.read_csv(file_path)
        else: df = pd.read_excel(file_path)
        
        # *** FIX IS HERE: Unpack the tuple into two separate variables ***
        compliance_report, processed_df = checker_agent.run_checker(df, agency_key)
        
        print("\n--- [Report 2/3] Compliance Report ---")
        print(json.dumps(compliance_report, indent=2, cls=CustomJSONEncoder))

        # *** FIX IS HERE: Check the status from the unpacked report dictionary ***
        if compliance_report.get("status") != "SUCCESS":
            print("\nAudit stopped at Compliance Checking stage.")
            continue

        # --- Agent 3: XAI Inspection ---
        xai_report = inspector_agent.run_inspector(processed_df)
        print("\n--- [Report 3/3] XAI Inspector Report ---")
        print(json.dumps(xai_report, indent=2, cls=CustomJSONEncoder))
        
        if xai_report.get("status") != "SUCCESS":
            print("\nAudit stopped at XAI Inspection stage.")
            continue

        # --- Agent 4: Voting and Final Report ---
        final_report = voting_agent.run_voter(validation_report, compliance_report, xai_report)
        
        # --- Agent 5: Generate the HTML Report ---
        report_file_path = report_agent.generate_report(final_report)
        
        print("\n--- AUDIT COMPLETE ---")
        print(f"Final Grade: {final_report['final_compliance_grade']}")
        print(f"A detailed HTML report has been saved to: {report_file_path}")
        print("----------------------\n")


if __name__ == "__main__":
    # Before running, ensure you have installed the required packages:
    # pip install pandas openpyxl scikit-learn shap lime matplotlib google-generativeai jinja2
    # AND set your Google API Key: export GOOGLE_API_KEY="YOUR_API_KEY"
    run_full_audit_pipeline()
