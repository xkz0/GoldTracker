import curses
import json
from datetime import datetime, timedelta
from getprice import get_gold_price
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
        config = {"api_key": ""}
        save_config(config)
    return config

def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)

def display_inventory(stdscr, inventory):
    stdscr.clear()
    stdscr.addstr(0, 0, "Inventory:")
    for idx, item in enumerate(inventory, start=1):
        stdscr.addstr(idx, 0, f"ID: {item['id']}, Name: {item['name']}, Price: £{item['price']:.2f}, Weight: {item['weight']:.2f}g, Date: {item['date']}, Gold Price: £{item['gold_price']:.2f}")
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

def main(stdscr):
    config = load_config()
    if 'api_key' not in config or len(config['api_key']) != 32:
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
                gold_price, timestamp = get_gold_price(api_key)
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
            gold_price, timestamp = get_gold_price(api_key)
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
        for i, line in enumerate(ascii_art):
            stdscr.addstr(i, 0, line, curses.color_pair(8))
        stdscr.addstr(9, 0, f"Current Price of Gold per Troy Ounce at {readable_date} in GBP: {gold_price:.2f}", curses.color_pair(8))
        total_weight = sum(item['weight'] for item in inventory)
        total_weight_oz = total_weight / 31.1035  # Convert grams to troy ounces
        total_value = sum((item['weight'] / 31.1035) * gold_price for item in inventory)
        total_purchase_price = sum(item['price'] for item in inventory)
        profit_loss = total_value - total_purchase_price
        
        cgt_free_value = sum((item['weight'] / 31.1035) * gold_price for item in inventory if item['is_cgt_free'])
        non_cgt_free_value = total_value - cgt_free_value
        
        stdscr.addstr(10, 0, f"Total weight of gold: {total_weight:.2f} grams ({total_weight_oz:.2f} troy ounces)", curses.color_pair(1))
        stdscr.addstr(11, 0, f"Total value of gold holdings: {total_value:.2f} GBP", curses.color_pair(2))
        stdscr.addstr(12, 0, f"Total purchase price: {total_purchase_price:.2f} GBP", curses.color_pair(3))
        stdscr.addstr(13, 0, f"Profit/Loss: {profit_loss:.2f} GBP", curses.color_pair(4))
        stdscr.addstr(14, 0, f"Value of CGT-Free coins: {cgt_free_value:.2f} GBP", curses.color_pair(5))
        stdscr.addstr(15, 0, f"Value of non-CGT-Free: {non_cgt_free_value:.2f} GBP", curses.color_pair(6))
        stdscr.addstr(17, 0, "Options: (v)iew inventory, (r)emove entry, (a)dd more gold, (c)hange API key, (e)xit", curses.color_pair(7))
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == ord('v'):
            display_inventory(stdscr, inventory)
        elif key == ord('r'):
            inventory = remove_entry(stdscr, inventory)
        elif key == ord('a'):
            purchase_name = get_user_input(stdscr, f"Enter the name of purchase {purchase_id}: ")
            is_cgt_free = get_user_input(stdscr, "Is this a CGT-Free coin? (y/n): ").strip().lower()
            
            if is_cgt_free == 'y':
                weight_option = get_user_input(stdscr, "Select the weight (1oz, 1/2oz, 1/4oz): ").strip().lower()
                urls = {
                    "1oz": "https://www.royalmint.com/invest/bullion/bullion-coins/gold-coins/britannia-2025-1oz-gold-bullion-coin/",
                    "1/2oz": "https://www.royalmint.com/invest/bullion/bullion-coins/gold-coins/britannia-2024-half-oz-gold-bullion-coin-in-blister/",
                    "1/4oz": "https://www.royalmint.com/invest/bullion/bullion-coins/gold-coins/britannia-2025-14oz-gold-bullion-coin-in-blister/"
                }
                if weight_option in urls:
                    try:
                        current_price = get_cgt_free_coin_price(urls[weight_option])
                        stdscr.addstr(2, 0, f"Current price of {weight_option} CGT-Free coin: £{current_price:.2f}")
                        stdscr.refresh()
                        stdscr.getch()
                    except Exception as e:
                        stdscr.addstr(2, 0, f"Error fetching price for {weight_option} coin: {e}")
                        stdscr.refresh()
                        stdscr.getch()
                        continue
                else:
                    stdscr.addstr(2, 0, "Invalid weight option. Please select 1oz, 1/2oz, or 1/4oz.")
                    stdscr.refresh()
                    stdscr.getch()
                    continue
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
            
            purchase_price = float(get_user_input(stdscr, f"Enter the purchase price (GBP) for {purchase_name}: "))
            purchase_date = get_user_input(stdscr, f"Enter the purchase date for {purchase_name} (YYYY-MM-DD): ")
            
            if is_cgt_free == 'y':
                purchase_weight = {
                    "1oz": 31.1035,
                    "1/2oz": 15.55175,
                    "1/4oz": 7.775875
                }[weight_option]
            
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
            config = change_api_key(stdscr, config)
            api_key = config.get("api_key", "")
        elif key == ord('e'):
            break

if __name__ == "__main__":
    curses.wrapper(main)
