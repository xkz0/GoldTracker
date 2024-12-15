# Crabs Gold Tracker

![Image](https://github.com/user-attachments/assets/bd88dafe-4ab7-4e09-abd0-3feaed3aa122) 

This simple TUI (Text User Interface) enables you to keep track of your current gold investments. I wanted this to be a privacy-conscious investment tracker that has no frills; it literally tells you your P/L, the current price of gold, and the value of your investments.

The reason I wanted to make this was that many open source/self-hosted solutions don't allow you to track the price of gold when it comes to physical gold in your possession. They also don't let you track the value of specific investments like the Capital Gains Tax-free coins in the UK. (Gold Sovereigns and Gold Britannias)

This is still very much a work in progress, and I clearly need to work on adding other metals/coins as well as probably other API providers.

The way this works is it polls metalpriceapi.com for the days price of gold with:
```
(https://api.metalpriceapi.com/v1/latest?api_key={api_key}&base=USD&currencies=XAU,{currency})
```
I chose MetalPriceAPI because youi get 100 free API requests per month, and we're only using one per day, even if you close and re-open the application, it stores the price data for that day (API only updates once per day on free tier).
This is great for metal prices but not for specific coins etc.
So I scrape the Royal Mints website for their prices on the Gold Britannias 1oz, 1/2oz, and 1/4oz.

## Setup

Just download the three Python files and "requirements.txt" , then run:
```bash
pip install -r requirements.txt
```
Then in the console type:
```bash
python3 tui.py
```
This will generate two files, config.json and inventory.json
the inventory will contain your purchases.
The config.json file just contains your metalpriceapi.com API key which you get prompted to enter upon first run, and your currency.
From there, just enter in your gold purchases following the on screen prompts.


## To Do
```
1. Implement other currencies - Done
2. Implement other metals
3. Implement other Coins, or at least the facility to easily do this yourself - Added gold sovereigns
```

## Disclaimer
I am not claiming that this information is accurate or should be used to make financial decisions off of. Always do your own due diligence.
