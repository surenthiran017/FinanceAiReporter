import os
import json
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Initialize Gemini API
def init_gemini():
    """
    Initialize the Gemini API with the API key from environment variables
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)
    return genai

# Configure Gemini model settings
def get_gemini_config():
    """
    Configure the Gemini model with appropriate settings for financial analysis
    """
    return {
        "temperature": 0.2,  # Lower temperature for more deterministic outputs
        "max_output_tokens": 2048,
        "safety_settings": [
            {
                "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
            {
                "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
            {
                "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
            {
                "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
        ],
    }

def financial_chat_with_gemini(prompt, transaction_summary=None, chat_history=None):
    """
    Generate a data-driven financial analysis response using Gemini API.
    
    Args:
        prompt (str): User's input question or query
        transaction_summary (dict, optional): Summary of transaction data
        chat_history (list, optional): Previous chat history
    
    Returns:
        str: Data-driven financial analysis from Gemini
    """
    try:
        # Initialize Gemini
        genai_client = init_gemini()
        
        # Check if data is available
        if not transaction_summary:
            return "I need your financial data to answer this question. Please upload your transaction data through the Data Import tab first, or use one of our sample datasets."
        
        # Get model
        model = genai_client.GenerativeModel(
            model_name="gemini-1.5-flash",
            **get_gemini_config()
        )
        
        # Extract key financial metrics to enhance prompt
        total_income = transaction_summary.get("income_total", 0)
        total_expense = transaction_summary.get("expense_total", 0)
        net_income = total_income - total_expense
        profit_margin = (net_income / total_income * 100) if total_income > 0 else 0
        
        # Prepare detailed financial context
        financial_data = _prepare_analysis_context(transaction_summary)
        
        # Create a specialized system prompt with detailed instructions
        system_prompt = f"""
You are a financial analyst assistant analyzing real financial data. Your primary role is to analyze the user's financial data and provide specific data-driven insights and answers.

IMPORTANT GUIDELINES:
1. ONLY analyze the provided financial dataset. DO NOT fabricate data or make generic recommendations.
2. All responses MUST directly reference numbers from the provided financial data.
3. Always include specific figures, percentages, and calculations in your responses.
4. Format currency values with dollar signs and commas (e.g., $1,234.56).
5. When discussing trends, cite specific periods and percentage changes.
6. If asked about future predictions, base them ONLY on historical patterns in the provided data.
7. If data is insufficient to answer a specific question, clearly state this limitation.
8. If the question isn't about the financial data, gently redirect to financial analysis topics.
9. Always offer 1-2 actionable insights based on the data.

DATA SUMMARY:
Total Income: ${total_income:,.2f}
Total Expenses: ${total_expense:,.2f}
Net Income: ${net_income:,.2f}
Profit Margin: {profit_margin:.1f}%

DETAILED FINANCIAL DATA:
{financial_data}

USER QUESTION: {prompt}

Your analysis (be concise, specific, and data-driven):
"""
        
        # Get response with complete context
        response = model.generate_content(system_prompt)
        return response.text
        
    except Exception as e:
        # Log error for debugging
        print(f"Gemini API error: {str(e)}")
        
        # Fallback to rule-based response if Gemini API fails
        # Import here to avoid circular imports
        from utils.openai_utils import financial_chat
        return financial_chat(prompt, transaction_summary, chat_history)

def _prepare_analysis_context(transaction_summary):
    """
    Prepare a comprehensive analysis context for the financial data
    to enable more detailed and accurate responses.
    """
    
    # Basic financial metrics
    income_categories = transaction_summary.get("income_categories", {})
    expense_categories = transaction_summary.get("expense_categories", {})
    assets = transaction_summary.get("assets", {})
    liabilities = transaction_summary.get("liabilities", {})
    time_periods = transaction_summary.get("time_periods", [])
    
    # Prepare detailed context sections
    context_parts = []
    
    # Income breakdown
    context_parts.append("INCOME BREAKDOWN:")
    for category, amount in sorted(income_categories.items(), key=lambda x: x[1], reverse=True):
        percentage = (amount / transaction_summary.get("income_total", 1)) * 100
        context_parts.append(f"- {category}: ${amount:,.2f} ({percentage:.1f}%)")
    
    # Expense breakdown
    context_parts.append("\nEXPENSE BREAKDOWN:")
    for category, amount in sorted(expense_categories.items(), key=lambda x: x[1], reverse=True):
        percentage = (amount / transaction_summary.get("expense_total", 1)) * 100
        context_parts.append(f"- {category}: ${amount:,.2f} ({percentage:.1f}%)")
    
    # Assets breakdown
    if assets:
        context_parts.append("\nASSETS:")
        total_assets = sum(assets.values())
        for asset, value in sorted(assets.items(), key=lambda x: x[1], reverse=True):
            percentage = (value / total_assets) * 100
            context_parts.append(f"- {asset}: ${value:,.2f} ({percentage:.1f}%)")
    
    # Liabilities breakdown
    if liabilities:
        context_parts.append("\nLIABILITIES:")
        total_liabilities = sum(liabilities.values())
        for liability, value in sorted(liabilities.items(), key=lambda x: x[1], reverse=True):
            percentage = (value / total_liabilities) * 100
            context_parts.append(f"- {liability}: ${value:,.2f} ({percentage:.1f}%)")
    
    # Time period analysis if available
    if time_periods:
        context_parts.append("\nTIME PERIOD ANALYSIS:")
        for period in time_periods:
            period_name = period.get("period", "Unknown")
            period_income = period.get("income", 0)
            period_expense = period.get("expense", 0)
            period_net = period_income - period_expense
            profit_margin = (period_net / period_income * 100) if period_income > 0 else 0
            
            context_parts.append(f"- {period_name}: Income: ${period_income:,.2f}, Expenses: ${period_expense:,.2f}, Net: ${period_net:,.2f}, Margin: {profit_margin:.1f}%")
    
    # Financial ratios if available
    if "financial_ratios" in transaction_summary:
        context_parts.append("\nFINANCIAL RATIOS:")
        for ratio_name, ratio_value in transaction_summary["financial_ratios"].items():
            context_parts.append(f"- {ratio_name}: {ratio_value:.4f}")
    
    # Join all parts with line breaks
    return "\n".join(context_parts)

def _create_system_prompt(transaction_summary):
    """Create a system prompt with instructions for Gemini"""
    return """You are a financial analyst assistant. Your task is to answer questions about the user's financial data.
    
Rules:
1. Only provide information based on the financial data provided to you.
2. Be precise with numbers and calculations.
3. Format currency values with dollar signs and commas (e.g., $1,234.56).
4. When discussing percentages, include % symbol and show one decimal place (e.g., 12.3%).
5. If you're unsure or the data doesn't contain information to answer a question, say so clearly.
6. Always be helpful, concise, and focused on financial insights.
7. Do not make assumptions about financial data that isn't provided.
8. Present data in an easy-to-read format, using bullet points and line breaks when appropriate.
"""

def _format_financial_data(transaction_summary):
    """Format the financial data summary for Gemini's context"""
    # Extract key financial metrics
    total_income = transaction_summary.get("income_total", 0)
    total_expense = transaction_summary.get("expense_total", 0)
    net_income = total_income - total_expense
    income_categories = transaction_summary.get("income_categories", {})
    expense_categories = transaction_summary.get("expense_categories", {})
    assets = transaction_summary.get("assets", {})
    liabilities = transaction_summary.get("liabilities", {})
    
    # Create a formatted string representation
    data_str = f"""
FINANCIAL SUMMARY:
------------------
Total Income: ${total_income:,.2f}
Total Expenses: ${total_expense:,.2f}
Net Income: ${net_income:,.2f}
Profit Margin: {(net_income/total_income*100) if total_income > 0 else 0:.1f}%

INCOME CATEGORIES:
-----------------
{json.dumps(income_categories, indent=2)}

EXPENSE CATEGORIES:
------------------
{json.dumps(expense_categories, indent=2)}

ASSETS:
------
{json.dumps(assets, indent=2)}

LIABILITIES:
-----------
{json.dumps(liabilities, indent=2)}
"""
    
    return data_str

def analyze_financial_data_with_gemini(data_summary):
    """
    Analyze financial data and generate insights using Gemini.
    
    Args:
        data_summary (dict): Summary of financial data
    
    Returns:
        dict: Financial insights
    """
    try:
        # Initialize Gemini
        genai_client = init_gemini()
        
        # Format the financial data for analysis
        financial_data = _format_financial_data(data_summary)
        
        # Create prompt for analysis
        analysis_prompt = f"""
Financial Data:
{financial_data}

Analyze this financial data and provide:
1. 3-5 key insights
2. 2-3 observable trends
3. 3 actionable recommendations
4. 2-3 potential financial risks

Format the response as JSON with these exact keys: key_insights, trends, recommendations, risks.
Each key should contain an array of strings.
"""

        # Get model
        model = genai_client.GenerativeModel(
            model_name="gemini-1.5-flash",
            **get_gemini_config()
        )
        
        # Get response
        response = model.generate_content(analysis_prompt)
        
        # Parse the response into a dictionary
        try:
            # The response might be in markdown JSON format, so try to extract it
            content = response.text
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].strip()
            else:
                json_str = content
                
            return json.loads(json_str)
        except json.JSONDecodeError:
            # If parsing as JSON fails, return a formatted dict from the text
            return {
                "key_insights": [line.strip() for line in response.text.split("\n") if line.strip().startswith("- ")],
                "trends": [],
                "recommendations": [],
                "risks": []
            }
            
    except Exception as e:
        # Fall back to rule-based analysis
        from utils.openai_utils import analyze_financial_data
        return analyze_financial_data(data_summary)

def generate_report_content_with_gemini(report_type, data_summary):
    """
    Generate content for financial reports using Gemini.
    
    Args:
        report_type (str): Type of report to generate (income_statement, balance_sheet, cash_flow)
        data_summary (dict): Summary of financial data
    
    Returns:
        dict: Report content with narrative analysis
    """
    try:
        # Initialize Gemini
        genai_client = init_gemini()
        
        # Format the financial data for report generation
        financial_data = _format_financial_data(data_summary)
        
        # Create prompt based on report type
        if report_type == "income_statement":
            report_prompt = f"""
Financial Data:
{financial_data}

Generate a comprehensive income statement analysis based on this financial data.
Focus on revenue sources, major expense categories, and profitability.
Include a narrative analysis explaining the key factors affecting the company's performance.

Format the response as JSON with these keys:
1. title (string)
2. summary (string) - A brief executive summary of the income statement
3. analysis (array of strings) - Each string should be a paragraph analyzing different aspects
4. key_metrics (object) - Key financial metrics related to the income statement
5. recommendations (array of strings) - Actionable insights based on the income statement
"""
        elif report_type == "balance_sheet":
            report_prompt = f"""
Financial Data:
{financial_data}

Generate a comprehensive balance sheet analysis based on this financial data.
Focus on assets, liabilities, and equity positions.
Include a narrative analysis explaining the key factors affecting the company's financial position.

Format the response as JSON with these keys:
1. title (string)
2. summary (string) - A brief executive summary of the balance sheet
3. analysis (array of strings) - Each string should be a paragraph analyzing different aspects
4. key_metrics (object) - Key financial metrics related to the balance sheet
5. recommendations (array of strings) - Actionable insights based on the balance sheet
"""
        elif report_type == "cash_flow":
            report_prompt = f"""
Financial Data:
{financial_data}

Generate a comprehensive cash flow analysis based on this financial data.
Focus on operating cash flow, investing activities, and financing activities.
Include a narrative analysis explaining the key factors affecting the company's cash position.

Format the response as JSON with these keys:
1. title (string)
2. summary (string) - A brief executive summary of the cash flow
3. analysis (array of strings) - Each string should be a paragraph analyzing different aspects
4. key_metrics (object) - Key financial metrics related to cash flow
5. recommendations (array of strings) - Actionable insights based on the cash flow
"""
        else:  # financial_summary
            report_prompt = f"""
Financial Data:
{financial_data}

Generate a comprehensive financial summary based on this data.
Provide an overview of income, expenses, assets, liabilities, and financial health.
Include a narrative analysis explaining the key factors affecting the overall financial situation.

Format the response as JSON with these keys:
1. title (string)
2. summary (string) - A brief executive summary of the financial situation
3. analysis (array of strings) - Each string should be a paragraph analyzing different aspects
4. key_metrics (object) - Key financial metrics across all financial statements
5. recommendations (array of strings) - Actionable insights based on the financial data
"""

        # Get model
        model = genai_client.GenerativeModel(
            model_name="gemini-1.5-flash",
            **get_gemini_config()
        )
        
        # Get response
        response = model.generate_content(report_prompt)
        
        # Parse the response into a dictionary
        try:
            # The response might be in markdown JSON format, so try to extract it
            content = response.text
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].strip()
            else:
                json_str = content
                
            return json.loads(json_str)
        except (json.JSONDecodeError, IndexError) as e:
            # If parsing fails, create a simple structured response
            return {
                "title": f"{report_type.replace('_', ' ').title()} Report",
                "summary": "Financial report generated with Gemini AI",
                "analysis": [response.text],
                "key_metrics": {},
                "recommendations": []
            }
            
    except Exception as e:
        # Fall back to rule-based report generation
        from utils.openai_utils import generate_report_content
        return generate_report_content(report_type, data_summary)