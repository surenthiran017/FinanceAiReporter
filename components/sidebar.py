import streamlit as st
import os

def render_sidebar():
    """Render the application sidebar with navigation and info"""
    
    with st.sidebar:
        st.title("FinBot")
        
        # Show which AI model is being used with badge
        gemini_available = os.environ.get("GEMINI_API_KEY") is not None
        openai_available = os.environ.get("OPENAI_API_KEY") is not None
        
        if gemini_available:
            st.markdown("#### ⚔️ Powered by Warriors")
        elif openai_available:
            st.markdown("#### 🧠 Powered by OpenAI")
        else:
            st.markdown("#### ⚔️ Powered by Warriors")
            
        st.markdown("---")
        
        # Navigation
        st.subheader("Navigation")
        pages = {
            "Upload Data": "📊",
            "Chat with FinBot": "💬",
            "Generate Reports": "📝",
            "Visualizations": "📈"
        }
        
        for page, icon in pages.items():
            if st.button(f"{icon} {page}"):
                st.session_state.current_page = page
                st.rerun()
        
        st.markdown("---")
        
        # Show current data status
        st.subheader("Data Status")
        if st.session_state.data_uploaded:
            st.success("✅ Transaction data loaded")
            
            # Show basic data stats if available
            if st.session_state.transaction_data is not None:
                df = st.session_state.transaction_data
                st.markdown(f"**Records:** {len(df)}")
                
                if 'date' in df.columns:
                    min_date = df['date'].min().strftime('%Y-%m-%d')
                    max_date = df['date'].max().strftime('%Y-%m-%d')
                    st.markdown(f"**Date Range:** {min_date} to {max_date}")
                
                if 'amount' in df.columns:
                    total = df['amount'].sum()
                    st.markdown(f"**Net Amount:** ${total:.2f}")
            
            if st.button("Clear Data"):
                st.session_state.data_uploaded = False
                st.session_state.transaction_data = None
                st.session_state.chat_history = []
                st.session_state.generated_reports = {}
                st.rerun()
        else:
            st.info("⚠️ No data loaded yet")
        
        st.markdown("---")
        
        # About section
        st.subheader("About FinBot")
        st.markdown("""
        FinBot is an AI-powered financial reporting assistant that helps you:
        
        * Generate financial reports
        * Analyze transaction data
        * Visualize financial trends
        * Get insights through chat
        
        Upload your transaction data to get started!
        """)
        
        # Add version info
        st.markdown("---")
        st.caption("FinBot v1.0 - Financial Analysis Suite")
