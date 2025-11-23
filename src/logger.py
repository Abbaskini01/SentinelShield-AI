import pandas as pd
import os
from datetime import datetime
import ast  # Needed to safely convert string back to tuple

# Define the path for the log file
LOG_FILE = "activity_log.csv"
# Updated columns to include pca_coords
LOG_COLUMNS = ['timestamp', 'prompt', 'action', 'threat_type', 'threat_score', 'reason', 'pca_coords']

def log_interaction(prompt: str, response_data: dict, pca_coords: tuple = None):
    """
    Logs the details of a single user prompt, system response, and PCA coords to a CSV.

    Args:
        prompt (str): The raw user input.
        response_data (dict): The analysis dictionary from the defense engine.
        pca_coords (tuple, optional): The (x, y) or (x, y, z) coordinates from PCA analysis. Defaults to None.
    """
    # Ensure response_data is a dictionary
    if not isinstance(response_data, dict):
        response_data = {'action': 'error', 'threat_type': 'invalid_response', 'threat_score': 0, 'reason': 'Response was not a valid dictionary.'}

    # Prepare the new log entry
    log_entry = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'prompt': prompt,
        'action': response_data.get('action', 'unknown'),
        'threat_type': response_data.get('threat_type', 'none'),
        'threat_score': response_data.get('threat_score', 0),
        'reason': response_data.get('reason', 'No reason provided.'),
        # Convert tuple to string for CSV storage, handle None case
        'pca_coords': str(pca_coords) if pca_coords is not None else 'none'
    }

    # Check if the log file already exists to determine if headers are needed
    file_exists = os.path.exists(LOG_FILE)

    # Create a DataFrame from the new entry to easily append to CSV
    df_new_log = pd.DataFrame([log_entry])

    # Append to the CSV file. Write header only if the file is new.
    # Using mode='a' (append) works best.
    try:
        df_new_log.to_csv(LOG_FILE, mode='a', header=not file_exists, index=False)
    except Exception as e:
        print(f"Error writing to log file: {e}")


def get_logs() -> pd.DataFrame:
    """
    Retrieves all logs from the CSV file, converts data types back to usable formats,
    and returns them as a sorted DataFrame.
    """
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame(columns=LOG_COLUMNS)

    try:
        # Read the log file into a DataFrame
        df = pd.read_csv(LOG_FILE)
        
        # Handle case where file exists but is empty
        if df.empty:
            return pd.DataFrame(columns=LOG_COLUMNS)

        # Ensure timestamp column is treated as datetime for proper sorting
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # --- CRITICAL FIX FOR GRAPH ---
        # Convert the 'pca_coords' string column back into actual Python tuples/lists
        # We use ast.literal_eval for safe evaluation of the string representation
        if 'pca_coords' in df.columns:
            def safe_coords_convert(val):
                try:
                    if pd.isna(val) or val == 'none':
                        return None
                    return ast.literal_eval(val)
                except (ValueError, SyntaxError):
                    return None
            
            df['pca_coords'] = df['pca_coords'].apply(safe_coords_convert)
        # ------------------------------

        # Sort the DataFrame by timestamp, newest first
        df = df.sort_values(by='timestamp', ascending=False)
        
        # Ensure all expected columns exist, even if file was created by older version
        for col in LOG_COLUMNS:
             if col not in df.columns:
                 df[col] = None
                 
        # Reorder columns to match defined order
        df = df[LOG_COLUMNS]
        
        return df

    except pd.errors.EmptyDataError:
         return pd.DataFrame(columns=LOG_COLUMNS)
    except Exception as e:
        print(f"An error occurred while reading the log file: {e}")
        # Return an empty dataframe with correct columns as fallback
        return pd.DataFrame(columns=LOG_COLUMNS)

if __name__ == '__main__':
    # Quick test to ensure it works
    print("--- Testing Logger with PCA support ---")
    if os.path.exists(LOG_FILE): os.remove(LOG_FILE) # Start fresh for test

    # Test 1: Blocked with coords
    log_interaction("test attack", {"action": "blocked", "threat_type": "anomaly", "reason": "test"}, pca_coords=(0.5, -0.2))
    
    # Test 2: Allowed with coords
    log_interaction("hello world", {"action": "allowed", "threat_type": "none", "reason": "safe"}, pca_coords=(-0.1, 0.05))

    # Test 3: No coords
    log_interaction("no coords test", {"action": "allowed", "reason": "safe"})

    df = get_logs()
    print(df[['prompt', 'action', 'pca_coords']].head())
    print("\nLogger test complete. Check data above.")
    if os.path.exists(LOG_FILE): os.remove(LOG_FILE)