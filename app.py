import streamlit as st
import pandas as pd
import os
from components.sidebar import render_sidebar
from components.chat_interface import render_chat_interface
from components.data_import import render_data_import
from components.report_generator import render_report_generator
from components.visualizations import render_visualizations

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if 'data_uploaded' not in st.session_state:
        st.session_state.data_uploaded = False
    if 'transaction_data' not in st.session_state:
        st.session_state.transaction_data = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'generated_reports' not in st.session_state:
        st.session_state.generated_reports = {}
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Upload Data"

def main():
    st.set_page_config(
        page_title="FinBot - Financial Reporting Assistant",
        page_icon="💹",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    initialize_session_state()
    
    st.title("FinBot - Financial Reporting Assistant")
    st.markdown("""
    Your AI-powered assistant for financial reporting and analysis. 
    Upload your transaction data, chat with FinBot, and get automated financial reports and insights.
    """)
    
    # Render sidebar with navigation
    render_sidebar()
    
    # Main content based on selected page
    if st.session_state.current_page == "Upload Data":
        render_data_import()
    elif st.session_state.current_page == "Chat with FinBot":
        if not st.session_state.data_uploaded:
            st.warning("Please upload transaction data first to chat with FinBot.")
        else:
            render_chat_interface()
    elif st.session_state.current_page == "Generate Reports":
        if not st.session_state.data_uploaded:
            st.warning("Please upload transaction data first to generate reports.")
        else:
            render_report_generator()
    elif st.session_state.current_page == "Visualizations":
        if not st.session_state.data_uploaded:
            st.warning("Please upload transaction data first to view visualizations.")
        else:
            render_visualizations()

if __name__ == "__main__":
    main()
