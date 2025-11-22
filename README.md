# SentinelShield.AI - The Next-Gen LLM Firewall

## The Problem

Large Language Models (LLMs) are powerful but inherently vulnerable to sophisticated attacks like Prompt Injection, Jailbreaks, and the detection of Zero-Day Anomalies. Traditional security solutions, including standard firewalls, are often too rigid and lack the contextual understanding required to effectively protect LLMs without generating excessive "false positives" – blocking legitimate, safe interactions.

## The Solution: A "Defense-in-Depth" Architecture

SentinelShield.AI employs a revolutionary multi-layered approach, designed not just to block threats, but to understand context and minimize false positives.

### 🌌 Layer 1 (Math): Isolation Forest (Anomaly Detection)
This layer acts as a highly sensitive "gibberish" filter. It leverages advanced mathematical models (Isolation Forest on vector embeddings) to identify and block inputs that are statistically unusual or structurally nonsensical. This catches obvious attacks and noise, ensuring only coherent prompts reach the next layer.

### 🧠 Layer 2 (Intelligence): Gemini 2.5 Flash (Context-Aware Judge)
For prompts that pass the initial math-based anomaly check, a powerful Google Gemini 2.5 Flash agent takes over. This AI acts as a sophisticated judge, analyzing the semantic intent of the prompt. It's trained to distinguish between genuinely malicious actions (e.g., attempting to exploit the system) and safe contexts (e.g., research, storytelling, educational inquiries).

### ✨ The Innovation: Our "Anomaly Override" System
This is where SentinelShield.AI excels in solving the "False Positive" problem. If the Math layer (Isolation Forest) flags a prompt as anomalous that might *look* suspicious but is actually benign (e.g., a complex query about hacking for a novel), the Intelligence layer (Gemini 2.5 Flash) steps in. It reviews the context and, if deemed safe, *overrides* the anomaly detection in real-time, allowing the legitimate prompt to proceed. This ensures robust protection without hindering creativity or research.

## Key Features

*   **Real-time "Man-in-the-Middle" Protection:** All incoming prompts are intercepted and analyzed before they reach your LLM.
*   **3D Vector Space Visualization (Scatter Plot):** A dynamic UI displays how prompts are clustered in a semantic space, allowing you to visually see allowed (green) vs. blocked (red) interactions, and understand why certain prompts are flagged.
*   **"Context-Aware" Filtering:** Intelligent distinction between malicious intent and safe, legitimate inquiries (e.g., allows prompts like "Writing a novel about a hacker," blocks "How to hack a bank").
*   **Debug-Friendly Logging:** Comprehensive output for understanding the decision-making process at each layer.

## Tech Stack

*   **Python:** The core language for development.
*   **Streamlit:** For building interactive and visually stunning web applications.
*   **Google Gemini 2.5 Flash API:** Powering the advanced contextual and semantic analysis.
*   **SentenceTransformers:** For generating high-quality semantic embeddings of text.
*   **Scikit-Learn:** Providing robust machine learning algorithms like Isolation Forest and PCA.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/SentinelShield.AI.git
    cd SentinelShield.AI
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**
    Create a `.env` file in the root directory and add your Google API key:
    ```
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
    ```
    (Replace `YOUR_GOOGLE_API_KEY` with your actual Google API Key.)

5.  **Clean the Anomaly Detector's Brain (Recommended for first run or after configuration changes):**
    ```bash
    python reset_brain.py
    ```

6.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

## Why This Wins

SentinelShield.AI is not just another security tool; it's an intelligent defense platform that fundamentally redefines LLM security. We've tackled the pervasive "False Positive" problem by integrating cutting-edge Mathematical Anomaly Detection with advanced Semantic Understanding from a powerful AI. This hybrid approach allows the system to proactively identify novel threats while intelligently discerning safe contexts, offering unparalleled protection without compromising usability or legitimate exploration.
