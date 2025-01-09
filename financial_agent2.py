import google.generativeai as genai
import yfinance as yf
from duckduckgo_search import DDGS
from dotenv import load_dotenv
import os
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

def get_latest_news(company):
    with DDGS() as ddgs:
        news = list(ddgs.text(f"{company} stock news latest", max_results=2))
        return news

def compare_stocks(companies):
    """
    companies: list of tuples [(symbol, name), (symbol, name), ...]
    """
    try:
        # Collect data for all companies
        data = []
        for symbol, name in companies:
            stock = yf.Ticker(symbol)
            info = stock.info
            news = get_latest_news(name)
            
            company_data = {
                'symbol': symbol,
                'name': name,
                'price': info.get('currentPrice', 'N/A'),
                'prev_close': info.get('previousClose', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'news': news
            }
            data.append(company_data)
        
        # Create comparative analysis prompt
        prompt = f"""
        You are a stock market analyst. Compare these companies and provide investment insights:

        {"=" * 40}
        """
        
        for company in data:
            prompt += f"""
            {company['name']} ({company['symbol']}):
            Current Price: ${company['price']}
            Previous Close: ${company['prev_close']}
            Market Cap: ${company['market_cap']}
            Recent News: {company['news']}
            
            """

        prompt += """
        Please provide:
        1. Comparative analysis between these companies
        2. Their relative market positions
        3. Which company appears to have the best short-term potential and why
        4. Key risks and opportunities for each
        5. Which is the best company in between them to select for long term
        6. Which company is best for the short-term potential
        
        Make sure to use the real-time data and news to support your analysis.
        """
        
        response = model.generate_content(prompt)
        print("\nComparative Analysis:")
        print("=" * 50)
        print(response.text)
        
    except Exception as e:
        print(f"Error: {str(e)}")

# Example usage
if __name__ == "__main__":
    # List of companies to compare: (symbol, company name)
    companies_to_compare = [
        ("GAIL", "GAIL"),
        ("ASHOKLEY", "Ashok Leyland Limited"),
        ("ZOMATO", "ZOMATO Limited"),
        ("TCS","Tata Consultancy Services Limited"),
    ]
    
    # Run the comparison
    compare_stocks(companies_to_compare)