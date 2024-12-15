import requests
from bs4 import BeautifulSoup
import json

def get_cgt_free_coin_price(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the div with the data-product-settings attribute
    product_div = soup.find('div', {'data-module': 'product'})
    if product_div:
        product_settings = product_div['data-product-settings']
        product_data = json.loads(product_settings)
        
        # Extract the price for quantity 1
        for pricing in product_data['pricing']:
            if pricing['Quantity'] == 1:
                price = float(pricing['PriceString'].replace('£', '').replace(',', ''))
                return price
    else:
        raise ValueError("Product data not found on the page")

if __name__ == "__main__":
    britannia_urls = {
        "1oz": "https://www.royalmint.com/invest/bullion/bullion-coins/gold-coins/britannia-2025-1oz-gold-bullion-coin/",
        "1/2oz": "https://www.royalmint.com/invest/bullion/bullion-coins/gold-coins/britannia-2024-half-oz-gold-bullion-coin-in-blister/",
        "1/4oz": "https://www.royalmint.com/invest/bullion/bullion-coins/gold-coins/britannia-2025-14oz-gold-bullion-coin-in-blister/"
    }
    
    sovereign_urls = {
        "double": "https://www.royalmint.com/invest/bullion/bullion-coins/gold-coins/the-double-sovereign-2024-gold-bullion-coin-in-blister/",
        "full": "https://www.royalmint.com/invest/bullion/bullion-coins/gold-coins/the-sovereign-2024-gold-bullion-coin-in-blister/",
        "half": "https://www.royalmint.com/invest/bullion/bullion-coins/gold-coins/the-half-sovereign-2024-gold-bullion-coin-in-blister/",
        "quarter": "https://www.royalmint.com/invest/bullion/bullion-coins/gold-coins/the-quarter-sovereign-2024-gold-bullion-coin-in-blister/"
    }
    
    # Test Britannias
    for size, url in britannia_urls.items():
        try:
            price = get_cgt_free_coin_price(url)
            print(f"Current price of {size} Britannia: £{price:.2f}")
        except Exception as e:
            print(f"Error fetching price for {size} Britannia: {e}")
    
    # Test Sovereigns
    for size, url in sovereign_urls.items():
        try:
            price = get_cgt_free_coin_price(url)
            print(f"Current price of {size} Sovereign: £{price:.2f}")
        except Exception as e:
            print(f"Error fetching price for {size} Sovereign: {e}")
