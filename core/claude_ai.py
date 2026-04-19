import json
from anthropic import Anthropic
import os

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def analyze_receipt(ocr_text):
    """
    Send OCR text to Claude API for expense analysis.
    Returns structured JSON with merchant, amount, date, category, items.
    """
    prompt = """You are an expense analyzer. Given receipt OCR text, extract and return
ONLY a valid JSON object:
{
  "merchant": "store name",
  "amount": 0.0,
  "date": "YYYY-MM-DD or null",
  "category": "one of [Food/Transport/Shopping/Health/Entertainment/Utilities/Other]",
  "items": "comma-separated main items purchased"
}
No explanation, no markdown, just JSON.

Receipt OCR text:
"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": prompt + ocr_text
                }
            ]
        )

        response_text = message.content[0].text.strip()

        # Try to parse JSON
        try:
            result = json.loads(response_text)
            # Validate required fields
            if not all(k in result for k in ['merchant', 'amount', 'category']):
                return get_fallback_expense()
            return result
        except json.JSONDecodeError:
            # Try to extract JSON from response if wrapped in markdown
            if '```json' in response_text:
                json_str = response_text.split('```json')[1].split('```')[0]
                return json.loads(json_str)
            elif '```' in response_text:
                json_str = response_text.split('```')[1].split('```')[0]
                return json.loads(json_str)
            return get_fallback_expense()

    except Exception as e:
        print(f"Claude API error: {e}")
        return get_fallback_expense()

def get_fallback_expense():
    """Return a fallback expense object when API fails."""
    return {
        "merchant": "Unknown",
        "amount": 0.0,
        "date": None,
        "category": "Other",
        "items": ""
    }

def generate_financial_advice(spending_summary):
    """
    Generate personalized financial advice based on spending patterns.
    Returns 4 money-saving tips.
    """
    prompt = f"""You are a friendly personal finance advisor for a college student in India.
Based on this spending summary, provide exactly 4 practical money-saving tips
as a numbered list. Be specific, use Indian context (UPI, local stores, etc).

Spending data: {json.dumps(spending_summary)}

Format your response as:
1. [Tip 1]
2. [Tip 2]
3. [Tip 3]
4. [Tip 4]"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return message.content[0].text.strip()

    except Exception as e:
        print(f"Claude API error: {e}")
        return """1. Track your daily spending using UPI transaction history
2. Use apps like CRED for cashback on bill payments
3. Buy groceries from local markets instead of supermarkets
4. Use student discounts on food delivery apps like Swiggy and Zomato"""
