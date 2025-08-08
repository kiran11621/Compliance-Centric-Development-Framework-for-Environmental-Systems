import json
import numpy as np
import pandas as pd

class CustomJSONEncoder(json.JSONEncoder):
    """
    A custom JSON encoder to handle special data types from NumPy and pandas,
    preventing TypeError during JSON serialization.
    """
    def default(self, obj):
        """
        Overrides the default method to handle specific types.
        """
        # If the object is a NumPy integer, convert it to a standard Python int.
        if isinstance(obj, np.integer):
            return int(obj)
        # If the object is a NumPy float, convert it to a standard Python float.
        if isinstance(obj, np.floating):
            return float(obj)
        # If the object is a NumPy array, convert it to a list.
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        # If the object is a pandas DataFrame, convert it to a dictionary.
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient='records')
        # If the object is a pandas Series, convert it to a list.
        if isinstance(obj, pd.Series):
            return obj.tolist()
        # Let the base class default method raise the TypeError for other types.
        return super(CustomJSONEncoder, self).default(obj)

