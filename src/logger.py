import pandas as pd
import os
from datetime import datetime

# Define the path for the log file
LOG_FILE = "activity_log.csv"
LOG_COLUMNS = ['timestamp', 'prompt', 'action', 'threat_type', 'threat_score', 'reason']

def log_interaction(prompt: str, response_data: dict):
    """
    Logs the details of a single user prompt and the system's response to a CSV file.

    Args:
        prompt (str): The raw user input.
        response_data (dict): The analysis dictionary from the SentinelDefense engine.
    """
    # Ensure response_data is a dictionary
    if not isinstance(response_data, dict):
        # Handle cases where the response might not be as expected
        response_data = {'action': 'error', 'threat_type': 'invalid_response', 'threat_score': 0, 'reason': 'Response was not a valid dictionary.'}

    # Prepare the new log entry
    log_entry = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'prompt': prompt,
        'action': response_data.get('action', 'unknown'),
        'threat_type': response_data.get('threat_type', 'none'),
        'threat_score': response_data.get('threat_score', 0),
        'reason': response_data.get('reason', 'No reason provided.')
    }

    # Check if the log file already exists to determine if headers are needed
    file_exists = os.path.exists(LOG_FILE)

    # Create a DataFrame from the new entry to easily append to CSV
    df_new_log = pd.DataFrame([log_entry])

    # Append to the CSV file. Write header only if the file is new.
    df_new_log.to_csv(LOG_FILE, mode='a', header=not file_exists, index=False)

def get_logs() -> pd.DataFrame:
    """
    Retrieves all logs from the CSV file and returns them as a sorted DataFrame.

    Returns:
        pd.DataFrame: A DataFrame containing all log entries, sorted with the
                      most recent entries first. Returns an empty DataFrame if
                      the log file does not exist or is empty.
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

        # Sort the DataFrame by timestamp, newest first
        df = df.sort_values(by='timestamp', ascending=False)
        
        return df
    except pd.errors.EmptyDataError:
        # This can happen if the file exists but is completely empty
        return pd.DataFrame(columns=LOG_COLUMNS)
    except Exception as e:
        print(f"An error occurred while reading the log file: {e}")
        return pd.DataFrame(columns=LOG_COLUMNS)

if __name__ == '__main__':
    # Example usage for testing the logger
    print("--- Testing Logger System ---")
    
    # Example 1: A blocked interaction
    blocked_response = {
        "is_safe": False,
        "threat_type": "sql_injection",
        "threat_score": 95,
        "reason": "Detected a potential SQL injection pattern.",
        "action": "blocked"
    }
    log_interaction("' OR 1=1; --", blocked_response)
    print("Logged a blocked interaction.")

    # Example 2: An allowed interaction
    allowed_response = {
        "is_safe": True,
        "threat_type": "none",
        "threat_score": 5,
        "reason": "Prompt appears to be safe.",
        "action": "allowed"
    }
    log_interaction("What is the capital of France?", allowed_response)
    print("Logged an allowed interaction.")
    
    # Retrieve and print logs
    print("\n--- Current Logs (Newest First) ---")
    all_logs = get_logs()
    print(all_logs)

    # Clean up the test log file
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        print(f"\nCleaned up {LOG_FILE}.")
