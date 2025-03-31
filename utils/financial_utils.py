import pandas as pd
import numpy as np
from datetime import datetime

def categorize_transactions(df):
    """
    Categorize transactions into income, expense, asset, liability categories
    
    Args:
        df (pandas.DataFrame): Transaction data
    
    Returns:
        pandas.DataFrame: DataFrame with added category column
    """
    # Make a copy to avoid modifying the original
    result = df.copy()
    
    # Ensure amount column is numeric
    if 'amount' in result.columns:
        result['amount'] = pd.to_numeric(result['amount'], errors='coerce')
    
    # Add category column if it doesn't exist
    if 'category' not in result.columns:
        # Try to infer categories based on other columns like description or transaction_type
        if 'description' in result.columns and 'amount' in result.columns:
            # Common income keywords
            income_keywords = ['salary', 'income', 'revenue', 'deposit', 'interest', 'dividend']
            # Common expense keywords
            expense_keywords = ['purchase', 'payment', 'expense', 'fee', 'bill', 'subscription']
            
            def assign_category(row):
                desc = str(row['description']).lower()
                amount = row['amount'] if 'amount' in row else 0
                
                # If amount is positive, likely income
                if amount > 0:
                    if any(keyword in desc for keyword in income_keywords):
                        return 'Income'
                    return 'Income'
                # If amount is negative, likely expense
                elif amount < 0:
                    if any(keyword in desc for keyword in expense_keywords):
                        return 'Expense'
                    return 'Expense'
                else:
                    return 'Unknown'
            
            result['category'] = result.apply(assign_category, axis=1)
    
    return result

def calculate_income_statement(df, start_date=None, end_date=None):
    """
    Calculate income statement from transaction data
    
    Args:
        df (pandas.DataFrame): Transaction data
        start_date (str, optional): Start date for filtering
        end_date (str, optional): End date for filtering
    
    Returns:
        dict: Income statement data
    """
    # Make a copy and categorize transactions
    data = categorize_transactions(df.copy())
    
    # Convert date column to datetime if it exists
    if 'date' in data.columns:
        data['date'] = pd.to_datetime(data['date'], errors='coerce')
        
        # Filter by date range if provided
        if start_date:
            start_date = pd.to_datetime(start_date)
            data = data[data['date'] >= start_date]
        if end_date:
            end_date = pd.to_datetime(end_date)
            data = data[data['date'] <= end_date]
    
    # Calculate income statement components
    if 'amount' in data.columns and 'category' in data.columns:
        # Total income (positive amounts)
        income = data[data['category'] == 'Income']['amount'].sum()
        
        # Total expenses (negative amounts, convert to positive for reporting)
        expenses = abs(data[data['category'] == 'Expense']['amount'].sum())
        
        # Net income
        net_income = income - expenses
        
        # Group expenses by subcategory if available
        expense_breakdown = {}
        if 'subcategory' in data.columns:
            for subcategory, group in data[data['category'] == 'Expense'].groupby('subcategory'):
                expense_breakdown[subcategory] = abs(group['amount'].sum())
        
        # Group income by subcategory if available
        income_breakdown = {}
        if 'subcategory' in data.columns:
            for subcategory, group in data[data['category'] == 'Income'].groupby('subcategory'):
                income_breakdown[subcategory] = group['amount'].sum()
        
        return {
            'total_income': float(income),
            'total_expenses': float(expenses),
            'net_income': float(net_income),
            'expense_breakdown': expense_breakdown,
            'income_breakdown': income_breakdown,
            'time_period': {
                'start_date': start_date.strftime('%Y-%m-%d') if start_date else None,
                'end_date': end_date.strftime('%Y-%m-%d') if end_date else None
            }
        }
    else:
        return {
            'error': 'Data format does not contain required columns (amount, category)'
        }

def calculate_balance_sheet(df, as_of_date=None):
    """
    Calculate balance sheet from transaction data
    
    Args:
        df (pandas.DataFrame): Transaction data
        as_of_date (str, optional): Date for the balance sheet
    
    Returns:
        dict: Balance sheet data
    """
    # Make a copy and categorize transactions
    data = categorize_transactions(df.copy())
    
    # Convert date column to datetime if it exists
    if 'date' in data.columns:
        data['date'] = pd.to_datetime(data['date'], errors='coerce')
        
        # Filter by date if provided
        if as_of_date:
            as_of_date = pd.to_datetime(as_of_date)
            data = data[data['date'] <= as_of_date]
    
    # Initialize balance sheet components
    assets = 0
    liabilities = 0
    equity = 0
    
    # If account_type or similar column exists, use it for balance sheet calculation
    if 'account_type' in data.columns and 'amount' in data.columns:
        # Sum up assets
        asset_accounts = ['cash', 'bank', 'investment', 'receivable', 'asset']
        asset_condition = data['account_type'].str.lower().isin(asset_accounts)
        assets = data[asset_condition]['amount'].sum()
        
        # Sum up liabilities
        liability_accounts = ['loan', 'credit', 'payable', 'debt', 'liability']
        liability_condition = data['account_type'].str.lower().isin(liability_accounts)
        liabilities = abs(data[liability_condition]['amount'].sum())
        
        # Calculate equity (assets - liabilities)
        equity = assets - liabilities
    else:
        # Simplified approach: assets are positive balances, liabilities are negative
        if 'amount' in data.columns:
            assets = data[data['amount'] > 0]['amount'].sum()
            liabilities = abs(data[data['amount'] < 0]['amount'].sum())
            equity = assets - liabilities
    
    return {
        'total_assets': float(assets),
        'total_liabilities': float(liabilities),
        'total_equity': float(equity),
        'as_of_date': as_of_date.strftime('%Y-%m-%d') if as_of_date else datetime.now().strftime('%Y-%m-%d')
    }

def calculate_cash_flow(df, start_date=None, end_date=None):
    """
    Calculate cash flow statement from transaction data
    
    Args:
        df (pandas.DataFrame): Transaction data
        start_date (str, optional): Start date for filtering
        end_date (str, optional): End date for filtering
    
    Returns:
        dict: Cash flow statement data
    """
    # Make a copy and categorize transactions
    data = df.copy()
    
    # Convert date column to datetime if it exists
    if 'date' in data.columns:
        data['date'] = pd.to_datetime(data['date'], errors='coerce')
        
        # Filter by date range if provided
        if start_date:
            start_date = pd.to_datetime(start_date)
            data = data[data['date'] >= start_date]
        if end_date:
            end_date = pd.to_datetime(end_date)
            data = data[data['date'] <= end_date]
    
    # Initialize cash flow components
    operating_cash_flow = 0
    investing_cash_flow = 0
    financing_cash_flow = 0
    
    # If transaction_type or similar column exists, use it for cash flow calculation
    if 'transaction_type' in data.columns and 'amount' in data.columns:
        # Operating cash flow
        operating_types = ['revenue', 'expense', 'sale', 'purchase', 'operating']
        operating_condition = data['transaction_type'].str.lower().isin(operating_types)
        operating_cash_flow = data[operating_condition]['amount'].sum()
        
        # Investing cash flow
        investing_types = ['investment', 'asset purchase', 'asset sale', 'investing']
        investing_condition = data['transaction_type'].str.lower().isin(investing_types)
        investing_cash_flow = data[investing_condition]['amount'].sum()
        
        # Financing cash flow
        financing_types = ['loan', 'dividend', 'equity', 'financing']
        financing_condition = data['transaction_type'].str.lower().isin(financing_types)
        financing_cash_flow = data[financing_condition]['amount'].sum()
    else:
        # Simplified approach based on categorized transactions
        categorized_data = categorize_transactions(data)
        
        # Operating cash flow (income - expenses)
        if 'category' in categorized_data.columns and 'amount' in categorized_data.columns:
            income = categorized_data[categorized_data['category'] == 'Income']['amount'].sum()
            expenses = abs(categorized_data[categorized_data['category'] == 'Expense']['amount'].sum())
            operating_cash_flow = income - expenses
    
    # Calculate net cash flow
    net_cash_flow = operating_cash_flow + investing_cash_flow + financing_cash_flow
    
    return {
        'operating_cash_flow': float(operating_cash_flow),
        'investing_cash_flow': float(investing_cash_flow),
        'financing_cash_flow': float(financing_cash_flow),
        'net_cash_flow': float(net_cash_flow),
        'time_period': {
            'start_date': start_date.strftime('%Y-%m-%d') if start_date else None,
            'end_date': end_date.strftime('%Y-%m-%d') if end_date else None
        }
    }

def calculate_financial_ratios(df):
    """
    Calculate key financial ratios from transaction data
    
    Args:
        df (pandas.DataFrame): Transaction data
    
    Returns:
        dict: Financial ratios
    """
    # Calculate income statement and balance sheet for ratio calculation
    income_statement = calculate_income_statement(df)
    balance_sheet = calculate_balance_sheet(df)
    
    # Extract key metrics
    total_revenue = income_statement.get('total_income', 0)
    net_income = income_statement.get('net_income', 0)
    total_assets = balance_sheet.get('total_assets', 0)
    total_liabilities = balance_sheet.get('total_liabilities', 0)
    total_equity = balance_sheet.get('total_equity', 0)
    
    # Calculate ratios (with safety checks to avoid division by zero)
    profit_margin = (net_income / total_revenue) if total_revenue else 0
    return_on_assets = (net_income / total_assets) if total_assets else 0
    return_on_equity = (net_income / total_equity) if total_equity else 0
    debt_to_equity = (total_liabilities / total_equity) if total_equity else 0
    asset_to_liability = (total_assets / total_liabilities) if total_liabilities else 0
    
    return {
        'profit_margin': float(profit_margin),
        'return_on_assets': float(return_on_assets),
        'return_on_equity': float(return_on_equity),
        'debt_to_equity': float(debt_to_equity),
        'asset_to_liability': float(asset_to_liability)
    }

def summarize_financial_data(df):
    """
    Create a comprehensive summary of financial data for AI analysis
    with enhanced time-based metrics and trend analysis
    
    Args:
        df (pandas.DataFrame): Transaction data
    
    Returns:
        dict: Financial data summary
    """
    # Get date range from the data
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        min_date = df['date'].min().strftime('%Y-%m-%d') if not pd.isna(df['date'].min()) else None
        max_date = df['date'].max().strftime('%Y-%m-%d') if not pd.isna(df['date'].max()) else None
    else:
        min_date = None
        max_date = None
    
    # Calculate financial statements
    income_statement = calculate_income_statement(df)
    balance_sheet = calculate_balance_sheet(df)
    cash_flow = calculate_cash_flow(df)
    ratios = calculate_financial_ratios(df)
    
    # Get transaction statistics
    transaction_count = len(df)
    avg_transaction = df['amount'].mean() if 'amount' in df.columns else 0
    
    # Create time-based analysis and trends
    time_periods = []
    income_by_category = {}
    expense_by_category = {}
    
    # Create categorized transaction data
    categorized_df = categorize_transactions(df.copy())
    
    # Extract income/expense categories
    if 'category' in categorized_df.columns and 'amount' in categorized_df.columns:
        # Income categories
        income_data = categorized_df[categorized_df['category'] == 'Income']
        if 'subcategory' in income_data.columns:
            for subcat, group in income_data.groupby('subcategory'):
                income_by_category[subcat] = float(group['amount'].sum())
        else:
            # If no subcategory, try using description as a proxy
            if 'description' in income_data.columns:
                for desc, group in income_data.groupby('description'):
                    income_by_category[desc] = float(group['amount'].sum())
            else:
                income_by_category['General Income'] = float(income_data['amount'].sum())
                
        # Expense categories
        expense_data = categorized_df[categorized_df['category'] == 'Expense']
        if 'subcategory' in expense_data.columns:
            for subcat, group in expense_data.groupby('subcategory'):
                expense_by_category[subcat] = float(abs(group['amount'].sum()))
        else:
            # If no subcategory, try using description as a proxy
            if 'description' in expense_data.columns:
                for desc, group in expense_data.groupby('description'):
                    expense_by_category[desc] = float(abs(group['amount'].sum()))
            else:
                expense_by_category['General Expenses'] = float(abs(expense_data['amount'].sum()))
    
    # Time-based analysis
    if 'date' in categorized_df.columns:
        # Add month column for monthly analysis
        categorized_df['month'] = categorized_df['date'].dt.strftime('%Y-%m')
        
        # Group by month
        monthly_groups = categorized_df.groupby('month')
        
        # Create monthly summaries
        for month, month_df in monthly_groups:
            # Calculate income and expense for this month
            month_income = month_df[month_df['category'] == 'Income']['amount'].sum()
            month_expense = abs(month_df[month_df['category'] == 'Expense']['amount'].sum())
            month_net = month_income - month_expense
            
            # Monthly income by category
            month_income_categories = {}
            month_income_data = month_df[month_df['category'] == 'Income']
            if 'subcategory' in month_income_data.columns:
                for subcat, group in month_income_data.groupby('subcategory'):
                    month_income_categories[subcat] = float(group['amount'].sum())
            elif 'description' in month_income_data.columns:
                for desc, group in month_income_data.groupby('description'):
                    month_income_categories[desc] = float(group['amount'].sum())
            
            # Monthly expense by category
            month_expense_categories = {}
            month_expense_data = month_df[month_df['category'] == 'Expense']
            if 'subcategory' in month_expense_data.columns:
                for subcat, group in month_expense_data.groupby('subcategory'):
                    month_expense_categories[subcat] = float(abs(group['amount'].sum()))
            elif 'description' in month_expense_data.columns:
                for desc, group in month_expense_data.groupby('description'):
                    month_expense_categories[desc] = float(abs(group['amount'].sum()))
            
            # Add to time periods list
            time_periods.append({
                'period': month,
                'income': float(month_income),
                'expense': float(month_expense),
                'net': float(month_net),
                'income_categories': month_income_categories,
                'expense_categories': month_expense_categories
            })
        
        # Sort periods chronologically
        time_periods.sort(key=lambda x: x['period'])
        
        # Add trend analysis
        if len(time_periods) > 1:
            # Add trends for each time period (except first)
            for i in range(1, len(time_periods)):
                current = time_periods[i]
                previous = time_periods[i-1]
                
                # Income trend
                current['income_change'] = current['income'] - previous['income']
                if previous['income'] > 0:
                    current['income_change_pct'] = (current['income_change'] / previous['income']) * 100
                else:
                    current['income_change_pct'] = 0 if current['income_change'] == 0 else float('inf')
                
                # Expense trend
                current['expense_change'] = current['expense'] - previous['expense']
                if previous['expense'] > 0:
                    current['expense_change_pct'] = (current['expense_change'] / previous['expense']) * 100
                else:
                    current['expense_change_pct'] = 0 if current['expense_change'] == 0 else float('inf')
                
                # Net income trend
                current['net_change'] = current['net'] - previous['net']
                if previous['net'] != 0:
                    current['net_change_pct'] = (current['net_change'] / abs(previous['net'])) * 100
                else:
                    current['net_change_pct'] = 0 if current['net_change'] == 0 else float('inf')
    
    # Create comprehensive summary with all collected data
    summary = {
        'data_overview': {
            'transaction_count': transaction_count,
            'date_range': {'start': min_date, 'end': max_date},
            'average_transaction': float(avg_transaction)
        },
        'income_total': income_statement.get('total_income', 0),
        'expense_total': income_statement.get('total_expenses', 0),
        'net_income': income_statement.get('net_income', 0),
        'income_categories': income_by_category,
        'expense_categories': expense_by_category,
        'assets': balance_sheet.get('assets', {}),
        'liabilities': balance_sheet.get('liabilities', {}),
        'equity': balance_sheet.get('total_equity', 0),
        'financial_ratios': ratios,
        'time_periods': time_periods,
        'income_statement': income_statement,
        'balance_sheet': balance_sheet,
        'cash_flow': cash_flow
    }
    
    # Add overall trend analysis if we have time periods
    if len(time_periods) > 1:
        first_period = time_periods[0]
        last_period = time_periods[-1]
        
        # Calculate overall trends
        income_change = last_period['income'] - first_period['income']
        expense_change = last_period['expense'] - first_period['expense']
        net_change = last_period['net'] - first_period['net']
        
        # Calculate percentages
        income_change_pct = (income_change / first_period['income']) * 100 if first_period['income'] > 0 else 0
        expense_change_pct = (expense_change / first_period['expense']) * 100 if first_period['expense'] > 0 else 0
        net_change_pct = (net_change / abs(first_period['net'])) * 100 if first_period['net'] != 0 else 0
        
        # Add trend summary to results
        summary['trends'] = {
            'period_count': len(time_periods),
            'start_period': first_period['period'],
            'end_period': last_period['period'],
            'income_change': float(income_change),
            'income_change_pct': float(income_change_pct),
            'expense_change': float(expense_change),
            'expense_change_pct': float(expense_change_pct),
            'net_change': float(net_change),
            'net_change_pct': float(net_change_pct),
            'income_trend': 'increasing' if income_change > 0 else 'decreasing' if income_change < 0 else 'stable',
            'expense_trend': 'increasing' if expense_change > 0 else 'decreasing' if expense_change < 0 else 'stable',
            'net_trend': 'improving' if net_change > 0 else 'worsening' if net_change < 0 else 'stable'
        }
    
    return summary
