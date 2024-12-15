import requests
import json
from datetime import datetime
import math

def load_config():
    with open("config.json", "r") as f:
        config = json.load(f)
    
    api_key = config.get("api_key", "")
    if len(api_key) != 32:
        api_key = input("Please enter your 32-character metalpriceapi.com API key: ")
        config['api_key'] = api_key
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
    
    return config

def get_gold_price(api_key, currency):
    # Fetch rates with base USD and currencies XAU and user currency
    url = f"https://api.metalpriceapi.com/v1/latest?api_key={api_key}&base=USD&currencies=XAU,{currency}"
    response = requests.get(url)
    data = response.json()

    if 'rates' in data and 'XAU' in data['rates'] and currency in data['rates']:
        # Price of 1 USD in XAU (ounces of gold)
        usd_to_xau = data['rates']['XAU']
        # Price of 1 USD in user currency
        usd_to_currency = data['rates'][currency]
        # Calculate the price of 1 XAU in user currency
        xau_to_usd = 1 / usd_to_xau
        xau_to_currency = xau_to_usd * usd_to_currency
        gold_price = math.floor(xau_to_currency * 100) / 100  # Round down to two decimals
        timestamp = data['timestamp']
        return gold_price, timestamp
    else:
        print("Data doesn't contain expected keys. Printing full data for debugging:")
        print(data)
        raise ValueError("Invalid API response: Missing rates for XAU or user currency.")

def get_exchange_rate(api_key, from_currency, to_currency):
    url = f"https://api.metalpriceapi.com/v1/latest?api_key={api_key}&base={from_currency}&currencies={to_currency}"
    response = requests.get(url)
    data = response.json()
    
    if 'rates' in data and to_currency in data['rates']:
        exchange_rate = data['rates'][to_currency]
        return exchange_rate
    else:
        raise ValueError(f"Invalid API response: Missing rate for {to_currency}.")

if __name__ == "__main__":
    config = load_config()
    api_key = config.get("api_key", "")
    currency = config.get("currency", "USD")
    try:
        gold_price, timestamp = get_gold_price(api_key, currency)
        readable_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        print(f"Current Price of Gold per Troy Ounce at {readable_date} in {currency}: {gold_price:.2f}")
    except Exception as e:
        print(f"Error fetching gold price: {e}")
