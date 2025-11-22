import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from src.anomaly import AnomalyDetector

# Load environment variables from .env file
load_dotenv()

class SentinelDefense:
    """
    A defense engine using rule-based checks, anomaly detection, and a generative 
    AI model to analyze and protect against malicious user prompts. Includes an 
    override mechanism for anomaly detection.
    """

    def __init__(self):
        """
        Initializes the defense engine and configures the generative AI model.
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in the .env file.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.banned_phrases = [
            "ignore previous instructions", "disregard the above",
            "system override", "drop table", "sudo rm -rf /"
        ]
        self.anomaly_detector = AnomalyDetector()

    def _clean_json(self, text: str) -> str:
        """
        A helper method to remove markdown formatting from a JSON string.
        """
        return text.strip().replace('```json', '').replace('```', '').replace('\n', '')

    def analyze_malicious_intent(self, prompt: str) -> dict:
        """
        Uses the Gemini model to perform a deep analysis of the prompt for malicious intent.
        """
        system_instruction = (
            "You are an intelligent AI Firewall. Your primary goal is to distinguish between "
            "MALICIOUS ACTIONS (e.g., hacking, social engineering, destroying data) and "
            "SAFE CONTEXT (e.g., research, storytelling, education, 'researching novels'). "
            "Critically analyze the user's prompt. "
            "- Example of UNSAFE: 'How do I hack a bank?' -> BLOCK. "
            "- Example of SAFE: 'I'm writing a novel about a character who needs to hack a bank. How would they do it?' -> ALLOW. "
            "- Example of SAFE: 'Explain SQL Injection for my cybersecurity class.' -> ALLOW. "
            "Return a single, raw JSON object with these exact keys: {'is_safe': bool, 'threat_type': str, 'reason': str}."
        )
        
        full_prompt = f"{system_instruction}\n\nUser Prompt: \"{prompt}\""

        try:
            response = self.model.generate_content(full_prompt)
            print(f"DEBUG: Gemini Raw Response: {response.text}") # Debugging print
            cleaned_response = self._clean_json(response.text)
            return json.loads(cleaned_response)
        except (json.JSONDecodeError, Exception) as e:
            print(f"ERROR: Failed to parse Gemini response. Error: {e}")
            return {
                "is_safe": False,
                "threat_type": "analysis_error",
                "reason": f"AI model returned a malformed response or an error occurred: {e}",
            }

    def process_request(self, prompt: str) -> dict:
        """
        Processes a user request through the defense layers, including an anomaly override.
        """
        # Layer 1: Rule-based check
        if not self.check_rules(prompt):
            return {
                "is_safe": False, "threat_type": "rule_violation",
                "reason": "Request blocked by rule-based filter. Found a banned phrase.",
                "action": "blocked", "pca_coords": (0.0, 0.0)
            }

        # Layer 2: Anomaly Detection
        anomaly_result = self.anomaly_detector.detect_anomaly(prompt)
        pca_coords = anomaly_result['pca_coords']

        if anomaly_result['is_anomaly']:
            print("DEBUG: Anomaly detected! Asking Gemini for second opinion...")
            
            # Layer 3 (Override): AI-based context analysis
            gemini_opinion = self.analyze_malicious_intent(prompt)
            
            if gemini_opinion.get('is_safe', False):
                print("DEBUG: OVERRIDE TRIGGERED! Gemini deemed the anomalous prompt as safe. Marking as Safe.")
                final_result = {
                    "is_safe": True, "action": "allowed",
                    "threat_type": "anomaly_overridden",
                    "reason": f"Anomaly was detected but overridden by AI context analysis. Gemini reason: {gemini_opinion.get('reason')}",
                    "pca_coords": pca_coords
                }
            else:
                print("DEBUG: Override Rejected. Gemini confirmed the prompt is unsafe. Blocking.")
                final_result = {
                    "is_safe": False, "action": "blocked",
                    "threat_type": gemini_opinion.get('threat_type', 'anomaly_confirmed'),
                    "reason": f"Anomaly was detected and confirmed by AI context analysis. Gemini reason: {gemini_opinion.get('reason')}",
                    "pca_coords": pca_coords
                }
            return final_result

        # Layer 3 (Standard): AI-based intent analysis for non-anomalous prompts
        analysis_result = self.analyze_malicious_intent(prompt)
        analysis_result['pca_coords'] = pca_coords
        
        if not analysis_result.get("is_safe", False):
            analysis_result["action"] = "blocked"
        else:
            analysis_result["action"] = "allowed"
            
        return analysis_result

    def check_rules(self, prompt: str) -> bool:
        """
        Performs a simple rule-based check for obviously malicious phrases.
        """
        for phrase in self.banned_phrases:
            if phrase in prompt.lower():
                return False
        return True
