import streamlit as st
import pandas as pd
import io
from utils.data_utils import validate_transaction_data, preprocess_transaction_data, generate_sample_csv_content

def render_data_import():
    """Render the data import component for uploading transaction data"""
    
    st.header("📊 Upload Transaction Data")
    st.markdown("Upload your financial transaction data to begin analysis. The data should be in CSV format.")
    
    # Upload file section
    uploaded_file = st.file_uploader("Upload transaction data (CSV)", type=["csv"])
    
    # Process uploaded file
    if uploaded_file is not None:
        try:
            # Read the file
            df = pd.read_csv(uploaded_file)
            
            # Show raw data preview
            with st.expander("Preview Raw Data"):
                st.dataframe(df.head(10))
            
            # Validate data format
            is_valid, message = validate_transaction_data(df)
            
            if is_valid:
                # Preprocess the data
                processed_df = preprocess_transaction_data(df)
                
                # Store in session state
                st.session_state.transaction_data = processed_df
                st.session_state.data_uploaded = True
                
                # Show success message
                st.success("Data successfully uploaded and processed! 🎉")
                
                # Show processed data preview
                with st.expander("Preview Processed Data"):
                    st.dataframe(processed_df.head(10))
                
                # Basic statistics
                with st.expander("Data Statistics"):
                    st.markdown("### Basic Statistics")
                    
                    # Display transaction count
                    st.markdown(f"**Total Transactions:** {len(processed_df)}")
                    
                    # Display date range if date column exists
                    if 'date' in processed_df.columns:
                        min_date = processed_df['date'].min().strftime('%Y-%m-%d')
                        max_date = processed_df['date'].max().strftime('%Y-%m-%d')
                        st.markdown(f"**Date Range:** {min_date} to {max_date}")
                    
                    # Display amount statistics if amount column exists
                    if 'amount' in processed_df.columns:
                        total_amount = processed_df['amount'].sum()
                        avg_amount = processed_df['amount'].mean()
                        min_amount = processed_df['amount'].min()
                        max_amount = processed_df['amount'].max()
                        
                        st.markdown(f"**Total Amount:** ${total_amount:.2f}")
                        st.markdown(f"**Average Transaction:** ${avg_amount:.2f}")
                        st.markdown(f"**Min Transaction:** ${min_amount:.2f}")
                        st.markdown(f"**Max Transaction:** ${max_amount:.2f}")
                
                # What's next guidance
                st.markdown("### What's Next?")
                st.markdown("""
                Your data is now ready for analysis! You can:
                1. **Chat with FinBot** to ask questions about your data
                2. **Generate Reports** to create financial statements
                3. **View Visualizations** to see graphical representations
                
                Use the sidebar to navigate to these features.
                """)
                
                # Navigation buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Chat with FinBot"):
                        st.session_state.current_page = "Chat with FinBot"
                        st.rerun()
                with col2:
                    if st.button("Generate Reports"):
                        st.session_state.current_page = "Generate Reports"
                        st.rerun()
                with col3:
                    if st.button("View Visualizations"):
                        st.session_state.current_page = "Visualizations"
                        st.rerun()
            else:
                # Show error message for invalid data
                st.error(f"Error in uploaded data: {message}")
                st.markdown("""
                Please ensure your data contains the required columns:
                - `date` - Transaction date (in a valid date format)
                - `amount` - Transaction amount (numeric values)
                - `description` - Description of the transaction
                
                Optional but helpful columns:
                - `category` - Transaction category (e.g., Income, Expense)
                - `subcategory` - More detailed categorization
                - `account` - Source/destination account
                """)
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    
    # Template section
    st.markdown("---")
    st.subheader("Sample Datasets")
    st.markdown("Download our sample datasets to test the application:")
    
    # Generate template CSV content
    csv_content = generate_sample_csv_content()
    
    col1, col2, col3 = st.columns(3)
    
    # Create download button for template
    with col1:
        st.download_button(
            label="Download CSV Template",
            data=csv_content,
            file_name="transaction_template.csv",
            mime="text/csv"
        )
    
    # Add direct links to sample datasets
    with col2:
        try:
            with open('sample_business_transactions.csv', 'r') as f:
                business_csv = f.read()
            st.download_button(
                label="Business Transactions Sample",
                data=business_csv,
                file_name="sample_business_transactions.csv",
                mime="text/csv"
            )
        except:
            st.error("Business sample file not found")
    
    with col3:
        try:
            with open('sample_personal_finances.csv', 'r') as f:
                personal_csv = f.read()
            st.download_button(
                label="Personal Finances Sample",
                data=personal_csv,
                file_name="sample_personal_finances.csv",
                mime="text/csv"
            )
        except:
            st.error("Personal sample file not found")
    
    # Sample format explanation
    with st.expander("Expected Data Format"):
        st.markdown("""
        Your CSV file should include these columns:
        
        | Column | Description | Example |
        | ------ | ----------- | ------- |
        | date | Transaction date (YYYY-MM-DD) | 2023-01-15 |
        | amount | Transaction amount (positive for income, negative for expenses) | 1000.00 |
        | description | Brief description of the transaction | Monthly Salary |
        | category | General category (Income, Expense) | Income |
        | account | Account name | Business Account |
        
        **Notes:**
        - Dates should be in YYYY-MM-DD format
        - Amounts should be numeric (use negative values for expenses)
        - The first three columns (date, amount, description) are required
        """)
