# import pandas as pd
# import json
# import os
# import sys
# import joblib

# # Add the project root to the Python path
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# sys.path.insert(0, project_root)

# # Import all agents
# from app.core.rkb_loader import RegulatoryKnowledgeBase
# from app.core.data_validator import DataMappingAgent
# from app.core.compliance_checker import ComplianceCheckerAgent
# from app.core.xai_inspector import XAIInspectorAgent
# from app.core.voting_agent import VotingAgent
# from app.core.report_generator import ReportAgent
# from app.core.model_performance_agent import ModelPerformanceAgent
# from app.core.utils import CustomJSONEncoder

# def run_full_audit_pipeline():
#     """
#     An interactive command-line tool to run the entire 6-agent audit pipeline.
#     This version is designed to be resilient and always generate a final report.
#     """
#     # 1. Initialize all agents
#     try:
#         rkb_instance = RegulatoryKnowledgeBase()
#         validator_agent = DataMappingAgent(rkb=rkb_instance)
#         checker_agent = ComplianceCheckerAgent(rkb=rkb_instance)
#         performance_agent = ModelPerformanceAgent()
#         inspector_agent = XAIInspectorAgent()
#         voting_agent = VotingAgent()
#         report_agent = ReportAgent()
#         print("\n--- All Agents Initialized and Ready ---")
#     except Exception as e:
#         print(f"Failed to initialize agents. Error: {e}")
#         return

#     # 2. Start the interactive loop
#     while True:
#         try:
#             # --- Get User Inputs ---
#             file_path = input("\nEnter the path to your data file (or 'exit' to quit): ")
#             if file_path.lower() == 'exit':
#                 print("Exiting tool.")
#                 break
            
#             model_path = input("Enter the path to your pre-trained model file (.pkl): ")
#             agency_key = input("Enter the agency key to audit against (e.g., cpcb_standards): ")
#             target_column = input("Enter the name of the ground truth column in your data file (e.g., PM2_5_High): ")

#             if not os.path.exists(file_path) or not os.path.exists(model_path):
#                 print(f"Error: One or more files not found. Please check paths and try again.")
#                 continue

#             # --- Initialize report variables ---
#             validation_report, compliance_report, performance_report, xai_report = {}, {}, {}, {}

#             # --- Agent 1: Data Validation ---
#             validation_report = validator_agent.run_validation(file_path, agency_key)
#             if validation_report.get("status") == "SUCCESS":
#                 # --- Load data and model only if validation passes ---
#                 if file_path.endswith('.csv'): df = pd.read_csv(file_path)
#                 else: df = pd.read_excel(file_path)
#                 model = joblib.load(model_path)

#                 # --- Agent 2: Compliance Checking ---
#                 compliance_report, processed_df = checker_agent.run_checker(df, agency_key)

#                 # --- Agent 3: Model Performance ---
#                 # *** FIX IS HERE: Intelligently determine the features the model was trained on ***
#                 model_features = model.feature_names_in_ if hasattr(model, 'feature_names_in_') else None
#                 if model_features is None:
#                     # Fallback for older models without this attribute
#                     performance_report = {"status": "FAILURE", "message": "Could not determine model's training features automatically. This model is likely not compliant or was saved with an old library version."}
#                 else:
#                     performance_report = performance_agent.evaluate_performance(model, df, model_features, target_column)

#                 # --- Agent 4: XAI Inspection ---
#                 if performance_report.get("status") == "SUCCESS":
#                     xai_report = inspector_agent.run_inspector(df, model_path, model_features)
#                 else:
#                     xai_report = {"status": "SKIPPED", "message": "XAI Inspection was skipped due to model performance evaluation failure."}

#             # --- Agent 5 & 6: Voting and Reporting (This will always run) ---
#             final_report = voting_agent.run_voter(validation_report, compliance_report, xai_report, performance_report)
#             report_file_path = report_agent.generate_report(final_report)
            
#             print("\n--- AUDIT COMPLETE ---")
#             print(f"Final Grade: {final_report['final_compliance_grade']}")
#             print(f"A detailed HTML report has been saved to: {report_file_path}")
#             print("----------------------\n")

#         except Exception as e:
#             print(f"\nAn unexpected error occurred in the main pipeline: {e}")
#             print("Restarting audit loop...")
#             continue


# if __name__ == "__main__":
#     run_full_audit_pipeline()
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
    This version is designed to be resilient and always generate a final report.
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
            file_path = input("\nEnter the path to your data file (or 'exit' to quit): ")
            if file_path.lower() == 'exit':
                print("Exiting tool.")
                break
            
            model_path = input("Enter the path to your pre-trained model file (.pkl): ")
            agency_key = input("Enter the agency key to audit against (e.g., cpcb_standards): ")
            target_column = input("Enter the name of the ground truth column in your data file (e.g., PM2_5_High): ")

            if not os.path.exists(file_path) or not os.path.exists(model_path):
                print(f"Error: One or more files not found. Please check paths and try again.")
                continue

            # --- Initialize report variables ---
            validation_report, compliance_report, performance_report, xai_report = {}, {}, {}, {}

            # --- Agent 1: Data Validation ---
            validation_report = validator_agent.run_validation(file_path, agency_key)
            if validation_report.get("status") == "SUCCESS":
                # --- Load data and model only if validation passes ---
                if file_path.endswith('.csv'): df = pd.read_csv(file_path)
                else: df = pd.read_excel(file_path)
                model = joblib.load(model_path)

                # --- Agent 2: Compliance Checking ---
                compliance_report, processed_df = checker_agent.run_checker(df, agency_key)

                # --- Agent 3: Model Performance ---
                model_features = model.feature_names_in_ if hasattr(model, 'feature_names_in_') else []
                
                performance_report = performance_agent.evaluate_performance(model, df, model_features, target_column)

                # --- Agent 4: XAI Inspection ---
                if performance_report.get("status") == "SUCCESS":
                    xai_report = inspector_agent.run_inspector(df, model_path, model_features)
                else:
                    xai_report = {"status": "SKIPPED", "message": "XAI Inspection was skipped due to model performance evaluation failure."}

            # --- Agent 5 & 6: Voting and Reporting (This will always run) ---
            # *** FIX IS HERE: Pass the model's actual features to the voter ***
            model_features_list = model.feature_names_in_.tolist() if 'model' in locals() and hasattr(model, 'feature_names_in_') else []
            final_report = voting_agent.run_voter(validation_report, compliance_report, xai_report, performance_report, model_features_list)
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
