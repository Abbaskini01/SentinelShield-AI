import streamlit as st
import pandas as pd
import plotly.express as px
import time
import os

# Import core components of the application
from src.defense_engine import SentinelDefense
from src.logger import log_interaction, get_logs

# --- Custom CSS for Cyberpunk Theme ---
def load_custom_css():
    st.markdown(r"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto+Mono&display=swap');

        /* --- Main App & Background (Sophisticated Dark) --- */
        .stApp {
            /* Deep tech background with subtle gradient overlay */
            background:
                linear-gradient(180deg, rgba(10, 12, 18, 0.9) 0%, rgba(20, 24, 35, 1) 100%),
                radial-gradient(at 50% 0%, rgba(30, 35, 50, 0.5) 0%, transparent 70%);
            background-color: #0e1117; /* Fallback */
            color: #e0e0e0;
            font-family: 'Roboto Mono', monospace; /* More technical body font */
        }

        /* --- Typography (Clean, Professional) --- */
        h1, h2, h3, span, div[data-testid='stMetricLabel'] {
            font-family: 'Orbitron', sans-serif !important;
            color: #ffffff !important; /* Clean white text */
            text-transform: uppercase;
            letter-spacing: 1px;
            text-shadow: none !important; /* No aggressive neon blur */
        }

        .title-container h1 {
            font-size: 3rem;
            font-weight: 700;
            /* Subtle, professional glow only on main title border */
            border-bottom: 2px solid rgba(0, 242, 255, 0.3);
            padding-bottom: 15px;
            display: inline-block;
        }

        /* --- Sidebar (Fixed & Locked) --- */
        section[data-testid='stSidebar'] {
            background-color: #141823;
            border-right: 1px solid rgba(0, 242, 255, 0.2);
            /* LOCK SIDEBAR WIDTH */
            width: 320px !important;
            min-width: 320px !important;
            max-width: 320px !important;
        }

        /* HIDE SIDEBAR RESIZE HANDLE */
        div[data-testid='stSidebarNav'] + div {
            display: none !important;
        }

        /* --- Metrics (HUD Style) --- */
        div[data-testid='stMetricValue'] {
            font-family: 'Orbitron', sans-serif;
            color: #00f2ff !important; /* Keep accent color only for numbers */
            font-size: 2.2rem !important;
            font-weight: 700;
        }

        /* --- CRITICAL GRAPH FIXES (Plotly Containers) --- */
        /* Force ample space around charts so labels don't get cut off */
        .stPlotlyChart {
            background-color: rgba(20, 24, 35, 0.5); /* Subtle container background */
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 15px !important; /* padding inside container */
            margin-top: 10px !important;
            margin-bottom: 20px !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            /* Removing forced min-height here, handling it in Python for better alignment control */
        }

        /* --- Alert Boxes & Chat (Glass HUD Style) --- */
        .alert-box, .stChatMessage {
            background: rgba(30, 35, 50, 0.7) !important; /* Semi-transparent glass */
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            padding: 1.5rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            margin-bottom: 1.5rem;
        }

        /* Subtle color accents for status */
        .alert-danger { border-left: 4px solid #ff4d4d; color: #ffcccc; }
        .alert-success { border-left: 4px solid #00f2ff; color: #ccffcc; }
        .alert-warning { border-left: 4px solid #ffcc66; color: #ffcc66; }

        /* --- Chat Input Button Styling (New Fix) --- */
        /* Target the submit button inside the chat input container */
        .stChatInput button {
            background: rgba(30, 35, 50, 0.7) !important; /* Glass background */
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 242, 255, 0.3) !important; /* Subtle neon border */
            color: #00f2ff !important; /* Neon icon color */
            transition: all 0.3s ease;
        }

        /* Hover state for the button */
        .stChatInput button:hover {
            background: rgba(0, 242, 255, 0.1) !important; /* Slight glow background */
            border: 1px solid rgba(0, 242, 255, 0.8) !important; /* Brighter border */
            box-shadow: 0 0 15px rgba(0, 242, 255, 0.4); /* Glow effect */
        }

        /* --- PERMANENT SIDEBAR FIX (HIDE TOGGLE) --- */
        /* Completely hide the container that holds the collapse button */
        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
            visibility: hidden !important;
        }
        /* Also hide the close button inside the sidebar just in case */
        section[data-testid="stSidebar"] > div:first-child > div:first-child button {
             display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

# --- Page Configuration ---
st.set_page_config(
    page_title="SentinelShield.AI",
    page_icon="🛡️",
    layout="wide",
    # Ensure it starts expanded, CSS will keep it that way
    initial_sidebar_state="expanded"
)
load_custom_css()

# --- Initialization ---
if 'defense_engine' not in st.session_state:
    with st.spinner('Initializing Defense Core...'):
        try:
            st.session_state.defense_engine = SentinelDefense()
        except Exception as e:
            st.error(f"Initialization Failed: {e}")
            st.stop()

# --- Sidebar ---
with st.sidebar:
    st.title("SentinelShield")
    st.metric(label="System Status", value="ACTIVE")
    
    st.markdown("---")
    
    # Get logs centrally here
    logs_df = get_logs()
    total_requests = len(logs_df)
    threats_blocked = len(logs_df[logs_df['action'] == 'blocked']) if not logs_df.empty else 0
    
    col1, col2 = st.columns(2)
    col1.metric("Total Requests", total_requests)
    col2.metric("Threats Blocked", threats_blocked)
    
    st.markdown("---")
    if st.button("Refresh Data"):
        st.rerun()

# --- Main Application Layout ---
st.markdown('<div class="title-container"><h1>SentinelShield.AI Interface</h1></div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🛡️ Secure Chat", "📊 Threat Forensics"])

# --- Secure Chat Tab ---
with tab1:
    st.subheader("AI-Powered Secure Prompt Gateway")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

    # Chat Input Processing
    if prompt := st.chat_input("Enter your prompt here..."):
        # 1. Add user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 2. Process through Defense Engine
        with st.spinner('Analyzing prompt with SentinelShield AI...'):
            defense = st.session_state.defense_engine
            gateway_response = defense.process_request(prompt)
            
            # Extract coords if they exist
            pca_coords = gateway_response.get('pca_coords')
            
            # Log the interaction centrally
            log_interaction(prompt, gateway_response, pca_coords)

        # 3. Handle Response & Display
        with st.chat_message("assistant"):
            action = gateway_response.get("action")
            
            if action == "blocked":
                threat_type = gateway_response.get('threat_type', 'N/A')
                reason = gateway_response.get('reason', 'N/A')
                
                error_html = f"""
                <div class="alert-box alert-danger">
                    <strong>🚨 PROMPT BLOCKED</strong><br>
                    <b>Threat Type:</b> {threat_type}<br>
                    <b>Reason:</b> {reason}
                </div>
                """
                st.markdown(error_html, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": error_html})
            
            elif action == "allowed":
                # Check for override or sanitization
                if gateway_response.get('override_triggered'):
                     override_html = f"""
                    <div class="alert-box alert-warning">
                        <strong>⚠️ Anomaly Override Triggered</strong><br>
                        Prompt was statistically unusual but determined to be safe by AI context analysis.<br>
                        <b>Reason:</b> {gateway_response.get('reason')}
                    </div>
                    """
                     st.markdown(override_html, unsafe_allow_html=True)
                     st.session_state.messages.append({"role": "assistant", "content": override_html})

                sanitized_prompt = gateway_response.get('sanitized_prompt', prompt)
                if sanitized_prompt != prompt:
                     sanitized_html = f"""
                    <div class="alert-box alert-warning">
                        <b>ℹ️ Prompt Rewritten for Safety</b><br>
                        Original prompt was sanitized before being sent to the AI model.
                    </div>
                    """
                     st.markdown(sanitized_html, unsafe_allow_html=True)
                     st.session_state.messages.append({"role": "assistant", "content": sanitized_html})

                # Fetch real response from Gemini
                try:
                    with st.spinner('Fetching safe response from Gemini...'):
                        gemini_response = defense.model.generate_content(sanitized_prompt)
                        
                        if gemini_response.parts:
                            response_text = gemini_response.text
                            success_html = f"""
                            <div class="alert-box alert-success">
                                <strong>✅ Verified Safe Response:</strong><br><br>
                                {response_text}
                            </div>
                            """
                            st.markdown(success_html, unsafe_allow_html=True)
                            st.session_state.messages.append({"role": "assistant", "content": success_html})
                        else:
                             # Gemini refused due to its own safety settings
                            refusal_html = """
                            <div class="alert-box alert-warning">
                                <b>⚠️ Response Unavailable</b><br>
                                The prompt passed SentinelShield, but the downstream AI model refused to generate a response due to its own safety policies.
                            </div>
                            """
                            st.markdown(refusal_html, unsafe_allow_html=True)
                            st.session_state.messages.append({"role": "assistant", "content": refusal_html})

                except Exception as e:
                    error_html = f"""
                    <div class="alert-box alert-danger">
                        <b>🚨 API Error</b><br>
                        Failed to get response from Gemini API: {str(e)}
                    </div>
                    """
                    st.markdown(error_html, unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": error_html})

# --- Threat Forensics Tab ---
with tab2:
    st.subheader("Threat Analysis Dashboard")
    st.markdown("Visualizing log data and semantic anomalies of all interactions.")
    
    # Get the latest logs
    logs_df_forensics = get_logs()

    # --- 1. Anomaly Space Visualization (Scatter Plot) ---
    st.markdown("### Real-Time Anomaly Space (PCA Visualization)")
    
    # Filter for logs that have valid PCA coordinates
    df_pca = logs_df_forensics.dropna(subset=['pca_coords'])

    if not df_pca.empty:
        # Split the 'pca_coords' tuple column into two separate X and Y columns
        try:
            df_pca[['pca_x', 'pca_y']] = pd.DataFrame(df_pca['pca_coords'].tolist(), index=df_pca.index)
            
            # Create the scatter plot
            fig_scatter = px.scatter(
                df_pca,
                x='pca_x',
                y='pca_y',
                color='action',
                symbol='action',
                hover_data=['prompt', 'threat_type', 'reason'],
                color_discrete_map={'blocked': '#ff4d4d', 'allowed': '#00f2ff'},
                title="Semantic Clusters of Prompts",
                labels={'pca_x': 'PCA Component 1', 'pca_y': 'PCA Component 2'}
            )
            
            # Customize layout for cyberpunk theme
            # ADDED: Explicit margins and height for alignment
            fig_scatter.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#e0e0e0',
                xaxis=dict(showgrid=True, gridcolor='#333333'),
                yaxis=dict(showgrid=True, gridcolor='#333333'),
                legend_title_text='Action Taken',
                margin=dict(t=40, b=20, l=20, r=20),
                height=400, # Fixed height for consistency
                autosize=True
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        except Exception as e:
             st.error(f"Error creating PCA plot: {e}")
    else:
        st.info("Not enough data points with PCA coordinates to display the scatter plot yet. Interact with the chat to generate data.")

    st.markdown("---")

    # --- 2. & 3. Pie and Bar Charts ---
    if logs_df_forensics.empty:
        st.warning("No log data available yet.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Threat Types")
            threats_only_df = logs_df_forensics[logs_df_forensics['threat_type'] != 'none']
            if not threats_only_df.empty:
                threat_counts = threats_only_df['threat_type'].value_counts().reset_index()
                fig_pie = px.pie(
                    threat_counts, names='threat_type', values='count',
                    hole=0.4, title='Detected Threat Categories',
                    color_discrete_sequence=px.colors.qualitative.Vivid
                )
                # CHANGED: Hide labels on the chart itself (rely on legend)
                fig_pie.update_traces(textposition='none')

                # UPDATED Layout: Increased height to maximize size, adjusted margins
                fig_pie.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#e0e0e0',
                    margin=dict(t=50, b=20, l=20, r=20),
                    height=600, # BIGGER HEIGHT to maximize
                    autosize=True,
                     # Ensure legend is positioned nicely
                    legend=dict(yanchor="top", y=1, xanchor="left", x=1.02)
                )
                # CHANGED: Added config to enable download button and modebar
                st.plotly_chart(fig_pie, use_container_width=True, config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['zoom', 'pan', 'select', 'lasso2d', 'autoScale', 'resetScale2d'],
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': 'threat_pie_chart',
                        'height': 800,
                        'width': 1200,
                        'scale': 2
                    }
                })
            else:
                st.info("No malicious threats detected yet.")

        with col2:
            st.markdown("### Actions Taken")
            action_counts = logs_df_forensics['action'].value_counts().reset_index()
            if not action_counts.empty:
                fig_bar = px.bar(
                    action_counts, x='action', y='count', color='action',
                    title='Allowed vs. Blocked Requests', text_auto=True,
                    color_discrete_map={'allowed': '#00f2ff', 'blocked': '#ff4d4d'}
                )
                # ADDED: Explicit margins and fixed height for alignment
                fig_bar.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#e0e0e0',
                    xaxis_title=None,
                    margin=dict(t=50, b=20, l=20, r=20),
                    height=600, # Match the new pie chart height
                    autosize=True
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No actions recorded yet.")

    # --- 4. Raw Data Table ---
    st.markdown("### Raw Activity Log")
    st.dataframe(logs_df_forensics, use_container_width=True, height=300)