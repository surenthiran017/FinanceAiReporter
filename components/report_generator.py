import streamlit as st
import pandas as pd
import os
from datetime import datetime
from utils.financial_utils import (
    calculate_income_statement,
    calculate_balance_sheet,
    calculate_cash_flow,
    calculate_financial_ratios,
    summarize_financial_data
)
from utils.report_utils import (
    generate_income_statement_pdf,
    generate_balance_sheet_pdf,
    generate_cash_flow_pdf,
    generate_financial_summary_pdf,
    get_download_link
)
from utils.data_utils import filter_data_by_date, get_date_range_options

# Check for available APIs and import the appropriate module
gemini_api_available = os.environ.get("GEMINI_API_KEY") is not None

# Import the appropriate report generation function based on available API keys
if gemini_api_available:
    from utils.gemini_utils import generate_report_content_with_gemini as generate_report_content
else:
    from utils.openai_utils import generate_report_content

def render_report_generator():
    """Render the report generator component for creating financial reports"""
    
    st.header("📝 Generate Financial Reports")
    st.markdown("Generate professional financial reports based on your transaction data.")
    
    # Get transaction data
    if not st.session_state.data_uploaded or st.session_state.transaction_data is None:
        st.warning("Please upload transaction data first to generate reports.")
        return
    
    # Get transaction data and date range options
    df = st.session_state.transaction_data
    date_range = get_date_range_options(df)
    
    # Initialize generated_reports in session state if not exists
    if "generated_reports" not in st.session_state:
        st.session_state.generated_reports = {}
    
    # Report selection and date range filters
    st.subheader("Report Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.selectbox(
            "Select Report Type",
            [
                "Income Statement",
                "Balance Sheet",
                "Cash Flow Statement",
                "Financial Summary"
            ]
        )
    
    with col2:
        if report_type == "Balance Sheet":
            as_of_date = st.date_input(
                "As of Date",
                value=date_range['max_date'],
                min_value=date_range['min_date'],
                max_value=date_range['max_date']
            )
            start_date = None
            end_date = as_of_date
        else:
            start_date = st.date_input(
                "Start Date",
                value=date_range['min_date'],
                min_value=date_range['min_date'],
                max_value=date_range['max_date']
            )
            end_date = st.date_input(
                "End Date",
                value=date_range['max_date'],
                min_value=start_date,
                max_value=date_range['max_date']
            )
            as_of_date = end_date
    
    # Apply date filters
    filtered_df = filter_data_by_date(df, start_date, end_date)
    
    # Button to generate report
    if st.button(f"Generate {report_type}"):
        with st.spinner(f"Generating {report_type}..."):
            try:
                # Generate report data based on type
                if report_type == "Income Statement":
                    report_data = calculate_income_statement(filtered_df)
                    report_period = f"{start_date} to {end_date}"
                    pdf_buffer = generate_income_statement_pdf(report_data, report_period)
                    report_key = f"income_statement_{start_date}_{end_date}"
                    
                elif report_type == "Balance Sheet":
                    report_data = calculate_balance_sheet(filtered_df, as_of_date)
                    pdf_buffer = generate_balance_sheet_pdf(report_data, as_of_date.strftime('%Y-%m-%d'))
                    report_key = f"balance_sheet_{as_of_date}"
                    
                elif report_type == "Cash Flow Statement":
                    report_data = calculate_cash_flow(filtered_df, start_date, end_date)
                    report_period = f"{start_date} to {end_date}"
                    pdf_buffer = generate_cash_flow_pdf(report_data, report_period)
                    report_key = f"cash_flow_{start_date}_{end_date}"
                    
                elif report_type == "Financial Summary":
                    report_data = summarize_financial_data(filtered_df)
                    report_period = f"{start_date} to {end_date}"
                    pdf_buffer = generate_financial_summary_pdf(report_data, report_period)
                    report_key = f"financial_summary_{start_date}_{end_date}"
                
                # Store generated report in session state
                st.session_state.generated_reports[report_key] = {
                    'type': report_type,
                    'data': report_data,
                    'pdf_buffer': pdf_buffer,
                    'period': f"{start_date} to {end_date}" if report_type != "Balance Sheet" else f"As of {as_of_date}",
                    'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                st.success(f"{report_type} successfully generated!")
                
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")
    
    # Display generated reports
    st.markdown("---")
    st.subheader("Generated Reports")
    
    if not st.session_state.generated_reports:
        st.info("No reports generated yet. Use the form above to generate reports.")
    else:
        # Create tabs for each report type
        tab_names = ["All Reports", "Income Statements", "Balance Sheets", "Cash Flow Statements", "Financial Summaries"]
        tabs = st.tabs(tab_names)
        
        with tabs[0]:  # All Reports
            st.markdown("### All Generated Reports")
            for key, report in st.session_state.generated_reports.items():
                with st.expander(f"{report['type']} - {report['period']}"):
                    st.markdown(f"**Generated:** {report['generated_at']}")
                    st.markdown(f"**Period:** {report['period']}")
                    
                    # Display download link
                    file_name = f"{report['type'].lower().replace(' ', '_')}_{report['period'].replace(' ', '_')}.pdf"
                    st.markdown(get_download_link(report['pdf_buffer'], file_name, "application/pdf"), unsafe_allow_html=True)
                    
                    # Display report summary
                    if report['type'] == "Income Statement":
                        data = report['data']
                        st.markdown(f"**Total Income:** ${data.get('total_income', 0):,.2f}")
                        st.markdown(f"**Total Expenses:** ${data.get('total_expenses', 0):,.2f}")
                        st.markdown(f"**Net Income:** ${data.get('net_income', 0):,.2f}")
                    
                    elif report['type'] == "Balance Sheet":
                        data = report['data']
                        st.markdown(f"**Total Assets:** ${data.get('total_assets', 0):,.2f}")
                        st.markdown(f"**Total Liabilities:** ${data.get('total_liabilities', 0):,.2f}")
                        st.markdown(f"**Total Equity:** ${data.get('total_equity', 0):,.2f}")
                    
                    elif report['type'] == "Cash Flow Statement":
                        data = report['data']
                        st.markdown(f"**Operating Cash Flow:** ${data.get('operating_cash_flow', 0):,.2f}")
                        st.markdown(f"**Investing Cash Flow:** ${data.get('investing_cash_flow', 0):,.2f}")
                        st.markdown(f"**Financing Cash Flow:** ${data.get('financing_cash_flow', 0):,.2f}")
                        st.markdown(f"**Net Cash Flow:** ${data.get('net_cash_flow', 0):,.2f}")
                    
                    elif report['type'] == "Financial Summary":
                        # Display basic summary information
                        st.markdown("This report contains a comprehensive summary of financial performance.")
                        
                        if 'financial_ratios' in report['data']:
                            ratios = report['data']['financial_ratios']
                            st.markdown("### Key Financial Ratios")
                            st.markdown(f"**Profit Margin:** {ratios.get('profit_margin', 0):.2%}")
                            st.markdown(f"**Return on Assets:** {ratios.get('return_on_assets', 0):.2%}")
                            st.markdown(f"**Return on Equity:** {ratios.get('return_on_equity', 0):.2%}")
        
        # Filter reports by type for other tabs
        with tabs[1]:  # Income Statements
            st.markdown("### Income Statements")
            income_reports = {k: v for k, v in st.session_state.generated_reports.items() if v['type'] == 'Income Statement'}
            if not income_reports:
                st.info("No income statements generated yet.")
            else:
                for key, report in income_reports.items():
                    with st.expander(f"Income Statement - {report['period']}"):
                        st.markdown(f"**Generated:** {report['generated_at']}")
                        st.markdown(f"**Period:** {report['period']}")
                        
                        # Display download link
                        file_name = f"income_statement_{report['period'].replace(' ', '_')}.pdf"
                        st.markdown(get_download_link(report['pdf_buffer'], file_name, "application/pdf"), unsafe_allow_html=True)
                        
                        # Display report summary
                        data = report['data']
                        st.markdown(f"**Total Income:** ${data.get('total_income', 0):,.2f}")
                        st.markdown(f"**Total Expenses:** ${data.get('total_expenses', 0):,.2f}")
                        st.markdown(f"**Net Income:** ${data.get('net_income', 0):,.2f}")
        
        with tabs[2]:  # Balance Sheets
            st.markdown("### Balance Sheets")
            balance_reports = {k: v for k, v in st.session_state.generated_reports.items() if v['type'] == 'Balance Sheet'}
            if not balance_reports:
                st.info("No balance sheets generated yet.")
            else:
                for key, report in balance_reports.items():
                    with st.expander(f"Balance Sheet - {report['period']}"):
                        st.markdown(f"**Generated:** {report['generated_at']}")
                        st.markdown(f"**Period:** {report['period']}")
                        
                        # Display download link
                        file_name = f"balance_sheet_{report['period'].replace(' ', '_')}.pdf"
                        st.markdown(get_download_link(report['pdf_buffer'], file_name, "application/pdf"), unsafe_allow_html=True)
                        
                        # Display report summary
                        data = report['data']
                        st.markdown(f"**Total Assets:** ${data.get('total_assets', 0):,.2f}")
                        st.markdown(f"**Total Liabilities:** ${data.get('total_liabilities', 0):,.2f}")
                        st.markdown(f"**Total Equity:** ${data.get('total_equity', 0):,.2f}")
        
        with tabs[3]:  # Cash Flow Statements
            st.markdown("### Cash Flow Statements")
            cash_flow_reports = {k: v for k, v in st.session_state.generated_reports.items() if v['type'] == 'Cash Flow Statement'}
            if not cash_flow_reports:
                st.info("No cash flow statements generated yet.")
            else:
                for key, report in cash_flow_reports.items():
                    with st.expander(f"Cash Flow Statement - {report['period']}"):
                        st.markdown(f"**Generated:** {report['generated_at']}")
                        st.markdown(f"**Period:** {report['period']}")
                        
                        # Display download link
                        file_name = f"cash_flow_statement_{report['period'].replace(' ', '_')}.pdf"
                        st.markdown(get_download_link(report['pdf_buffer'], file_name, "application/pdf"), unsafe_allow_html=True)
                        
                        # Display report summary
                        data = report['data']
                        st.markdown(f"**Operating Cash Flow:** ${data.get('operating_cash_flow', 0):,.2f}")
                        st.markdown(f"**Investing Cash Flow:** ${data.get('investing_cash_flow', 0):,.2f}")
                        st.markdown(f"**Financing Cash Flow:** ${data.get('financing_cash_flow', 0):,.2f}")
                        st.markdown(f"**Net Cash Flow:** ${data.get('net_cash_flow', 0):,.2f}")
        
        with tabs[4]:  # Financial Summaries
            st.markdown("### Financial Summaries")
            summary_reports = {k: v for k, v in st.session_state.generated_reports.items() if v['type'] == 'Financial Summary'}
            if not summary_reports:
                st.info("No financial summaries generated yet.")
            else:
                for key, report in summary_reports.items():
                    with st.expander(f"Financial Summary - {report['period']}"):
                        st.markdown(f"**Generated:** {report['generated_at']}")
                        st.markdown(f"**Period:** {report['period']}")
                        
                        # Display download link
                        file_name = f"financial_summary_{report['period'].replace(' ', '_')}.pdf"
                        st.markdown(get_download_link(report['pdf_buffer'], file_name, "application/pdf"), unsafe_allow_html=True)
                        
                        # Display abbreviated summary
                        st.markdown("This report contains a comprehensive financial summary including income statement, balance sheet, cash flow, and key financial ratios.")
