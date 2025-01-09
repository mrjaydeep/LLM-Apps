import google.generativeai as genai
import yfinance as yf
import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

def get_latest_news(company):
    with DDGS() as ddgs:
        # Get both company news and industry news
        company_news = list(ddgs.text(f"{company} stock news latest", max_results=3))
        industry_news = list(ddgs.text(f"{company} industry trends latest", max_results=2))
        return company_news, industry_news

def analyze_stock(symbol, company_name):
    try:
        # Get stock data
        stock = yf.Ticker(symbol)
        info = stock.info
        
        # Get latest news
        company_news, industry_news = get_latest_news(company_name)
        
        
        prompt = f"""
        You are a stock market analyst. Analyze this data and predict potential stock movement:

        Company: {company_name} ({symbol})
        Current Price: ${info.get('currentPrice', 'N/A')}
        Previous Close: ${info.get('previousClose', 'N/A')}

        Latest Company News:
        {company_news}

        Industry Trends:
        {industry_news}

        Based on this real-time data:
        1. What's the current market sentiment?
        2. What are the key factors affecting the stock?
        3. What's the likely short-term trend?
        4. What's the likely Long-term trend?
        5. What's your choice?
        

        Provide a concise analysis and prediction.
        """
        
        response = model.generate_content(prompt)
        print(f"\nAnalysis for {company_name} ({symbol}):")
        print("=" * 50)
        print(response.text)
        
    except Exception as e:
        print(f"Error: {str(e)}")

# Example usage
analyze_stock("Gail", "tata motors")
