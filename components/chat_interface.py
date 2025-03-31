import streamlit as st
import os
from utils.financial_utils import summarize_financial_data

# Check for available APIs and import the appropriate module

gemini_api_available = os.environ.get("GEMINI_API_KEY") is not None
openai_api_available = os.environ.get("OPENAI_API_KEY") is not None

# Import the appropriate chat function based on available API keys
if gemini_api_available:
    from utils.gemini_utils import financial_chat_with_gemini as primary_chat_function
    from utils.openai_utils import financial_chat as fallback_chat_function
else:
    from utils.openai_utils import financial_chat as primary_chat_function
    fallback_chat_function = None

def render_chat_interface():
    """Render the chatbot interface for financial queries"""
    
    st.header("💬 Chat with FinBot")
    
    # Display which AI model is being used based on API availability
    if gemini_api_available:
        st.markdown("Ask questions about your financial data and get AI-powered insights from Google's Gemini model.")
        ai_badge = "⚔️ Powered by Warriors"
    elif openai_api_available:
        st.markdown("Ask questions about your financial data and get AI-powered insights from OpenAI.")
        ai_badge = "🧠 Powered by OpenAI"
    else:
        st.markdown("Ask questions about your financial data and get rule-based insights.")
        ai_badge = "📊 ⚔️ Powered by Warriors"
    
    # Display AI badge
    st.sidebar.markdown(f"### {ai_badge}")
    
    # Create a summary of financial data for the AI
    if st.session_state.transaction_data is not None:
        data_summary = summarize_financial_data(st.session_state.transaction_data)
    else:
        data_summary = None
    
    # Initialize chat history if empty
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat messages
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask something about your financial data..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response with spinner
        with st.chat_message("assistant"):
            with st.spinner("FinBot is analyzing your financial data..."):
                try:
                    # Try using the primary chat function (Gemini or rule-based)
                    response = primary_chat_function(
                        prompt, 
                        transaction_summary=data_summary,
                        chat_history=st.session_state.chat_history
                    )
                    
                    # If response is empty or contains error, try fallback
                    if "error" in response.lower() and fallback_chat_function:
                        response = fallback_chat_function(
                            prompt, 
                            transaction_summary=data_summary,
                            chat_history=st.session_state.chat_history
                        )
                        
                except Exception as e:
                    # If primary chat function fails, use fallback if available
                    if fallback_chat_function:
                        response = fallback_chat_function(
                            prompt, 
                            transaction_summary=data_summary,
                            chat_history=st.session_state.chat_history
                        )
                    else:
                        response = f"I'm sorry, I encountered an error: {str(e)}. Please try again with a different question."
                
                st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Show example questions
    with st.expander("Example questions you can ask"):
        st.markdown("""
        - What is my total income for the period?
        - What are my main expense categories?
        - What is my profit margin?
        - How have my expenses changed over time?
        - What's my financial health based on the data?
        - How much did I spend on rent?
        - What is my biggest income source?
        - What's my cash flow situation?
        - How was January for my finances?
        - What is my debt-to-equity ratio?
        """)
    
    # Option to clear chat history
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
