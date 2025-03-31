import json
import re
import pandas as pd

# This version doesn't rely on OpenAI API and directly analyzes financial dataset

def financial_chat(prompt, transaction_summary=None, chat_history=None):
    """
    Generate a response based on the user's financial data.
    
    Args:
        prompt (str): User's input question or query
        transaction_summary (dict, optional): Summary of transaction data
        chat_history (list, optional): Previous chat history
    
    Returns:
        str: Data-driven response
    """
    # Convert prompt to lowercase for easier pattern matching
    prompt = prompt.lower()
    
    # Handle case where no data is uploaded
    if not transaction_summary:
        return "I need financial data to answer your question. Please upload your transaction data through the Data Import tab first, or use one of our sample datasets."
    
    # ---- Data-driven responses based on the transaction_summary ----
    
    # Extract common financial metrics from transaction_summary
    total_income = transaction_summary.get("income_total", 0)
    total_expense = transaction_summary.get("expense_total", 0)
    net_income = total_income - total_expense
    income_categories = transaction_summary.get("income_categories", {})
    expense_categories = transaction_summary.get("expense_categories", {})
    assets = transaction_summary.get("assets", {})
    liabilities = transaction_summary.get("liabilities", {})
    time_periods = transaction_summary.get("time_periods", [])
    
    # Top income/expense categories
    top_income_categories = sorted(income_categories.items(), key=lambda x: x[1], reverse=True)
    top_expense_categories = sorted(expense_categories.items(), key=lambda x: x[1], reverse=True)
    
    # Check for income related questions
    if any(word in prompt for word in ["income", "revenue", "earnings", "sales", "money coming in"]):
        response = f"Based on your data, your total income is ${total_income:,.2f}.\n\n"
        
        if top_income_categories:
            response += "Your income sources are:\n"
            for category, amount in top_income_categories:
                percentage = (amount / total_income * 100) if total_income > 0 else 0
                response += f"- {category}: ${amount:,.2f} ({percentage:.1f}% of total)\n"
        
        if "trend" in prompt or "over time" in prompt:
            response += "\nFor income trends over time, please check the Visualizations tab."
            
        return response
    
    # Check for expense related questions
    if any(word in prompt for word in ["expense", "cost", "spending", "payments", "money going out"]):
        response = f"Based on your data, your total expenses are ${total_expense:,.2f}.\n\n"
        
        if top_expense_categories:
            response += "Your main expense categories are:\n"
            for category, amount in top_expense_categories:
                percentage = (amount / total_expense * 100) if total_expense > 0 else 0
                response += f"- {category}: ${amount:,.2f} ({percentage:.1f}% of total)\n"
        
        if "trend" in prompt or "over time" in prompt:
            response += "\nFor expense trends over time, please check the Visualizations tab."
            
        return response
    
    # Check for profit related questions
    if any(word in prompt for word in ["profit", "net income", "bottom line", "earnings", "profitability"]):
        profit_margin = (net_income / total_income * 100) if total_income > 0 else 0
        
        if net_income >= 0:
            response = f"Your net income is ${net_income:,.2f}, with a profit margin of {profit_margin:.1f}%.\n\n"
            if profit_margin > 15:
                response += "This is a healthy profit margin, indicating good financial management."
            elif profit_margin > 5:
                response += "This is an average profit margin. There might be room for improvement."
            else:
                response += "This profit margin is on the lower side. Consider ways to increase revenue or reduce costs."
        else:
            response = f"You have a net loss of ${abs(net_income):,.2f}.\n\n"
            response += "Your expenses exceed your income. Consider strategies to reduce costs or increase revenue."
        
        return response
    
    # Check for balance sheet related questions
    if any(word in prompt for word in ["assets", "liabilities", "equity", "own", "owe", "balance sheet"]):
        total_assets = sum(assets.values())
        total_liabilities = sum(liabilities.values())
        equity = total_assets - total_liabilities
        
        response = f"Based on your financial data:\n\n"
        response += f"Total Assets: ${total_assets:,.2f}\n"
        response += f"Total Liabilities: ${total_liabilities:,.2f}\n"
        response += f"Equity: ${equity:,.2f}\n\n"
        
        # Add asset breakdown
        if assets:
            response += "Asset breakdown:\n"
            for asset_name, asset_value in assets.items():
                percentage = (asset_value / total_assets * 100) if total_assets > 0 else 0
                response += f"- {asset_name}: ${asset_value:,.2f} ({percentage:.1f}%)\n"
        
        # Add liability breakdown
        if liabilities and "liabilities" in prompt:
            response += "\nLiability breakdown:\n"
            for liability_name, liability_value in liabilities.items():
                percentage = (liability_value / total_liabilities * 100) if total_liabilities > 0 else 0
                response += f"- {liability_name}: ${liability_value:,.2f} ({percentage:.1f}%)\n"
        
        return response
    
    # Check for cash flow related questions
    if any(word in prompt for word in ["cash flow", "liquidity", "cash position"]):
        response = f"Based on your transaction data:\n\n"
        response += f"Net Cash Flow: ${net_income:,.2f}\n"
        
        if net_income > 0:
            response += "You have positive cash flow, which is good for your financial health."
        else:
            response += "You have negative cash flow. This means you're spending more than you're bringing in, which may lead to liquidity issues if continued."
        
        return response
    
    # Check for category specific questions
    category_pattern = re.compile(r"(how much|what is|tell me about|show me) .* (spent on|earned from|paid for|received for|paid to|received from) (\w+)")
    match = category_pattern.search(prompt)
    if match:
        category_keyword = match.group(3).lower()
        
        # Try to find matching income category
        for category in income_categories:
            if category_keyword in category.lower():
                amount = income_categories[category]
                percentage = (amount / total_income * 100) if total_income > 0 else 0
                return f"For {category}, you earned ${amount:,.2f}, which is {percentage:.1f}% of your total income."
        
        # Try to find matching expense category
        for category in expense_categories:
            if category_keyword in category.lower():
                amount = expense_categories[category]
                percentage = (amount / total_expense * 100) if total_expense > 0 else 0
                return f"For {category}, you spent ${amount:,.2f}, which is {percentage:.1f}% of your total expenses."
        
        return f"I couldn't find information about '{match.group(3)}' in your financial data. Please check your category names or try a different query."
    
    # Check for financial health questions
    if any(phrase in prompt for phrase in ["financial health", "how am i doing", "performance", "standing", "financial situation"]):
        # Calculate some basic financial health indicators
        profit_margin = (net_income / total_income * 100) if total_income > 0 else 0
        total_assets = sum(assets.values())
        total_liabilities = sum(liabilities.values())
        debt_to_equity = (total_liabilities / (total_assets - total_liabilities)) if (total_assets - total_liabilities) > 0 else float('inf')
        
        response = "Financial Health Summary:\n\n"
        
        # Profitability assessment
        response += "Profitability: "
        if profit_margin > 15:
            response += "Strong - Your profit margin of {:.1f}% is excellent\n".format(profit_margin)
        elif profit_margin > 5:
            response += "Good - Your profit margin of {:.1f}% is solid\n".format(profit_margin)
        elif profit_margin > 0:
            response += "Fair - Your profit margin of {:.1f}% is positive but could be improved\n".format(profit_margin)
        else:
            response += "Poor - You're operating at a loss\n"
        
        # Liquidity assessment
        response += "Liquidity: "
        if net_income > 0:
            response += "Positive cash flow indicates good liquidity\n"
        else:
            response += "Negative cash flow indicates potential liquidity concerns\n"
        
        # Solvency assessment
        response += "Solvency: "
        if debt_to_equity < 1:
            response += "Strong - Your debt-to-equity ratio is healthy at {:.2f}\n".format(debt_to_equity)
        elif debt_to_equity < 2:
            response += "Moderate - Your debt-to-equity ratio of {:.2f} is acceptable\n".format(debt_to_equity)
        elif debt_to_equity != float('inf'):
            response += "Weak - Your debt-to-equity ratio of {:.2f} is high\n".format(debt_to_equity)
        else:
            response += "N/A - Unable to calculate debt-to-equity ratio\n"
        
        return response
    
    # Check for time period questions (like "How was January?")
    # This assumes time_periods contains data summarized by time periods
    if time_periods:
        month_pattern = re.compile(r"(how was|what about|show me|tell me about) (january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)")
        match = month_pattern.search(prompt)
        if match:
            month_name = match.group(2).lower()
            month_map = {
                "january": "01", "jan": "01", "february": "02", "feb": "02", "march": "03", "mar": "03",
                "april": "04", "apr": "04", "may": "05", "june": "06", "jun": "06", "july": "07", "jul": "07",
                "august": "08", "aug": "08", "september": "09", "sep": "09", "october": "10", "oct": "10",
                "november": "11", "nov": "11", "december": "12", "dec": "12"
            }
            
            month_code = month_map.get(month_name)
            if month_code:
                # Find the period in time_periods that matches the month
                for period in time_periods:
                    if month_code in period.get("period", ""):
                        period_income = period.get("income", 0)
                        period_expense = period.get("expense", 0)
                        period_net = period_income - period_expense
                        
                        month_fullname = {"01": "January", "02": "February", "03": "March", "04": "April", 
                                         "05": "May", "06": "June", "07": "July", "08": "August", 
                                         "09": "September", "10": "October", "11": "November", "12": "December"}
                        
                        response = f"Financial summary for {month_fullname.get(month_code, month_name.capitalize())}:\n\n"
                        response += f"Income: ${period_income:,.2f}\n"
                        response += f"Expenses: ${period_expense:,.2f}\n"
                        response += f"Net Result: ${period_net:,.2f}"
                        
                        return response
                        
                return f"I couldn't find data specifically for {month_name.capitalize()} in your transaction history."
    
    # If no specific pattern matched but we have financial data, give a general summary
    return f"""Based on your financial data:

Total Income: ${total_income:,.2f}
Total Expenses: ${total_expense:,.2f}
Net Income: ${net_income:,.2f}
Profit Margin: {(net_income/total_income*100) if total_income > 0 else 0:.1f}%

To get more specific insights, try asking about:
- Income or expense categories
- Profit margins and financial health
- Balance sheet information (assets, liabilities)
- Trends over specific time periods
"""

def analyze_financial_data(data_summary):
    """
    Analyze financial data and generate insights.
    
    Args:
        data_summary (dict): Summary of financial data
    
    Returns:
        dict: Financial insights
    """
    try:
        # Calculate some basic metrics
        total_income = data_summary.get("income_total", 0)
        total_expenses = data_summary.get("expense_total", 0)
        net_income = total_income - total_expenses
        
        # Extract top income and expense categories
        income_categories = data_summary.get("income_categories", {})
        expense_categories = data_summary.get("expense_categories", {})
        
        top_income = sorted(income_categories.items(), key=lambda x: x[1], reverse=True)[:3]
        top_expenses = sorted(expense_categories.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Calculate profit margin
        profit_margin = (net_income / total_income * 100) if total_income > 0 else 0
        
        # Generate insights
        key_insights = [
            f"Your net income for the period is ${net_income:,.2f}",
            f"Overall profit margin is {profit_margin:.1f}%",
            f"Your top income source is {top_income[0][0] if top_income else 'N/A'}"
        ]
        
        trends = [
            "Analysis of monthly trends would require time-series data",
            "Consider tracking your expenses over time to identify seasonal patterns",
            "Regular income sources provide stability to your financial situation"
        ]
        
        recommendations = [
            f"Focus on growing your top income category: {top_income[0][0] if top_income else 'N/A'}",
            f"Review your highest expense category: {top_expenses[0][0] if top_expenses else 'N/A'} for potential savings",
            "Consider diversifying income sources for greater financial stability"
        ]
        
        risks = [
            "Concentration risk if too dependent on a single income source",
            "Cash flow constraints if expenses continue to grow faster than income",
            "Inadequate emergency fund may pose liquidity risks"
        ]
        
        return {
            "key_insights": key_insights,
            "trends": trends,
            "recommendations": recommendations,
            "risks": risks
        }
    except Exception as e:
        return {"error": f"Failed to analyze financial data: {str(e)}"}

def generate_report_content(report_type, data_summary):
    """
    Generate content for financial reports.
    
    Args:
        report_type (str): Type of report to generate (income_statement, balance_sheet, cash_flow)
        data_summary (dict): Summary of financial data
    
    Returns:
        dict: Report content with narrative analysis
    """
    report_types = {
        "income_statement", "balance_sheet", "cash_flow", "financial_summary"
    }
    
    if report_type not in report_types:
        return {"error": f"Invalid report type: {report_type}"}
    
    try:
        # Basic calculations
        total_income = data_summary.get("income_total", 0)
        total_expenses = data_summary.get("expense_total", 0)
        net_income = total_income - total_expenses
        
        # Extract categories
        income_categories = data_summary.get("income_categories", {})
        expense_categories = data_summary.get("expense_categories", {})
        assets = data_summary.get("assets", {})
        liabilities = data_summary.get("liabilities", {})
        
        # Format data based on report type
        if report_type == "income_statement":
            return {
                "title": "Income Statement Analysis",
                "summary": f"This income statement shows a total revenue of ${total_income:,.2f} and expenses of ${total_expenses:,.2f}, resulting in a net income of ${net_income:,.2f}.",
                "sections": [
                    {
                        "heading": "Revenue Breakdown",
                        "content": "Your primary sources of revenue are from the following categories: " + 
                                  ", ".join([f"{cat} (${amt:,.2f})" for cat, amt in income_categories.items()][:3])
                    },
                    {
                        "heading": "Expense Analysis",
                        "content": "Your major expenses are in these categories: " +
                                  ", ".join([f"{cat} (${amt:,.2f})" for cat, amt in expense_categories.items()][:3])
                    },
                    {
                        "heading": "Profitability Assessment",
                        "content": f"Your overall profit margin is {(net_income/total_income*100) if total_income > 0 else 0:.1f}%. " +
                                  ("This is a healthy margin indicating good financial management." if (net_income/total_income*100) > 15 else "Consider strategies to increase revenue or reduce expenses to improve this margin.")
                    }
                ]
            }
        
        elif report_type == "balance_sheet":
            total_assets = sum(assets.values())
            total_liabilities = sum(liabilities.values())
            equity = total_assets - total_liabilities
            
            return {
                "title": "Balance Sheet Analysis",
                "summary": f"This balance sheet shows total assets of ${total_assets:,.2f}, liabilities of ${total_liabilities:,.2f}, and equity of ${equity:,.2f}.",
                "sections": [
                    {
                        "heading": "Asset Composition",
                        "content": "Your assets are primarily composed of: " +
                                  ", ".join([f"{cat} (${amt:,.2f})" for cat, amt in assets.items()][:3])
                    },
                    {
                        "heading": "Liability Structure",
                        "content": "Your liabilities include: " +
                                  ", ".join([f"{cat} (${amt:,.2f})" for cat, amt in liabilities.items()][:3])
                    },
                    {
                        "heading": "Equity Analysis",
                        "content": f"Your equity position of ${equity:,.2f} represents " +
                                  f"{(equity/total_assets*100) if total_assets > 0 else 0:.1f}% of your total assets."
                    },
                    {
                        "heading": "Financial Health Indicators",
                        "content": f"Debt-to-equity ratio: {(total_liabilities/equity) if equity > 0 else 0:.2f}. " +
                                  f"Current ratio: {data_summary.get('current_ratio', 'N/A')}."
                    }
                ]
            }
        
        elif report_type == "cash_flow":
            return {
                "title": "Cash Flow Statement Analysis",
                "summary": f"This cash flow statement shows the movement of cash in and out of your finances over the reporting period.",
                "sections": [
                    {
                        "heading": "Operating Cash Flow",
                        "content": f"Net operating cash flow: ${net_income:,.2f}. This represents the cash generated from your primary activities."
                    },
                    {
                        "heading": "Investing Activities",
                        "content": "Cash flow from investing activities includes asset purchases and sales. Detailed breakdown requires transaction-level data."
                    },
                    {
                        "heading": "Financing Activities",
                        "content": "Cash flow from financing activities includes debt payments and equity transactions. Detailed breakdown requires transaction-level data."
                    },
                    {
                        "heading": "Liquidity Assessment",
                        "content": f"Based on your cash flow, your liquidity appears to be " +
                                  ("strong." if net_income > 0 else "an area that needs attention.")
                    }
                ]
            }
        
        elif report_type == "financial_summary":
            total_assets = sum(assets.values())
            total_liabilities = sum(liabilities.values())
            equity = total_assets - total_liabilities
            
            return {
                "title": "Comprehensive Financial Summary",
                "summary": f"This report provides an overview of your financial position and performance.",
                "sections": [
                    {
                        "heading": "Key Financial Indicators",
                        "content": f"Net Income: ${net_income:,.2f}\n" +
                                  f"Total Assets: ${total_assets:,.2f}\n" +
                                  f"Total Liabilities: ${total_liabilities:,.2f}\n" +
                                  f"Equity: ${equity:,.2f}\n" +
                                  f"Profit Margin: {(net_income/total_income*100) if total_income > 0 else 0:.1f}%"
                    },
                    {
                        "heading": "Financial Health Assessment",
                        "content": "Based on the provided financial data, your overall financial health is " +
                                  ("good, with positive net income and reasonable debt levels." if net_income > 0 and total_liabilities < total_assets else 
                                   "showing some areas for improvement. Consider focusing on increasing income or reducing expenses.")
                    },
                    {
                        "heading": "Executive Insights",
                        "content": "Key areas to focus on include:\n" +
                                  "1. Managing major expense categories\n" +
                                  "2. Growing your strongest income sources\n" +
                                  "3. Maintaining adequate liquidity\n" +
                                  "4. Planning for future growth and contingencies"
                    }
                ]
            }
    
    except Exception as e:
        return {"error": f"Failed to generate report content: {str(e)}"}
