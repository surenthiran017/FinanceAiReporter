import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_utils import filter_data_by_date, get_date_range_options
from utils.financial_utils import (
    categorize_transactions, 
    calculate_income_statement,
    calculate_balance_sheet,
    calculate_cash_flow,
    calculate_financial_ratios,
    summarize_financial_data
)
from utils.report_utils import generate_report_visualizations

def render_visualizations():
    """Render financial data visualizations component"""
    
    st.header("📈 Financial Visualizations")
    st.markdown("Interactive charts and visualizations of your financial data.")
    
    # Get transaction data
    if not st.session_state.data_uploaded or st.session_state.transaction_data is None:
        st.warning("Please upload transaction data first to view visualizations.")
        return
    
    # Get transaction data and date range options
    df = st.session_state.transaction_data
    date_range = get_date_range_options(df)
    
    # Date range filter
    st.subheader("Filter Data")
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Start Date", 
            value=date_range['min_date'],
            min_value=date_range['min_date'],
            max_value=date_range['max_date']
        )
    
    with col2:
        end_date = st.date_input(
            "End Date", 
            value=date_range['max_date'],
            min_value=start_date,
            max_value=date_range['max_date']
        )
    
    # Apply date filter
    filtered_df = filter_data_by_date(df, start_date, end_date)
    
    # Ensure data has necessary columns
    if 'date' not in filtered_df.columns or 'amount' not in filtered_df.columns:
        st.error("Data must contain 'date' and 'amount' columns for visualization.")
        return
    
    # Calculate financial summaries for visualizations
    data_summary = summarize_financial_data(filtered_df)
    
    # Create tabs for different visualization categories
    tab_names = ["Income & Expenses", "Balance Sheet", "Cash Flow", "Trends", "Financial Health"]
    tabs = st.tabs(tab_names)
    
    # Income & Expenses Tab
    with tabs[0]:
        st.subheader("Income and Expenses Analysis")
        
        # Get income statement data
        income_data = data_summary['income_statement']
        
        # Create income vs. expenses chart
        income_expense_data = {
            'Category': ['Income', 'Expenses', 'Net Income'],
            'Amount': [
                income_data.get('total_income', 0),
                income_data.get('total_expenses', 0),
                income_data.get('net_income', 0)
            ]
        }
        
        income_expense_df = pd.DataFrame(income_expense_data)
        
        fig_income_expense = px.bar(
            income_expense_df,
            x='Category',
            y='Amount',
            title="Income vs. Expenses Summary",
            color='Category',
            color_discrete_map={
                'Income': '#4CAF50',
                'Expenses': '#F44336',
                'Net Income': '#2196F3'
            }
        )
        
        st.plotly_chart(fig_income_expense, use_container_width=True)
        
        # Income and expense breakdowns
        col1, col2 = st.columns(2)
        
        with col1:
            # Income breakdown if available
            income_breakdown = income_data.get('income_breakdown', {})
            if income_breakdown:
                income_breakdown_df = pd.DataFrame({
                    'Category': list(income_breakdown.keys()),
                    'Amount': list(income_breakdown.values())
                })
                
                fig_income_breakdown = px.pie(
                    income_breakdown_df,
                    values='Amount',
                    names='Category',
                    title="Income Breakdown",
                    hole=0.4
                )
                
                st.plotly_chart(fig_income_breakdown, use_container_width=True)
            else:
                st.info("No detailed income categories available in the data.")
        
        with col2:
            # Expense breakdown if available
            expense_breakdown = income_data.get('expense_breakdown', {})
            if expense_breakdown:
                expense_breakdown_df = pd.DataFrame({
                    'Category': list(expense_breakdown.keys()),
                    'Amount': list(expense_breakdown.values())
                })
                
                fig_expense_breakdown = px.pie(
                    expense_breakdown_df,
                    values='Amount',
                    names='Category',
                    title="Expense Breakdown",
                    hole=0.4
                )
                
                st.plotly_chart(fig_expense_breakdown, use_container_width=True)
            else:
                st.info("No detailed expense categories available in the data.")
    
    # Balance Sheet Tab
    with tabs[1]:
        st.subheader("Balance Sheet Analysis")
        
        # Get balance sheet data
        balance_data = data_summary['balance_sheet']
        
        # Assets vs Liabilities chart
        balance_chart_data = {
            'Category': ['Assets', 'Liabilities', 'Equity'],
            'Amount': [
                balance_data.get('total_assets', 0),
                balance_data.get('total_liabilities', 0),
                balance_data.get('total_equity', 0)
            ]
        }
        
        balance_df = pd.DataFrame(balance_chart_data)
        
        fig_balance = px.bar(
            balance_df,
            x='Category',
            y='Amount',
            title="Balance Sheet Components",
            color='Category',
            color_discrete_map={
                'Assets': '#4CAF50',
                'Liabilities': '#F44336',
                'Equity': '#2196F3'
            }
        )
        
        st.plotly_chart(fig_balance, use_container_width=True)
        
        # Balance Sheet Composition Pie Chart
        fig_composition = px.pie(
            balance_df,
            values='Amount',
            names='Category',
            title="Balance Sheet Composition",
            color='Category',
            color_discrete_map={
                'Assets': '#4CAF50',
                'Liabilities': '#F44336',
                'Equity': '#2196F3'
            }
        )
        
        st.plotly_chart(fig_composition, use_container_width=True)
        
        # Display accounting equation
        assets = balance_data.get('total_assets', 0)
        liabilities = balance_data.get('total_liabilities', 0)
        equity = balance_data.get('total_equity', 0)
        
        st.markdown("### Accounting Equation")
        st.markdown(f"**Assets** (${assets:,.2f}) = **Liabilities** (${liabilities:,.2f}) + **Equity** (${equity:,.2f})")
        
        # Check if equation balances (allowing for small float precision errors)
        is_balanced = abs((assets) - (liabilities + equity)) < 0.01
        if is_balanced:
            st.success("✅ The accounting equation is balanced.")
        else:
            st.warning("⚠️ The accounting equation is not balanced. This may indicate data issues.")
    
    # Cash Flow Tab
    with tabs[2]:
        st.subheader("Cash Flow Analysis")
        
        # Get cash flow data
        cash_flow_data = data_summary['cash_flow']
        
        # Cash Flow Components Chart
        cash_flow_chart_data = {
            'Category': ['Operating', 'Investing', 'Financing', 'Net Cash Flow'],
            'Amount': [
                cash_flow_data.get('operating_cash_flow', 0),
                cash_flow_data.get('investing_cash_flow', 0),
                cash_flow_data.get('financing_cash_flow', 0),
                cash_flow_data.get('net_cash_flow', 0)
            ]
        }
        
        cash_flow_df = pd.DataFrame(cash_flow_chart_data)
        
        fig_cash_flow = px.bar(
            cash_flow_df,
            x='Category',
            y='Amount',
            title="Cash Flow Components",
            color='Category',
            color_discrete_map={
                'Operating': '#4CAF50',
                'Investing': '#FF9800',
                'Financing': '#2196F3',
                'Net Cash Flow': '#9C27B0'
            }
        )
        
        st.plotly_chart(fig_cash_flow, use_container_width=True)
        
        # Cash Flow Waterfall Chart
        operating = cash_flow_data.get('operating_cash_flow', 0)
        investing = cash_flow_data.get('investing_cash_flow', 0)
        financing = cash_flow_data.get('financing_cash_flow', 0)
        net_cash_flow = cash_flow_data.get('net_cash_flow', 0)
        
        fig_waterfall = go.Figure(go.Waterfall(
            name="Cash Flow",
            orientation="v",
            measure=["relative", "relative", "relative", "total"],
            x=["Operating", "Investing", "Financing", "Net Cash Flow"],
            textposition="outside",
            text=[f"${operating:,.2f}", f"${investing:,.2f}", f"${financing:,.2f}", f"${net_cash_flow:,.2f}"],
            y=[operating, investing, financing, net_cash_flow],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))
        
        fig_waterfall.update_layout(
            title="Cash Flow Waterfall Chart",
            showlegend=False
        )
        
        st.plotly_chart(fig_waterfall, use_container_width=True)
    
    # Trends Tab
    with tabs[3]:
        st.subheader("Financial Trends Over Time")
        
        # Make sure we have date data
        if 'date' in filtered_df.columns and 'amount' in filtered_df.columns:
            # Create a copy with categorized transactions
            trend_df = categorize_transactions(filtered_df.copy())
            
            # Ensure date is datetime
            trend_df['date'] = pd.to_datetime(trend_df['date'])
            
            # Create month-year column for aggregation
            trend_df['month_year'] = trend_df['date'].dt.strftime('%Y-%m')
            
            # Monthly Income and Expenses
            monthly_data = trend_df.groupby(['month_year', 'category'])['amount'].sum().reset_index()
            
            # Filter income and expenses
            monthly_income = monthly_data[monthly_data['category'] == 'Income']
            monthly_expenses = monthly_data[monthly_data['category'] == 'Expense']
            
            # Create line chart for income and expenses over time
            fig_monthly = go.Figure()
            
            if not monthly_income.empty:
                fig_monthly.add_trace(go.Scatter(
                    x=monthly_income['month_year'],
                    y=monthly_income['amount'],
                    mode='lines+markers',
                    name='Income',
                    line=dict(color='#4CAF50', width=3)
                ))
            
            if not monthly_expenses.empty:
                # Convert expense amounts to positive for display
                monthly_expenses['amount'] = monthly_expenses['amount'].abs()
                
                fig_monthly.add_trace(go.Scatter(
                    x=monthly_expenses['month_year'],
                    y=monthly_expenses['amount'],
                    mode='lines+markers',
                    name='Expenses',
                    line=dict(color='#F44336', width=3)
                ))
            
            fig_monthly.update_layout(
                title="Monthly Income and Expenses",
                xaxis_title="Month",
                yaxis_title="Amount ($)",
                legend_title="Category",
                hovermode="x unified"
            )
            
            st.plotly_chart(fig_monthly, use_container_width=True)
            
            # Monthly Net Income
            monthly_net = trend_df.groupby('month_year')['amount'].sum().reset_index()
            
            fig_net = px.bar(
                monthly_net,
                x='month_year',
                y='amount',
                title="Monthly Net Income",
                color_discrete_sequence=['#2196F3']
            )
            
            fig_net.update_layout(
                xaxis_title="Month",
                yaxis_title="Net Income ($)",
                hovermode="x unified"
            )
            
            # Add a horizontal line at y=0
            fig_net.add_shape(
                type="line",
                x0=0,
                y0=0,
                x1=1,
                y1=0,
                xref="paper",
                yref="y",
                line=dict(color="red", width=2, dash="dash")
            )
            
            st.plotly_chart(fig_net, use_container_width=True)
            
            # Cumulative Growth
            monthly_net_sorted = monthly_net.sort_values('month_year')
            monthly_net_sorted['cumulative'] = monthly_net_sorted['amount'].cumsum()
            
            fig_cumulative = px.line(
                monthly_net_sorted,
                x='month_year',
                y='cumulative',
                title="Cumulative Financial Growth",
                markers=True
            )
            
            fig_cumulative.update_layout(
                xaxis_title="Month",
                yaxis_title="Cumulative Amount ($)",
                hovermode="x unified"
            )
            
            fig_cumulative.add_shape(
                type="line",
                x0=0,
                y0=0,
                x1=1,
                y1=0,
                xref="paper",
                yref="y",
                line=dict(color="red", width=2, dash="dash")
            )
            
            st.plotly_chart(fig_cumulative, use_container_width=True)
        else:
            st.warning("Trend analysis requires transaction data with date and amount columns.")
    
    # Financial Health Tab
    with tabs[4]:
        st.subheader("Financial Health Indicators")
        
        # Get financial ratios
        ratios = data_summary['financial_ratios']
        
        # Create financial ratios chart
        ratio_names = ['Profit Margin', 'Return on Assets', 'Return on Equity']
        ratio_values = [
            ratios.get('profit_margin', 0),
            ratios.get('return_on_assets', 0),
            ratios.get('return_on_equity', 0)
        ]
        
        # Convert to percentages for display
        ratio_percentages = [value * 100 for value in ratio_values]
        
        fig_ratios = px.bar(
            x=ratio_names,
            y=ratio_percentages,
            title="Key Financial Performance Ratios",
            labels={'x': 'Ratio', 'y': 'Percentage (%)'},
            color=ratio_names,
            text=[f"{value:.2f}%" for value in ratio_percentages]
        )
        
        fig_ratios.update_traces(textposition='outside')
        
        st.plotly_chart(fig_ratios, use_container_width=True)
        
        # Create debt and liquidity ratios chart
        other_ratio_names = ['Debt to Equity', 'Asset to Liability']
        other_ratio_values = [
            ratios.get('debt_to_equity', 0),
            ratios.get('asset_to_liability', 0)
        ]
        
        fig_other_ratios = px.bar(
            x=other_ratio_names,
            y=other_ratio_values,
            title="Debt and Liquidity Ratios",
            labels={'x': 'Ratio', 'y': 'Value'},
            color=other_ratio_names,
            text=[f"{value:.2f}" for value in other_ratio_values]
        )
        
        fig_other_ratios.update_traces(textposition='outside')
        
        st.plotly_chart(fig_other_ratios, use_container_width=True)
        
        # Financial Health Gauge
        # Create a simplified financial health score based on ratios
        profit_margin = ratios.get('profit_margin', 0)
        roa = ratios.get('return_on_assets', 0)
        roe = ratios.get('return_on_equity', 0)
        debt_equity = ratios.get('debt_to_equity', 0)
        
        # Simple score calculation (example logic, can be refined)
        score = 0
        if profit_margin > 0.15:
            score += 25
        elif profit_margin > 0.05:
            score += 15
        elif profit_margin > 0:
            score += 5
        
        if roa > 0.10:
            score += 25
        elif roa > 0.03:
            score += 15
        elif roa > 0:
            score += 5
        
        if roe > 0.15:
            score += 25
        elif roe > 0.05:
            score += 15
        elif roe > 0:
            score += 5
        
        if debt_equity < 0.5:
            score += 25
        elif debt_equity < 1.5:
            score += 15
        elif debt_equity < 3:
            score += 5
        
        # Create gauge chart
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={'text': "Financial Health Score"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#2196F3"},
                'steps': [
                    {'range': [0, 25], 'color': "#F44336"},
                    {'range': [25, 50], 'color': "#FF9800"},
                    {'range': [50, 75], 'color': "#FFEB3B"},
                    {'range': [75, 100], 'color': "#4CAF50"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': score
                }
            }
        ))
        
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Health score interpretation
        st.subheader("Health Score Interpretation")
        
        if score >= 75:
            st.success("🌟 Excellent Financial Health (75-100)")
            st.markdown("""
            Your financial indicators show strong performance across the board. You have:
            - Good profitability
            - Effective use of assets
            - Healthy return on equity
            - Manageable debt levels
            """)
        elif score >= 50:
            st.info("✅ Good Financial Health (50-74)")
            st.markdown("""
            Your financials show solid performance with some room for improvement:
            - Reasonable profitability
            - Adequate returns
            - Manageable debt levels
            """)
        elif score >= 25:
            st.warning("⚠️ Fair Financial Health (25-49)")
            st.markdown("""
            Your financial health shows some concerning indicators that need attention:
            - Limited profitability
            - Below-average returns
            - Potentially concerning debt levels
            """)
        else:
            st.error("❗ Needs Improvement (0-24)")
            st.markdown("""
            Your financial indicators suggest significant challenges:
            - Profitability issues
            - Poor returns on assets and equity
            - Potentially unsustainable debt levels
            
            Consider reviewing your revenue streams, cost structure, and debt management strategies.
            """)
