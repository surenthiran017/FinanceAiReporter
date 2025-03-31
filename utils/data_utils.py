import pandas as pd
import numpy as np
import io
import base64
from datetime import datetime

def validate_transaction_data(df):
    """
    Validate that the uploaded data has the required columns and format
    
    Args:
        df (pandas.DataFrame): Uploaded data
        
    Returns:
        tuple: (is_valid, message)
    """
    # Define required columns
    required_columns = ['date', 'amount', 'description']
    
    # Check if required columns exist
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    # Validate date column
    try:
        df['date'] = pd.to_datetime(df['date'])
    except Exception:
        return False, "Date column could not be parsed. Please ensure it's in a valid date format (e.g., YYYY-MM-DD)."
    
    # Validate amount column
    try:
        df['amount'] = pd.to_numeric(df['amount'])
    except Exception:
        return False, "Amount column could not be converted to numbers. Please ensure it contains valid numeric values."
    
    # Check for empty data
    if df.empty:
        return False, "The uploaded file contains no data."
    
    # Check for missing values in essential columns
    essential_cols = ['date', 'amount']
    for col in essential_cols:
        if df[col].isna().any():
            missing_count = df[col].isna().sum()
            return False, f"The {col} column contains {missing_count} missing values. Please fix these before uploading."
    
    return True, "Data validation successful."

def preprocess_transaction_data(df):
    """
    Preprocess transaction data for analysis
    
    Args:
        df (pandas.DataFrame): Raw transaction data
        
    Returns:
        pandas.DataFrame: Preprocessed data
    """
    # Make a copy to avoid modifying the original
    processed_df = df.copy()
    
    # Convert date column to datetime
    if 'date' in processed_df.columns:
        processed_df['date'] = pd.to_datetime(processed_df['date'], errors='coerce')
    
    # Convert amount to numeric
    if 'amount' in processed_df.columns:
        processed_df['amount'] = pd.to_numeric(processed_df['amount'], errors='coerce')
    
    # Handle missing values
    for col in processed_df.columns:
        # For numeric columns, fill missing values with 0
        if processed_df[col].dtype in [np.int64, np.float64]:
            processed_df[col].fillna(0, inplace=True)
        # For string/object columns, fill missing values with empty string
        elif processed_df[col].dtype == 'object':
            processed_df[col].fillna('', inplace=True)
    
    # Add month and year columns for time-based analysis
    if 'date' in processed_df.columns:
        processed_df['month'] = processed_df['date'].dt.month
        processed_df['year'] = processed_df['date'].dt.year
        processed_df['month_year'] = processed_df['date'].dt.strftime('%Y-%m')
    
    # Sort by date
    if 'date' in processed_df.columns:
        processed_df.sort_values(by='date', inplace=True)
    
    return processed_df

def get_date_range_options(df):
    """
    Get date range options for filtering data
    
    Args:
        df (pandas.DataFrame): Transaction data
        
    Returns:
        dict: Date range options
    """
    if 'date' not in df.columns:
        return {
            'min_date': datetime.now().date(),
            'max_date': datetime.now().date(),
            'years': [datetime.now().year],
            'months': [datetime.now().month]
        }
    
    # Ensure date column is datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Get min and max dates
    min_date = df['date'].min().date() if not pd.isna(df['date'].min()) else datetime.now().date()
    max_date = df['date'].max().date() if not pd.isna(df['date'].max()) else datetime.now().date()
    
    # Get unique years and months
    years = sorted(df['date'].dt.year.unique().tolist())
    months = sorted(df['date'].dt.month.unique().tolist())
    
    return {
        'min_date': min_date,
        'max_date': max_date,
        'years': years,
        'months': months
    }

def filter_data_by_date(df, start_date=None, end_date=None):
    """
    Filter transaction data by date range
    
    Args:
        df (pandas.DataFrame): Transaction data
        start_date (str, optional): Start date
        end_date (str, optional): End date
        
    Returns:
        pandas.DataFrame: Filtered data
    """
    # Make a copy to avoid modifying the original
    filtered_df = df.copy()
    
    # Ensure date column is datetime
    if 'date' in filtered_df.columns:
        filtered_df['date'] = pd.to_datetime(filtered_df['date'], errors='coerce')
        
        # Filter by start date if provided
        if start_date:
            start_date = pd.to_datetime(start_date)
            filtered_df = filtered_df[filtered_df['date'] >= start_date]
        
        # Filter by end date if provided
        if end_date:
            end_date = pd.to_datetime(end_date)
            filtered_df = filtered_df[filtered_df['date'] <= end_date]
    
    return filtered_df

def generate_sample_csv_content():
    """
    Generate sample CSV content for the template
    
    Returns:
        str: CSV content as string
    """
    # Try to read from sample file first
    try:
        sample_path = 'sample_business_transactions.csv'
        sample_df = pd.read_csv(sample_path)
        # Just take the first 10 rows to keep the template manageable
        sample_df = sample_df.head(10)
    except Exception as e:
        # Fallback to creating a simple template
        sample_df = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-15', '2023-02-01', '2023-02-15', '2023-03-01'],
            'amount': [1000.00, -250.75, 1500.00, -340.50, -125.00],
            'description': ['Monthly Revenue', 'Office Supplies', 'Service Income', 'Utility Bill', 'Internet Bill'],
            'category': ['Income', 'Expense', 'Income', 'Expense', 'Expense'],
            'account': ['Business Account', 'Business Account', 'Business Account', 'Business Account', 'Business Account']
        })
    
    # Convert to CSV string
    csv_buffer = io.StringIO()
    sample_df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()

def get_csv_download_link(df, filename="transaction_data.csv"):
    """
    Generate a download link for a DataFrame as CSV
    
    Args:
        df (pandas.DataFrame): DataFrame to convert to CSV
        filename (str): Name of the file to download
        
    Returns:
        str: HTML string with download link
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV</a>'
    return href
