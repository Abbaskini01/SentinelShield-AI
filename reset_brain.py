import os

# Define the path to the anomaly detector's saved state file
MODEL_FILE = os.path.join('src', 'anomaly_model_state.pkl')

def reset_brain():
    """
    Checks for the existence of the anomaly detector's model file
    and deletes it to force retraining on the next application run.
    """
    print(f"Checking for brain file at: {MODEL_FILE}")
    if os.path.exists(MODEL_FILE):
        try:
            os.remove(MODEL_FILE)
            print("✅ Old Brain Deleted. The anomaly detector will retrain on the next run.")
        except OSError as e:
            print(f"❌ Error deleting brain file: {e}")
    else:
        print("Brain already clean. No action needed.")

if __name__ == '__main__':
    reset_brain()
