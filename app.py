import streamlit as st
import pandas as pd
import plotly.express as px
import time

# Import core components of the application
from src.defense_engine import SentinelDefense
from src.logger import log_interaction, get_logs

def load_custom_css():
    """Injects custom CSS to style the app with a cyberpunk theme."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');

        /* Main app styling */
        .stApp {
            background-color: #0e1117;
            color: #e0e0e0;
        }

        /* Title styling */
        .title-container {
            text-align: center;
            padding: 20px;
        }
        .title-container h1 {
            font-family: 'Orbitron', sans-serif;
            color: #00f2ff; /* Neon Cyan */
            text-shadow: 0 0 10px #00f2ff, 0 0 20px #00f2ff;
        }
        
        /* Sidebar styling */
        .st-emotion-cache-16txtl3 {
            background-color: #1a1f2e;
            border-right: 1px solid #00f2ff;
        }
        .st-emotion-cache-16txtl3 h1, .st-emotion-cache-16txtl3 .st-emotion-cache-1g8p3r6 {
            font-family: 'Orbitron', sans-serif;
            color: #00f2ff;
        }

        /* Metric box styling */
        .st-emotion-cache-1vzeuhh, .st-emotion-cache-1n76own {
            background-color: rgba(0, 242, 255, 0.05);
            border: 1px solid #00f2ff;
            border-radius: 8px;
            padding: 10px;
            color: white !important;
        }
        .st-emotion-cache-1vzeuhh .st-emotion-cache-1g8p3r6, .st-emotion-cache-1n76own .st-emotion-cache-1g8p3r6 {
             color: white !important;
        }
        .st-emotion-cache-1vzeuhh .st-emotion-cache-1wiv0i8, .st-emotion-cache-1n76own .st-emotion-cache-1wiv0i8 {
            font-size: 1.5rem !important;
            color: white !important;
        }

        /* Custom alert boxes */
        .stAlert {
            border-radius: 8px;
        }
        /* Blocked / Error box */
        .st-emotion-cache-l7gloc {
            background-color: #2e1a1a;
            border: 1px solid #ff4d4d;
            color: #ffcccc;
        }
        /* Safe / Success box */
        .st-emotion-cache-x0m92w {
            background-color: #1a2e1a;
            border: 1px solid #4dff4d;
            color: #ccffcc;
        }
        </style>
    """, unsafe_allow_html=True)

# --- Page Configuration and CSS Loading ---
st.set_page_config(
    page_title="SentinelShield.AI",
    layout="wide",
    initial_sidebar_state="expanded"
)
load_custom_css()

# --- Initialization ---
if 'defense_engine' not in st.session_state:
    with st.spinner('Initializing Defense Core...'):
        try:
            st.session_state.defense_engine = SentinelDefense()
        except ValueError as e:
            st.error(f"Initialization Failed: {e}")
            st.stop()

# --- Sidebar ---
with st.sidebar:
    st.title("SentinelShield")
    st.metric(label="System Status", value="ACTIVE", delta_color="off")
    
    st.markdown("---")
    
    logs_df = get_logs()
    total_requests = len(logs_df)
    threats_blocked = len(logs_df[logs_df['action'] == 'blocked']) if not logs_df.empty else 0
    
    col1, col2 = st.columns(2)
    col1.metric("Total Requests", total_requests)
    col2.metric("Threats Blocked", threats_blocked)
    
    st.markdown("---")
    st.info("Dashboard auto-refreshes on interaction.")
    time.sleep(5) 


# --- Main Application Layout ---
st.markdown('<div class="title-container"><h1>SentinelShield.AI Interface</h1></div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🛡️ Secure Chat", "📊 Threat Forensics"])

# --- Secure Chat Tab ---
with tab1:
    st.header("AI-Powered Secure Prompt Gateway")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "anomaly_history" not in st.session_state:
        st.session_state.anomaly_history = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

    if prompt := st.chat_input("Enter your prompt here..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # --- Gateway Logic ---
        with st.spinner('Analyzing prompt with SentinelShield AI...'):
            defense = st.session_state.defense_engine
            gateway_response = defense.process_request(prompt)
            log_interaction(prompt, gateway_response)

            if isinstance(gateway_response, dict) and 'pca_coords' in gateway_response and 'action' in gateway_response:
                coords = gateway_response['pca_coords']
                st.session_state.anomaly_history.append({
                    'x_coord': coords[0],
                    'y_coord': coords[1],
                    'action': gateway_response['action']
                })
        
        # --- Response Handling ---
        with st.chat_message("assistant"):
            if isinstance(gateway_response, dict) and gateway_response.get("action") == "blocked":
                # Handle blocked prompts
                error_message = f"""
                <div style='color: #ffcccc;'>
                    <b>PROMPT BLOCKED BY SENTINELSHIELD</b><br>
                    <b>Threat Type:</b> {gateway_response.get('threat_type', 'N/A')}<br>
                    <b>Reason:</b> {gateway_response.get('reason', 'N/A')}
                </div>
                """
                st.error(error_message, icon="🚨")
                st.session_state.messages.append({"role": "assistant", "content": error_message})
            
            elif isinstance(gateway_response, dict) and gateway_response.get("action") == "allowed": # Action is "allowed"
                # If prompt was rewritten, use the sanitized version for Gemini
                final_prompt = gateway_response.get('sanitized_prompt', prompt)
                if 'sanitized_prompt' in gateway_response:
                    sanitized_info = f"<b style='color: #ffcc66;'>Original prompt was rewritten for safety.</b>"
                    st.warning(sanitized_info, icon="⚠️")
                    st.session_state.messages.append({"role": "assistant", "content": sanitized_info})

                # Fetch real response from Gemini
                try:
                    with st.spinner('Processing...'):
                        # Use the potentially sanitized prompt
                        gemini_response = defense.model.generate_content(final_prompt)
                        
                        # Handle cases where Gemini itself might refuse to answer
                        if not gemini_response.parts:
                             # This can happen if Gemini's internal safety filters trigger
                            gemini_refusal_message = """
                            <div style='color: #ffcc66;'>
                                <b>Response Unvailable.</b><br>
                                The prompt was deemed safe by SentinelShield, but the content could not be generated by the downstream AI model due to its own safety policies.
                            </div>
                            """
                            st.warning(gemini_refusal_message, icon="⚠️")
                            st.session_state.messages.append({"role": "assistant", "content": gemini_refusal_message})
                        else:
                            # Display the successful response
                            real_gemini_response = f"""
                            <div style='color: #ccffcc;'>
                                <b>✅ Verified Safe Response from Gemini:</b><br>
                                {gemini_response.text}
                            </div>
                            """
                            st.markdown(real_gemini_response, unsafe_allow_html=True)
                            st.session_state.messages.append({"role": "assistant", "content": real_gemini_response})

                except Exception as e:
                    error_gemini = f"""
                    <div style='color: #ffcccc;'>
                        <b>Error processing request with Gemini:</b><br>
                        {str(e)}<br>
                        The prompt was allowed by SentinelShield, but an error occurred with the final request. Please check your API key or network status.
                    </div>
                    """
                    st.error(error_gemini, icon="🚨")
                    st.session_state.messages.append({"role": "assistant", "content": error_gemini})
            else:
                # Fallback for unexpected gateway_response types
                st.error("An unexpected error occurred with the gateway response. Please check the logs.")

        st.rerun()

# --- Threat Forensics Tab ---
with tab2:
    st.header("Threat Analysis Dashboard")
    logs_df_forensics = get_logs()

    # --- Anomaly Space Visualization ---
    st.subheader("Real-Time Anomaly Space")
    if st.session_state.anomaly_history:
        history_df = pd.DataFrame(st.session_state.anomaly_history)
        fig_scatter = px.scatter(
            history_df, x='x_coord', y='y_coord', color='action',
            color_discrete_map={'allowed': '#00f2ff', 'blocked': '#ff4d4d'},
            title="Semantic Clusters of Prompts (PCA)",
            labels={'x_coord': 'PCA Component 1', 'y_coord': 'PCA Component 2'}
        )
        fig_scatter.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font_color='#e0e0e0', legend_title_text='Action'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("Interact with the chat to visualize prompt anomalies.")

    st.markdown("---")

    if logs_df_forensics.empty:
        st.warning("No log data available yet.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Threat Types")
            threats_only_df = logs_df_forensics[logs_df_forensics['threat_type'] != 'none']
            if not threats_only_df.empty:
                threat_counts = threats_only_df['threat_type'].value_counts().reset_index()
                fig_pie = px.pie(
                    threat_counts, names='threat_type', values='count',
                    hole=0.4, title='Detected Threats'
                )
                fig_pie.update_traces(textinfo='percent+label', marker=dict(colors=['#ff4d4d', '#ff8c00', '#ffd700']))
                fig_pie.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No threats detected so far.")

        with col2:
            st.subheader("Actions Taken")
            action_counts = logs_df_forensics['action'].value_counts().reset_index()
            fig_bar = px.bar(
                action_counts, x='action', y='count', color='action',
                title='Allowed vs. Blocked', text_auto=True,
                color_discrete_map={'allowed': '#00f2ff', 'blocked': '#ff4d4d'}
            )
            fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
            st.plotly_chart(fig_bar, use_container_width=True)
            
        st.markdown("---")
        
        st.subheader("System Event Log")
        st.dataframe(logs_df_forensics)