import curses
import json
import math
import time
from datetime import datetime, timedelta
from getprice import get_gold_price, get_exchange_rate  # Add get_exchange_rate
from scrape import get_cgt_free_coin_price

INVENTORY_FILE = "inventory.json"
CONFIG_FILE = "config.json"

def get_user_input(stdscr, prompt):
    stdscr.clear()
    stdscr.addstr(0, 0, prompt)
    stdscr.refresh()
    curses.echo()
    user_input = stdscr.getstr(1, 0).decode('utf-8')
    curses.noecho()
    return user_input

def get_menu_choice(stdscr, menu_text, input_prompt):
    """Display a menu and get user choice without clearing screen"""
    stdscr.clear()
    for i, line in enumerate(menu_text):
        stdscr.addstr(i, 0, line)
    stdscr.addstr(len(menu_text) + 1, 0, input_prompt)
    stdscr.refresh()
    curses.echo()
    choice = stdscr.getstr(len(menu_text) + 2, 0).decode('utf-8').strip()
    curses.noecho()
    return choice

def load_inventory():
    try:
        with open(INVENTORY_FILE, 'r') as file:
            inventory = json.load(file)
            if not inventory:
                inventory = []
            # Ensure all items have the 'is_cgt_free' key
            for item in inventory:
                if 'is_cgt_free' not in item:
                    item['is_cgt_free'] = False
                # Convert date to ISO format if necessary
                try:
                    datetime.fromisoformat(item['date'])
                except ValueError:
                    item['date'] = datetime.strptime(item['date'], "%d-%m-%Y").isoformat()
    except (FileNotFoundError, json.JSONDecodeError):
        inventory = []
    return inventory

def save_inventory(inventory):
    with open(INVENTORY_FILE, 'w') as file:
        json.dump(inventory, file, indent=4)

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {"api_key": "", "currency": ""}
        save_config(config)
    return config

def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)

def display_inventory(stdscr, inventory, currency):
    stdscr.clear()
    stdscr.addstr(0, 0, "Inventory:")
    for idx, item in enumerate(inventory, start=1):
        stdscr.addstr(idx, 0, f"ID: {item['id']}, Name: {item['name']}, Price: {item['price']:.2f} {currency}, Weight: {item['weight']:.2f}g, Date: {item['date']}, Gold Price: {item['gold_price']:.2f} {currency}")
    stdscr.refresh()
    stdscr.getch()

def remove_entry(stdscr, inventory):
    stdscr.clear()
    stdscr.addstr(0, 0, "Enter the ID of the entry to remove: ")
    stdscr.refresh()
    curses.echo()
    entry_id = int(stdscr.getstr(1, 0).decode('utf-8'))
    curses.noecho()
    inventory = [item for item in inventory if item['id'] != entry_id]
    save_inventory(inventory)
    stdscr.addstr(2, 0, "Entry removed. Press any key to continue.")
    stdscr.refresh()
    stdscr.getch()
    return inventory

def change_api_key(stdscr, config):
    new_api_key = get_user_input(stdscr, "Enter the new metalpriceapi.com API key: ")
    config['api_key'] = new_api_key
    save_config(config)
    stdscr.addstr(2, 0, "API key updated. Press any key to continue.")
    stdscr.refresh()
    stdscr.getch()
    return config

def change_currency(stdscr, config, api_key, inventory):
    stdscr.clear()
    stdscr.addstr(0, 0, f"Current currency: {config.get('currency', 'USD')}")
    new_currency = get_user_input(stdscr, "Enter your new preferred currency code (e.g., USD, EUR): ").upper()
    old_currency = config.get('currency', 'USD')
    
    if new_currency == old_currency:
        stdscr.addstr(2, 0, "Currency is the same as before. No changes made. Press any key to continue.")
        stdscr.refresh()
        stdscr.getch()
        return config, inventory, None, None

    try:
        # Get exchange rate from old currency to new currency
        exchange_rate = get_exchange_rate(api_key, old_currency, new_currency)
        # Update purchase prices in the inventory
        for item in inventory:
            item['price'] = item['price'] * exchange_rate
        
        # Fetch new gold price in the new currency
        try:
            gold_price, timestamp = get_gold_price(api_key, new_currency)
            for item in inventory:
                item['gold_price'] = gold_price
                item['gold_price_timestamp'] = datetime.fromtimestamp(timestamp).isoformat()
            save_inventory(inventory)
        except Exception as e:
            stdscr.addstr(2, 0, f"Error fetching new gold price: {e}")
            stdscr.refresh()
            stdscr.getch()
            return config, inventory, None, None

        # Update the config with the new currency
        config['currency'] = new_currency
        save_config(config)
        stdscr.addstr(2, 0, f"Currency changed to {new_currency}. Prices updated. Press Enter to return to main menu.")
        stdscr.refresh()
        stdscr.getch()
        return config, inventory, gold_price, timestamp

    except Exception as e:
        stdscr.addstr(2, 0, f"Error changing currency: {e}")
        stdscr.refresh()
        stdscr.getch()
        return config, inventory, None, None

def display_header(stdscr, text_lines, color_pair):
    """Display ASCII art header with gold color"""
    for y, line in enumerate(text_lines):
        try:
            stdscr.addstr(y, 0, line, color_pair | curses.A_REVERSE)
        except curses.error:
            pass

def main(stdscr):
    config = load_config()
    # Prompt for currency if not set
    if not config.get('currency'):
        config['currency'] = get_user_input(stdscr, "Enter your preferred currency code (e.g., USD, EUR): ").upper()
        save_config(config)
    currency = config.get("currency", "USD")
    # Prompt for API key if not set or invalid
    if not config.get('api_key') or len(config['api_key']) != 32:
        config['api_key'] = get_user_input(stdscr, "Enter your 32-character metalpriceapi.com API key: ")
        save_config(config)
    api_key = config.get("api_key", "")

    inventory = load_inventory()
    purchase_id = len(inventory) + 1
    
    # Check if the stored gold price is still valid
    if inventory and 'gold_price_timestamp' in inventory[0]:
        last_update = datetime.fromisoformat(inventory[0]['gold_price_timestamp'])
        if datetime.now() < last_update + timedelta(days=1):
            gold_price = inventory[0]['gold_price']
            timestamp = last_update.timestamp()
        else:
            try:
                gold_price, timestamp = get_gold_price(api_key, currency)
                for item in inventory:
                    item['gold_price'] = gold_price
                    item['gold_price_timestamp'] = datetime.fromtimestamp(timestamp).isoformat()
                save_inventory(inventory)
            except Exception as e:
                stdscr.addstr(0, 0, f"Error fetching gold price: {e}")
                stdscr.refresh()
                stdscr.getch()
                return
    else:
        try:
            gold_price, timestamp = get_gold_price(api_key, currency)
            for item in inventory:
                item['gold_price'] = gold_price
                item['gold_price_timestamp'] = datetime.fromtimestamp(timestamp).isoformat()
            save_inventory(inventory)
        except Exception as e:
            stdscr.addstr(0, 0, f"Error fetching gold price: {e}")
            stdscr.refresh()
            stdscr.getch()
            return
    
    readable_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    # Initialize colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # Gold color
    
    ascii_art = [
        "  /$$$$$$                     /$$                        /$$$$$$            /$$       /$$       /$$$$$$$$                           /$$                          ",
        " /$$__  $$                   | $$                       /$$__  $$          | $$      | $$      |__  $$__/                          | $$                          ",
        "| $$  \\__/  /$$$$$$  /$$$$$$ | $$$$$$$   /$$$$$$$      | $$  \\__/  /$$$$$$ | $$  /$$$$$$$         | $$  /$$$$$$  /$$$$$$   /$$$$$$$| $$   /$$  /$$$$$$   /$$$$$$ ",
        "| $$       /$$__  $$|____  $$| $$__  $$ /$$_____/      | $$ /$$$$ /$$__  $$| $$ /$$__  $$         | $$ /$$__  $$|____  $$ /$$_____/| $$  /$$/ /$$__  $$ /$$__  $$",
        "| $$      | $$  \\__/ /$$$$$$$| $$  \\ $$|  $$$$$$       | $$|_  $$| $$  \\ $$| $$| $$  | $$         | $$| $$  \\__/ /$$$$$$$| $$      | $$$$$$/ | $$$$$$$$| $$  \\__/",
        "| $$    $$| $$      /$$__  $$| $$  | $$ \\____  $$      | $$  \\ $$| $$  | $$| $$| $$  | $$         | $$| $$      /$$__  $$| $$      | $$_  $$ | $$_____/| $$      ",
        "|  $$$$$$/| $$     |  $$$$$$$| $$$$$$$/ /$$$$$$$/      |  $$$$$$/|  $$$$$$/| $$|  $$$$$$$         | $$| $$     |  $$$$$$$|  $$$$$$$| $$ \\  $$|  $$$$$$$| $$      ",
        " \\______/ |__/      \\_______/|_______/ |_______/        \\______/  \\______/ |__/ \\_______/         |__/|__/      \\_______/ \\_______/|__/  \\__/ \\_______/|__/      "
    ]
    
    while True:
        stdscr.clear()
        
        # Display ASCII art header
        display_header(stdscr, ascii_art, curses.color_pair(8))
        
        # Display status information
        start_y = len(ascii_art) + 2  # Space after header
        try:
            stdscr.addstr(start_y, 0, f"Current Price of Gold per Troy Ounce at {readable_date} in {currency}: {gold_price:.2f}", curses.color_pair(8))
            total_weight = sum(item['weight'] for item in inventory)
            total_weight_oz = total_weight / 31.1035
            total_value = sum((item['weight'] / 31.1035) * gold_price for item in inventory)
            total_purchase_price = sum(item['price'] for item in inventory)
            profit_loss = total_value - total_purchase_price
            
            cgt_free_value = sum((item['weight'] / 31.1035) * gold_price for item in inventory if item['is_cgt_free'])
            non_cgt_free_value = total_value - cgt_free_value
            
            stdscr.addstr(start_y + 1, 0, f"Total weight of gold: {total_weight:.2f} grams ({total_weight_oz:.2f} troy ounces)", curses.color_pair(1))
            stdscr.addstr(start_y + 2, 0, f"Total value of gold holdings: {total_value:.2f} {currency}", curses.color_pair(2))
            stdscr.addstr(start_y + 3, 0, f"Total purchase price: {total_purchase_price:.2f} {currency}", curses.color_pair(3))
            stdscr.addstr(start_y + 4, 0, f"Profit/Loss: {profit_loss:.2f} {currency}", curses.color_pair(4))
            stdscr.addstr(start_y + 5, 0, f"Value of CGT-Free coins: {cgt_free_value:.2f} {currency}", curses.color_pair(5))
            stdscr.addstr(start_y + 6, 0, f"Value of non-CGT-Free: {non_cgt_free_value:.2f} {currency}", curses.color_pair(6))
            stdscr.addstr(start_y + 8, 0, "Options: (v)iew inventory, (r)emove entry, (a)dd more gold, (c)hange settings, (e)xit", curses.color_pair(7))
        except curses.error:
            pass
            
        stdscr.refresh()
        
        # Handle input
        try:
            key = stdscr.getch()
        except curses.error:
            continue
            
        # Handle key presses
        if key == ord('v'):
            stdscr.nodelay(0)  # Disable nodelay for menu
            display_inventory(stdscr, inventory, currency)
            stdscr.nodelay(1)  # Re-enable nodelay for animation
        elif key == ord('r'):
            inventory = remove_entry(stdscr, inventory)
        elif key == ord('a'):
            purchase_name = get_user_input(stdscr, f"Enter the name of purchase {purchase_id}: ")
            is_cgt_free = get_user_input(stdscr, "Is this a CGT-Free coin? (y/n): ").strip().lower()
            
            if is_cgt_free == 'y':
                coin_type = get_menu_choice(stdscr, 
                    ["Select coin type:",
                     "(1) Sovereign",
                     "(2) Britannia"],
                    "Enter choice (1-2): ")
                
                if coin_type == '1':  # Sovereign
                    weight_options = {
                        "1": ("double", 15.97, "Double Sovereign"),
                        "2": ("full", 7.98, "Full Sovereign"),
                        "3": ("half", 3.99, "Half Sovereign"),
                        "4": ("quarter", 1.997, "Quarter Sovereign")
                    }
                    
                    weight_choice = get_menu_choice(stdscr,
                        ["Select sovereign size:",
                         "(1) Double Sovereign - 15.97g",
                         "(2) Full Sovereign - 7.98g",
                         "(3) Half Sovereign - 3.99g",
                         "(4) Quarter Sovereign - 1.997g"],
                        "Enter your choice (1-4): ")
                    
                    if weight_choice not in weight_options:
                        stdscr.addstr(8, 0, "Invalid choice. Press any key to continue.")
                        stdscr.refresh()
                        stdscr.getch()
                        continue
                    
                    size_key, purchase_weight, name = weight_options[weight_choice]
                    
                    
                elif coin_type == '2':  # Britannia
                    weight_options = {
                        "1": ("1oz", 31.1035, "1oz Britannia"),
                        "2": ("1/2oz", 15.55175, "1/2oz Britannia"),
                        "3": ("1/4oz", 7.775875, "1/4oz Britannia")
                    }
                    
                    weight_choice = get_menu_choice(stdscr,
                        ["Select Britannia size:",
                         "(1) 1oz Britannia - 31.1035g",
                         "(2) 1/2oz Britannia - 15.55175g",
                         "(3) 1/4oz Britannia - 7.775875g"],
                        "Enter your choice (1-3): ")
                    
                    if weight_choice not in weight_options:
                        stdscr.addstr(6, 0, "Invalid choice. Press any key to continue.")
                        stdscr.refresh()
                        stdscr.getch()
                        continue
                    
                    size_key, purchase_weight, name = weight_options[weight_choice]

            else:
                weight_input = get_user_input(stdscr, f"Enter the weight for {purchase_name} (e.g., 20g or 1oz): ").strip().lower()
                if weight_input.endswith('g'):
                    purchase_weight = float(weight_input[:-1])
                elif weight_input.endswith('oz'):
                    purchase_weight = float(weight_input[:-2]) * 31.1035  # Convert ounces to grams
                else:
                    stdscr.addstr(2, 0, "Invalid weight unit. Please enter weight in grams (g) or ounces (oz).")
                    stdscr.refresh()
                    stdscr.getch()
                    continue
            
            purchase_price = float(get_user_input(stdscr, f"Enter the purchase price ({currency}) for {purchase_name}: "))
            purchase_date = get_user_input(stdscr, f"Enter the purchase date for {purchase_name} (YYYY-MM-DD): ")
            
            inventory.append({
                'id': purchase_id,
                'name': purchase_name,
                'price': purchase_price,
                'weight': purchase_weight,
                'date': purchase_date,
                'gold_price': gold_price,
                'gold_price_timestamp': datetime.fromtimestamp(timestamp).isoformat(),
                'is_cgt_free': is_cgt_free == 'y'
            })
            
            purchase_id += 1
            save_inventory(inventory)
        elif key == ord('c'):
            stdscr.clear()
            stdscr.addstr(0, 0, "Settings:")
            stdscr.addstr(1, 0, "(1) Change API key")
            stdscr.addstr(2, 0, "(2) Change currency")
            stdscr.addstr(3, 0, "(3) Back to main menu")
            stdscr.refresh()
            option = stdscr.getch()
            if option == ord('1'):
                config = change_api_key(stdscr, config)
                api_key = config.get("api_key", "")
            elif option == ord('2'):
                config, inventory, new_gold_price, new_timestamp = change_currency(stdscr, config, api_key, inventory)
                if new_gold_price is not None and new_timestamp is not None:
                    gold_price = new_gold_price
                    timestamp = new_timestamp
                    readable_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                currency = config.get("currency", "USD")
            elif option == ord('3'):
                continue
        elif key == ord('e'):
            break

if __name__ == "__main__":
    curses.wrapper(main)
