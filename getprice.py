import requests
from datetime import datetime
import math

def get_gold_price(api_key):
    url = f"https://api.metalpriceapi.com/v1/latest?api_key={api_key}&base=GBP&currencies=XAU"
    response = requests.get(url)
    data = response.json()    
    
    if 'rates' in data and 'GBPXAU' in data['rates']:
        gold_price = data['rates']['GBPXAU']
        gold_price = math.floor(gold_price * 100) / 100  # Round down to two decimal points
        timestamp = data['timestamp']
        return gold_price, timestamp
    else:
        print("Data doesn't contain expected keys. Printing full data for debugging:")
        print(data)
        raise ValueError("Invalid API response: 'rates' key not found or 'GBPXAU' not in 'rates' is API key present?")
        

if __name__ == "__main__":
    api_key = "7fea29cb34d10e4331d7667001446fc9"
    try:
        gold_price, timestamp = get_gold_price(api_key)
        readable_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        print(f"Current Price of Gold per Troy Ounce at {readable_date} in GBP: {gold_price:.2f}")
    except Exception as e:
        print(f"Error fetching gold price: {e}")