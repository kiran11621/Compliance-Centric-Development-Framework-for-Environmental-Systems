import pandas as pd
import json
from typing import Dict, Any, List, Tuple

# Assuming rkb_loader and data_validator are in the same directory
from .rkb_loader import RegulatoryKnowledgeBase
from .data_validator import DataMappingAgent

class ComplianceCheckerAgent:
    """
    An agent that compares validated data against regulatory norms from the RKB,
    assigns compliance categories, and calculates a fidelity score.
    """

    def __init__(self, rkb: RegulatoryKnowledgeBase):
        """
        Initializes the agent with a Regulatory Knowledge Base instance.
        
        Args:
            rkb (RegulatoryKnowledgeBase): An initialized instance of the RKB.
        """
        self.rkb = rkb
        self.compliance_report = {}

    def _get_cpcb_category(self, value: float, param_id: str, agency_regs: Dict) -> str:
        """Finds the CPCB AQI category for a given value."""
        standards = agency_regs.get('standards', {}).get('air_quality', [])
        for param in standards:
            if param.get('parameter_id') == param_id:
                for cat in param.get('aqi_categories', []):
                    # Handle 'Severe' case which might have a null max
                    is_in_range = (cat['min'] <= value and (cat['max'] is None or value <= cat['max']))
                    if is_in_range:
                        return cat['category']
        return "Uncategorized"

    def _check_epa_violation(self, value: float, param_id: str, agency_regs: Dict) -> bool:
        """Checks if a value violates EPA NAAQS standards."""
        standards = agency_regs.get('standards', {}).get('air_quality', [])
        for param in standards:
            if param.get('parameter_id') == param_id:
                # For simplicity, we check against the primary 24-hour or 8-hour standard
                for std in param.get('naaqs_standards', []):
                    # This logic can be expanded to be more specific about the 'form'
                    if std['averaging_time'] in ['24 hours', '8 hours', '1 hour']:
                        if value > float(std['level']):
                            return True # Violation
        return False # No violation

    def run_checker(self, dataframe: pd.DataFrame, agency_key: str) -> Tuple[Dict[str, Any], pd.DataFrame]:
        """
        Runs the full compliance check on a validated DataFrame.

        Args:
            dataframe (pd.DataFrame): The validated input data.
            agency_key (str): The key for the agency standards (e.g., 'cpcb_standards').

        Returns:
            A tuple containing:
            - A dictionary with the detailed compliance report.
            - The processed DataFrame with added compliance category columns.
        """
        print(f"\n--- Running Compliance Check for Agency: {agency_key} ---")
        agency_regs = self.rkb.get_regulation_by_agency(agency_key)
        if not agency_regs:
            report = {"status": "FAILURE", "message": f"No regulations found for agency key '{agency_key}'."}
            return report, dataframe

        processed_df = dataframe.copy()
        
        # Get the list of features to check from the dataframe columns
        all_param_ids = [p['parameter_id'] for p in agency_regs.get('standards', {}).get('air_quality', [])]
        
        # Process each parameter found in the dataframe
        for param_id in processed_df.columns:
            if param_id not in all_param_ids:
                continue # Skip columns like 'Temperature'

            if agency_key == 'cpcb_standards':
                cat_col_name = f"{param_id}_Category"
                processed_df[cat_col_name] = processed_df[param_id].apply(
                    lambda x: self._get_cpcb_category(float(x), param_id, agency_regs)
                )
            elif agency_key == 'epa_standards':
                violation_col_name = f"{param_id}_Violation"
                processed_df[violation_col_name] = processed_df[param_id].apply(
                    lambda x: self._check_epa_violation(float(x), param_id, agency_regs)
                )

        # Calculate Compliance Score (example for CPCB)
        total_rows = len(processed_df)
        compliant_rows = 0
        category_distribution = {}

        if agency_key == 'cpcb_standards' and total_rows > 0:
            # Score based on the first parameter's categories for simplicity
            first_cat_col = f"{processed_df.columns[0]}_Category"
            if first_cat_col in processed_df.columns:
                compliant_rows = processed_df[first_cat_col].isin(['Good', 'Satisfactory']).sum()
                # *** ROBUST FIX IS HERE: Manually build dict with standard python types ***
                counts = processed_df[first_cat_col].value_counts()
                category_distribution = {}
                for index, value in counts.items():
                    category_distribution[str(index)] = int(value)
            
            compliance_score = (compliant_rows / total_rows) * 100
        else:
            compliance_score = None 

        # Assemble the final report
        self.compliance_report = {
            "status": "SUCCESS",
            "agency": agency_key,
            "compliance_score_percent": f"{compliance_score:.2f}%" if compliance_score is not None else "N/A",
            "category_distribution": category_distribution,
        }
        
        print("Compliance Check Completed.")
        return self.compliance_report, processed_df


# --- Interactive Command-Line Tool ---
if __name__ == "__main__":
    # This block demonstrates the full pipeline: Validate then Check.
    
    # 1. Initialize the agents
    try:
        rkb_instance = RegulatoryKnowledgeBase()
        validator_agent = DataMappingAgent(rkb=rkb_instance)
        checker_agent = ComplianceCheckerAgent(rkb=rkb_instance)
        print("\nAll Agents are ready.")
    except Exception as e:
        print(f"Failed to initialize agents. Error: {e}")
        exit()

    # 2. Start the interactive loop
    while True:
        file_path = input("\nEnter the path to your CSV or Excel file (or 'exit' to quit): ")
        if file_path.lower() == 'exit':
            print("Exiting tool.")
            break
        
        agency_key = input("Enter the agency key to audit against (e.g., cpcb_standards, epa_standards): ")

        # Step 1: Validate the data with the DataMappingAgent
        validation_report = validator_agent.run_validation(file_path, agency_key)
        print("\n--- Validation Report ---")
        print(json.dumps(validation_report, indent=2))
        
        # Step 2: If validation is successful, run the compliance checker
        if validation_report.get("status") == "SUCCESS":
            # Load the dataframe again to pass to the checker
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # Run the checker and get both the report and the processed dataframe
            compliance_report, processed_df = checker_agent.run_checker(df, agency_key)
            
            print("\n--- Compliance Report ---")
            print(json.dumps(compliance_report, indent=2))
            print("\n--- Processed Data Sample ---")
            print(processed_df.head().to_string())
            print("-------------------------\n")
        else:
            print("\nCompliance check skipped due to validation failure.")
            print("------------------------------------------------\n")
