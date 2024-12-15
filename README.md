# Crabs Gold Tracker

![Image](https://github.com/user-attachments/assets/bd88dafe-4ab7-4e09-abd0-3feaed3aa122) 

This simple TUI (Text User Interface) enables you to keep track of your current gold investments. I wanted this to be a privacy-conscious investment tracker that has no frills; it literally tells you your P/L, the current price of gold, and the value of your investments.

The reason I wanted to make this was that many open source/self-hosted solutions don't allow you to track the price of gold when it comes to physical gold in your possession. They also don't let you track the value of specific investments like the Capital Gains Tax-free coins in the UK.

This is still very much a work in progress, and I clearly need to work on adding other metals/coins as well as probably other API providers.

## Setup

Just download the three Python files, and in the console type:

```bash
# python3 tui.py
```
This will generate two files, config.json and inventory.json
the inventory will contain your purchases.
The config.json file just contains your metalpriceapi.com API key which you get prompted to enter upon first run.
From there, just enter in your gold purchases following the on screen prompts.
