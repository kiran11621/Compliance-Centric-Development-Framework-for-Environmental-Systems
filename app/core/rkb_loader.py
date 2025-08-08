import json
import os
from typing import Dict, Any

# Define the absolute path to the regulations directory
REGULATIONS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'regulations')
)

class RegulatoryKnowledgeBase:
    """
    A class to load, manage, and provide access to environmental regulations
    from JSON files. It acts as a singleton to ensure regulations are loaded only once.
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RegulatoryKnowledgeBase, cls).__new__(cls)
        return cls._instance

    def __init__(self, regulations_path: str = REGULATIONS_DIR):
        """
        Initializes the RKB by loading all regulation files from the specified path.
        The initialization happens only once.
        """
        # The check below ensures that the expensive file I/O runs only once.
        if not hasattr(self, 'initialized'):
            self.regulations = self._load_regulations(regulations_path)
            if not self.regulations:
                print("Warning: No regulations were loaded. Check the regulations directory and file contents.")
            else:
                print("Regulatory Knowledge Base initialized successfully.")
            self.initialized = True

    def _load_regulations(self, path: str) -> Dict[str, Any]:
        """
        Loads all .json files from the given directory path.
        The key for the dictionary will be the filename without the extension.
        """
        loaded_regs = {}
        if not os.path.exists(path):
            print(f"Error: Regulations directory not found at '{path}'")
            return loaded_regs
            
        for filename in os.listdir(path):
            if filename.endswith(".json"):
                file_path = os.path.join(path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        key = filename.replace('.json', '')
                        loaded_regs[key] = json.load(f)
                        print(f"Successfully loaded: {filename}")
                except json.JSONDecodeError as e:
                    print(f"Error: Could not decode JSON from {filename}. Details: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred while loading {filename}: {e}")
        return loaded_regs

    def get_all_regulations(self) -> Dict[str, Any]:
        """Returns all loaded regulations."""
        return self.regulations

    def get_regulation_by_agency(self, agency_key: str) -> Dict[str, Any]:
        """
        Retrieves regulations for a specific agency key (e.g., 'cpcb_standards').
        """
        return self.regulations.get(agency_key, {})

# Example of how to use this class
if __name__ == "__main__":
    print("--- Testing RKB Loader ---")
    rkb = RegulatoryKnowledgeBase()
    
    print("\n--- Loaded Agency Keys ---")
    print(list(rkb.get_all_regulations().keys()))

    print("\n--- Fetching EPA PM2.5 Standards ---")
    epa_regs = rkb.get_regulation_by_agency('epa_standards')
    if epa_regs:
        air_standards = epa_regs.get('standards', {}).get('air_quality', [])
        for standard in air_standards:
            if standard.get('parameter_id') == 'PM2_5':
                print(json.dumps(standard, indent=2))
