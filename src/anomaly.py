import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA

class AnomalyDetector:
    """
    An anomaly detection module fine-tuned to have extremely low sensitivity, 
    only blocking the most structurally weird/gibberish prompts.
    """
    MODEL_STATE_PATH = "anomaly_model_state.pkl"
    EMBEDDING_MODEL = 'all-MiniLM-L6-v2'

    def __init__(self):
        """
        Initializes the AnomalyDetector, loading the sentence transformer and 
        either loading a pre-trained model or training a new one.
        """
        print("Initializing Low-Sensitivity Anomaly Detector...")
        self.embedding_model = SentenceTransformer(self.EMBEDDING_MODEL)
        
        self.model = None
        self.pca = None
        self.baseline_embeddings_pca = None

        if os.path.exists(self.MODEL_STATE_PATH):
            print(f"Loading existing model state from {self.MODEL_STATE_PATH}...")
            self._load_model_state()
        else:
            print("No existing model found. Training initial low-sensitivity model...")
            self.train_initial_model()
        print("Anomaly Detector initialized successfully.")

    def _load_model_state(self):
        """
        Loads the model, PCA transformer, and baseline data from a pickle file.
        If the file is corrupt or empty, it triggers a retraining.
        """
        if not os.path.exists(self.MODEL_STATE_PATH) or os.path.getsize(self.MODEL_STATE_PATH) == 0:
            self.train_initial_model()
            return

        try:
            with open(self.MODEL_STATE_PATH, 'rb') as f:
                state = pickle.load(f)
                self.model = state['model']
                self.pca = state['pca']
                self.baseline_embeddings_pca = state['baseline_embeddings_pca']
        except (EOFError, pickle.UnpicklingError) as e:
            print(f"WARNING: Could not load model state due to error: {e}. Forcing retraining.")
            if os.path.exists(self.MODEL_STATE_PATH):
                os.remove(self.MODEL_STATE_PATH)
            self.train_initial_model()

    def _save_model_state(self):
        """Saves the current model, PCA transformer, and baseline data to a pickle file."""
        state = {
            'model': self.model,
            'pca': self.pca,
            'baseline_embeddings_pca': self.baseline_embeddings_pca
        }
        with open(self.MODEL_STATE_PATH, 'wb') as f:
            pickle.dump(state, f)
        print(f"Model state saved to {self.MODEL_STATE_PATH}")

    def train_initial_model(self):
        """
        Trains the Isolation Forest model on a baseline dataset that includes
        examples of safe but potentially suspicious-looking prompts.
        """
        base_prompts = [
            # Standard Prompts
            "Hello, how are you?", "What is the capital of Spain?",
            "Write a Python function to sort a list.", "Tell me a story.",
            "Summarize the main points of this article.", "Explain how a car engine works.",
            "What's the weather forecast for tomorrow?", "Solve for y: 3y - 7 = 11",
            "List the primary colors.", "How do I make a good cup of coffee?",
            # Prompts with potentially sensitive keywords in a safe context
            "I am writing a cybersecurity novel about hackers.",
            "I am researching firewalls and need to understand how they work.",
            "How to kill a process in Linux using the terminal?",
            "What is SQL injection and how can I prevent it in my code?",
            "For my history class, can you explain the concept of a 'trojan horse'?",
            "My character in a story needs to bypass a security system. What are some fictional methods?",
            "Explain different types of malware for a school presentation."
        ] * 5  # Repeat for a more stable training set

        print(f"Training on {len(base_prompts)} prompts with EXTREMELY LOW sensitivity...")
        baseline_embeddings = self.embedding_model.encode(base_prompts)

        # VERY LOW contamination to only flag the most extreme outliers (true gibberish)
        self.model = IsolationForest(contamination=0.005, n_estimators=200, random_state=42)
        self.model.fit(baseline_embeddings)

        self.pca = PCA(n_components=2)
        self.baseline_embeddings_pca = self.pca.fit_transform(baseline_embeddings)
        
        self._save_model_state()

    def detect_anomaly(self, prompt: str) -> dict:
        """
        Detects if a given prompt is an anomaly (gibberish) based on the trained model.
        """
        if not self.model or not self.pca:
            raise RuntimeError("Model is not trained or loaded. Cannot detect anomalies.")
            
        prompt_embedding = self.embedding_model.encode([prompt])
        prediction = self.model.predict(prompt_embedding)[0]
        is_anomaly = prediction == -1
        anomaly_score = self.model.decision_function(prompt_embedding)[0]
        
        debug_prompt = prompt[:50].replace('\n', ' ')
        print(f"DEBUG: Prompt='{debug_prompt}...', Score={anomaly_score:.4f}, Anomaly={is_anomaly}")
        
        pca_coords = self.pca.transform(prompt_embedding)[0]
        
        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": float(anomaly_score),
            "pca_coords": tuple(pca_coords)
        }