import pandas as pd
import os
from typing import Dict, Any, List, Tuple

# Assuming rkb_loader is in the same directory
from .rkb_loader import RegulatoryKnowledgeBase

class DataMappingAgent:
    """
    An agent responsible for validating and mapping input data against
    regulatory standards stored in the RKB.
    """

    def __init__(self, rkb: RegulatoryKnowledgeBase):
        """
        Initializes the agent with a Regulatory Knowledge Base instance.
        
        Args:
            rkb (RegulatoryKnowledgeBase): An initialized instance of the RKB.
        """
        self.rkb = rkb
        self.validation_report = {}

    def _get_required_features(self, agency: str, standard_type: str = 'air_quality') -> List[str]:
        """
        Retrieves the list of required parameter IDs for a given agency and standard type.
        """
        agency_regs = self.rkb.get_regulation_by_agency(agency)
        if not agency_regs:
            return []
        
        standards = agency_regs.get('standards', {}).get(standard_type, [])
        return [param.get('parameter_id') for param in standards if 'parameter_id' in param]

    def check_feature_presence(self, dataset_columns: List[str], required_features: List[str]) -> Tuple[List[str], List[str], List[str]]:
        """
        Compares dataset columns with required features from the RKB.
        
        Returns:
            A tuple containing (present_features, missing_features, extra_features).
        """
        dataset_set = set(dataset_columns)
        required_set = set(required_features)

        present = list(dataset_set.intersection(required_set))
        missing = list(required_set.difference(dataset_set))
        extra = list(dataset_set.difference(required_set))
        
        return present, missing, extra

    def validate_schema(self, dataframe: pd.DataFrame, features_to_check: List[str]) -> Dict[str, str]:
        """
        Validates that the data in specified columns is numeric.
        """
        schema_errors = {}
        for col in features_to_check:
            if col in dataframe.columns:
                # Check if the column can be converted to a numeric type
                if not pd.to_numeric(dataframe[col], errors='coerce').notna().all():
                    schema_errors[col] = f"Contains non-numeric values."
        return schema_errors

    def run_validation(self, file_path: str, agency_key: str) -> Dict[str, Any]:
        """
        Executes the full validation pipeline for a given dataset file (CSV or Excel) and agency.
        
        Args:
            file_path (str): The path to the input data file (.csv or .xlsx).
            agency_key (str): The key for the agency standards (e.g., 'cpcb_standards').
            
        Returns:
            A dictionary containing the detailed validation report.
        """
        print(f"\n--- Running Validation for Agency: {agency_key} on file: {file_path} ---")

        # Load the dataset from the file path
        try:
            if file_path.endswith('.csv'):
                dataframe = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                dataframe = pd.read_excel(file_path)
            else:
                return {"status": "FAILURE", "message": "Unsupported file type. Please use .csv or .xlsx."}
        except FileNotFoundError:
            return {"status": "FAILURE", "message": f"File not found at path: {file_path}"}
        except Exception as e:
            return {"status": "FAILURE", "message": f"Error reading file: {e}"}

        # 1. Get required features from RKB
        required_features = self._get_required_features(agency_key)
        if not required_features:
            return {"status": "FAILURE", "message": f"No regulations found for agency key '{agency_key}'."}
        
        dataset_columns = dataframe.columns.tolist()
        
        # 2. Feature Presence Check
        present, missing, extra = self.check_feature_presence(dataset_columns, required_features)
        
        # 3. Schema Validation
        schema_errors = self.validate_schema(dataframe, present)
        
        # 4. Assemble the report
        report = {
            "agency": agency_key,
            "file_path": file_path,
            "required_features": required_features,
            "feature_presence": {
                "present_features": present,
                "missing_features": missing,
                "extra_features": extra
            },
            "schema_errors": schema_errors,
        }
        
        # 5. Determine final status
        if missing:
            report["status"] = "FAILURE"
            report["message"] = f"Dataset is missing required features: {missing}"
        elif schema_errors:
            report["status"] = "FAILURE"
            report["message"] = f"Dataset has schema errors: {schema_errors}"
        else:
            report["status"] = "SUCCESS"
            report["message"] = "Dataset validation passed. Ready for compliance checking."
            
        self.validation_report = report
        print(f"Validation Status: {report['status']}")
        return report

# --- Interactive Command-Line Tool ---
if __name__ == "__main__":
    # This block makes the script a runnable, interactive tool.
    
    # 1. Initialize the RKB and the Agent
    try:
        rkb_instance = RegulatoryKnowledgeBase()
        validator_agent = DataMappingAgent(rkb=rkb_instance)
        print("\nData Mapping Agent is ready.")
    except Exception as e:
        print(f"Failed to initialize the agent. Error: {e}")
        exit()

    # 2. Start the interactive loop
    while True:
        file_path = input("\nEnter the path to your CSV or Excel file (or 'exit' to quit): ")
        if file_path.lower() == 'exit':
            print("Exiting tool.")
            break
        import pandas as pd
import os
from typing import Dict, Any, List, Tuple

# Assuming rkb_loader is in the same directory
from .rkb_loader import RegulatoryKnowledgeBase

class DataMappingAgent:
    """
    An agent responsible for validating and mapping input data against
    regulatory standards stored in the RKB.
    """

    def __init__(self, rkb: RegulatoryKnowledgeBase):
        """
        Initializes the agent with a Regulatory Knowledge Base instance.
        
        Args:
            rkb (RegulatoryKnowledgeBase): An initialized instance of the RKB.
        """
        self.rkb = rkb
        self.validation_report = {}

    def _get_required_features(self, agency: str, standard_type: str = 'air_quality') -> List[str]:
        """
        Retrieves the list of required parameter IDs for a given agency and standard type.
        """
        agency_regs = self.rkb.get_regulation_by_agency(agency)
        if not agency_regs:
            return []
        
        standards = agency_regs.get('standards', {}).get(standard_type, [])
        return [param.get('parameter_id') for param in standards if 'parameter_id' in param]

    def check_feature_presence(self, dataset_columns: List[str], required_features: List[str]) -> Tuple[List[str], List[str], List[str]]:
        """
        Compares dataset columns with required features from the RKB.
        
        Returns:
            A tuple containing (present_features, missing_features, extra_features).
        """
        dataset_set = set(dataset_columns)
        required_set = set(required_features)

        present = list(dataset_set.intersection(required_set))
        missing = list(required_set.difference(dataset_set))
        extra = list(dataset_set.difference(required_set))
        
        return present, missing, extra

    def validate_schema(self, dataframe: pd.DataFrame, features_to_check: List[str]) -> Dict[str, str]:
        """
        Validates that the data in specified columns is numeric.
        """
        schema_errors = {}
        for col in features_to_check:
            if col in dataframe.columns:
                # Check if the column can be converted to a numeric type
                if not pd.to_numeric(dataframe[col], errors='coerce').notna().all():
                    schema_errors[col] = f"Contains non-numeric values."
        return schema_errors

    def run_validation(self, file_path: str, agency_key: str) -> Dict[str, Any]:
        """
        Executes the full validation pipeline for a given dataset file (CSV or Excel) and agency.
        
        Args:
            file_path (str): The path to the input data file (.csv or .xlsx).
            agency_key (str): The key for the agency standards (e.g., 'cpcb_standards').
            
        Returns:
            A dictionary containing the detailed validation report.
        """
        print(f"\n--- Running Validation for Agency: {agency_key} on file: {file_path} ---")

        # Load the dataset from the file path
        try:
            if file_path.endswith('.csv'):
                dataframe = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                dataframe = pd.read_excel(file_path)
            else:
                return {"status": "FAILURE", "message": "Unsupported file type. Please use .csv or .xlsx."}
        except FileNotFoundError:
            return {"status": "FAILURE", "message": f"File not found at path: {file_path}"}
        except Exception as e:
            return {"status": "FAILURE", "message": f"Error reading file: {e}"}

        # 1. Get required features from RKB
        required_features = self._get_required_features(agency_key)
        if not required_features:
            return {"status": "FAILURE", "message": f"No regulations found for agency key '{agency_key}'."}
        
        dataset_columns = dataframe.columns.tolist()
        
        # 2. Feature Presence Check
        present, missing, extra = self.check_feature_presence(dataset_columns, required_features)
        
        # 3. Schema Validation
        schema_errors = self.validate_schema(dataframe, present)
        
        # 4. Assemble the report
        report = {
            "agency": agency_key,
            "file_path": file_path,
            "required_features": required_features,
            "feature_presence": {
                "present_features": present,
                "missing_features": missing,
                "extra_features": extra
            },
            "schema_errors": schema_errors,
        }
        
        # 5. Determine final status
        if missing:
            report["status"] = "FAILURE"
            report["message"] = f"Dataset is missing required features: {missing}"
        elif schema_errors:
            report["status"] = "FAILURE"
            report["message"] = f"Dataset has schema errors: {schema_errors}"
        else:
            report["status"] = "SUCCESS"
            report["message"] = "Dataset validation passed. Ready for compliance checking."
            
        self.validation_report = report
        print(f"Validation Status: {report['status']}")
        return report

# --- Interactive Command-Line Tool ---
if __name__ == "__main__":
    # This block makes the script a runnable, interactive tool.
    
    # 1. Initialize the RKB and the Agent
    try:
        rkb_instance = RegulatoryKnowledgeBase()
        validator_agent = DataMappingAgent(rkb=rkb_instance)
        print("\nData Mapping Agent is ready.")
    except Exception as e:
        print(f"Failed to initialize the agent. Error: {e}")
        exit()

    # 2. Start the interactive loop
    while True:
        file_path = input("\nEnter the path to your CSV or Excel file (or 'exit' to quit): ")
        if file_path.lower() == 'exit':
            print("Exiting tool.")
            break
        
        agency_key = input("Enter the agency key to validate against (e.g., cpcb_standards, epa_standards): ")

        if not os.path.exists(file_path):
            print(f"Error: File not found at '{file_path}'. Please check the path and try again.")
            continue
        
        # 3. Run validation and print the report
        validation_report = validator_agent.run_validation(file_path, agency_key)
        
        print("\n--- Validation Report ---")
        import json
        print(json.dumps(validation_report, indent=2))
        print("-------------------------\n")

        agency_key = input("Enter the agency key to validate against (e.g., cpcb_standards, epa_standards): ")

        if not os.path.exists(file_path):
            print(f"Error: File not found at '{file_path}'. Please check the path and try again.")
            continue
        
        # 3. Run validation and print the report
        validation_report = validator_agent.run_validation(file_path, agency_key)
        
        print("\n--- Validation Report ---")
        import json
        print(json.dumps(validation_report, indent=2))
        print("-------------------------\n")
