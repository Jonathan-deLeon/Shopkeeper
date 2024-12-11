"""
A tycoon game about running a shop

Takes place in a DnD style medieval fantasy land 
"""

from items import ItemType, Storage, get_items_of_type, Item, random_valid_item
from customers import get_customer, Customer, DialogueType, get_dialogue
from random import choice, choices, randint
from math import floor
from time import sleep
import os

# This is cached at the start, do not fill out
storages =[]

stats = {"Customers Served": 0, 
        "Money made": 0,
        "Money spent": 0,
        "Items sold": 0,
        "Discounts given": 0,
        "Upcharges attempted": 0,
        "Upcharges succeeded ": 0,
        "Haggles agreed upon": 0,
        "Haggles rejected": 0
         }

# Starting values when the game begins
day = 1
silver = 200
shop_level = 1
reputation = 0

goal_silver = 2500

# Amount of customers that come in each morning
daily_customers = 3

# Amount you pay for operating costs daily
default_operating_cost = 15
# Cost per upgrade (multiplied by shop level)
shop_upgrade_cost = 100
max_customers_per_shop_level = 6
# How much operating costs increases
precent_operating_cost_step = 10

# The item type and margin
margins = {}
# At what average margins your reputation will decay
high_margin_percent = 50
# At what average margins your reputation will improve
low_margin_percent = 20

# Set up storages and their default values
shelf = Storage(24, [ItemType.Materials, ItemType.Consumables, ItemType.Common], "Shelves", 8)
table = Storage(12, [ItemType.Valuables, ItemType.Supplies, ItemType.Loot], "Table", 4)
rack = Storage(5, [ItemType.Weapons, ItemType.Tools], "Racks", 2)
stand = Storage(2, [ItemType.Armor], "Stands", 1)

def get_storages() -> list:
    return [obj for obj in globals().values() if isinstance(obj, Storage)]     

# fills the storage with random items from the catagories
def debug_storage_fill(storage: Storage):
    storage.held_items.clear()

    for x in range(storage.max_storage // 2):
        chosen_type = choice(storage.stored_types)
        chosen_item = choice(get_items_of_type(chosen_type))
        storage.add_items(chosen_item, 1)
    
    # for i in storage.held_items:
    #     print(i, storage.held_items[i])

def buy_phase():
    clear_console()
    print("---------- Buying Stock ---------")
    for storage in storages:
        print(f"{storages.index(storage) + 1}: {storage} ({storage.get_status()}/{storage.max_storage})")
    print(f"{len(storages) + 1}: Auto Buy")
    print(f"{len(storages) + 2}: Begin day {day}")
    print("---------------------------------")

    getting_input = True
    while(getting_input):
        player_choice = int_input(1, len(storages) + 2, "Choose:")

        # check if player chooses auto buy, catching it 
        # before player choice is used as list index
        if(player_choice == len(storages) + 1):
                auto_buy()
                getting_input = False
                return
        # Leave buy phase if the player chooses to skip
        elif(player_choice == len(storages) + 2):
            return

        # Make sure selected storage is not full
        if(storages[player_choice - 1].max_storage - storages[player_choice - 1].get_status() == 0):
            print("That Storage is full!")
        else: 
            # otherwise select the storage chosen
            chosen_storage = storages[player_choice -1]
            getting_input = False
    
    buy_for_storage(chosen_storage)

def buy_for_storage(chosen_storage: Storage):
    clear_console()
    print("What would you like to buy?")
    print(f"You have {silver} silver")

    print("-----------------------")
    counter = 1
    stock_options = chosen_storage.get_all_valid_items()

    if(ItemType.Loot in stock_options.keys()):
        del stock_options[ItemType.Loot]

    for type in stock_options.keys():
        print(f"{type.name}:")
        for item in stock_options[type]:
            print_message = f"{counter}: {item} - {item.price} silver"
            if(item in chosen_storage.held_items):
                print_message += f" (You have {chosen_storage.held_items[item]})"
            print(print_message)
            counter += 1

        # If this is the last listed catagory do not print the space
        # I know this is slop but it works :(
        print("")
    print(f"{counter}: Back")
    print("-----------------------")

    # combine all stock items into one big list
    all_items = sum(list(stock_options.values()), [])

    getting_input = True
    while(getting_input):
        player_choice = int_input(1, len(all_items) + 1, "Choose:")

        # Return to buy phase if they choose to go back
        if(player_choice == len(all_items) + 1):
            buy_phase()
            return

        # Calculate room left in storage
        remaining_space = chosen_storage.max_storage - chosen_storage.get_status()
        chosen_item = all_items[player_choice - 1]
        # Calculate max quantity the player could afford
        max_affordable = silver//chosen_item.price

        # Make the player choose something else if they cant afford even 1
        if(max_affordable == 0):
            print(f"You cant afford that! (missing {chosen_item.price - silver} silver)")
            continue
        else: getting_input = False

        chosen_quantity = int_input(0, min(remaining_space, max_affordable), f"How many? (max {min(remaining_space, max_affordable)}):")
        total_price = chosen_item.price * chosen_quantity

        # Check if the player can afford it
        if(total_price > silver):
            print("You can't afford that!")
            buy_for_storage(chosen_storage)

        # Confirm with the player and show them the total
        print(f"Selected: {chosen_quantity} {chosen_item} (Total price: {total_price} silver)")

        if(yes_no_input("Confirm?")):
            chosen_storage.add_items(chosen_item, chosen_quantity)
            change_player_currency(-total_price)

            # If the storage is now full after purchase return to stock screen
            if(chosen_storage.max_storage - chosen_storage.get_status() == 0):
                buy_phase()
                return
        
        # return to the buy menu for selected storage
        buy_for_storage(chosen_storage)

def int_input(min, max, input_prompt) -> int:
    """
    gets input within the range and returns the int.
    """
    getting_input = True
    while getting_input:
    # if a value error occurs try will catch it and execute the code in the except block
        try:
            player_choice = int(input(input_prompt + " "))
            if(player_choice in range(min, max + 1)):
                getting_input = False
                return player_choice
            else:
                print(f"You must enter a number between {min} and {max}")
        except ValueError:
            print(f"You must enter a number between {min} and {max}")

def auto_buy():
    """
    Spend a player determined amount of money on random items
    price can be capped
    """
    clear_console()
    print("------------ Auto Buy -----------")
    print(f"You have {silver} silver")

    amount_to_spend = int_input(0, silver, "How much do you want to spend?")
    max_price = int_input(0, silver, "Maximum item price:")
    amount_remaining = amount_to_spend

    # Create a list of storages
    valid_storages = storages.copy()
    # Turn storages size into weight, so bigger storages get filled more often
    weights_list = []
    
    # Filter out loot if it can be stored (player cannot buy loot)
    for storage in valid_storages:
        if ItemType.Loot in storage.stored_types: storage.stored_types.remove(ItemType.Loot)
        weights_list.append(storage.max_storage)

    items_bought = {}
    # While the algorithim has budget left
    while(amount_remaining > 0):
        # If there are no valid storages left end the algortihim early
        if len(valid_storages) == 0:
            break

        # Random Storage
        random_storage = choices(valid_storages, weights_list, k = 1)[0]

        #If the storage has room continue
        if(random_storage.get_status() < random_storage.max_storage):
            chosen_item = random_valid_item(min(amount_remaining, max_price), choice(random_storage.stored_types))
            # If chosen item returns null (No valid items remaining)
            # remove the storage from consideration
            if chosen_item == None:
                valid_storages.remove(random_storage)
                weights_list.remove(random_storage.max_storage)
                continue

            random_storage.add_items(chosen_item, 1)
            amount_remaining -= chosen_item.price
            #Add the item to the dict for display
            if chosen_item in items_bought.keys():
                items_bought[chosen_item] += 1
            else: items_bought[chosen_item] = 1
        # Otherwise remove it from consideration
        else: 
            valid_storages.remove(random_storage)
            weights_list.remove(random_storage.max_storage)

    change_player_currency(-(amount_to_spend - amount_remaining))
    sleep(0.35)
    print("")
    print(f"Bought {sum(items_bought.values())} items using {amount_to_spend - amount_remaining} silver")
    sleep(0.35)
    print("---------------------------------")
    sleep(0.35)
    print("")
    print("1: See details")
    sleep(0.35)
    print("2: Back to stock menu")
    sleep(0.35)
    player_choice = int_input(1, 2, "Choose:")

    if player_choice == 1:
        # List purchased items
        print("")
        if(len(items_bought.keys()) == 0):
            sleep(0.2)
            print("Nothing to show.")
        else: 
            for item, amount in items_bought.items():
                sleep(0.2)
                print(f"{item.name} x {amount}")
        print("")
        input("Press enter to return to stock screen ")
        buy_phase()
    else: buy_phase()

def shop_phase():
    for i in range(daily_customers):
        if(i != 0):
            print("")
            next = input("Press enter to greet the next customer ")
            print("")
        customer = get_customer()
        item_to_sell = None
        #roll and if the player can store another loot item
        if(random_roll(customer.offer_item_chance)) and table.get_status() < table.max_storage:
            item_to_sell = choice(get_items_of_type(ItemType.Loot))

        chosen_items = choose_items(customer)
        clear_console()
        # if customer cant find anything and has nothing to sell they walk out
        if len(chosen_items) == 0 and item_to_sell == None:
            sleep(0.3)
            print(f"{customer.name}, {customer.title} left as they could not find anything they wanted.")
            continue

        approach_counter(customer, chosen_items, item_to_sell)
    
    print("")
    sleep(0.4)
    input("That was the last customer, press enter to close up shop. ")
    print("")

def approach_counter(customer: Customer, chosen_items, item_to_sell):
    """
    take the customer's cart of items and present them to the player.
    """
    print("------------ Customer -----------")
    sleep(0.5)
    print(f"{customer.name}, {customer.title} approaches the counter.")
    stats["Customers Served"] += 1
    
    # Haggle
    if(len(chosen_items) != 0 and random_roll(customer.haggle_chance)):
        print("")
        sleep(0.3)
        haggle_item = choice(chosen_items)
        haggle_item.price = get_adjusted_price(haggle_item)
        # Adjust for margins
        # The amount of silver the customer wants off
        # minimum 10% of the price, max 30
        haggle_amount = randint(haggle_item.price // 10, haggle_item.price // 3)
        if(haggle_amount == 0): 
            haggle_amount = 1
        # Print the request
        print(f"{get_dialogue(DialogueType.haggle_attempt)}")
        sleep(0.3)
        print(f"{haggle_item}: {haggle_item.price} -> {haggle_item.price - haggle_amount} ({haggle_amount} silver discount)")
        sleep(0.3)
        if(yes_no_input("Accept?")):
            # The customer buys the item instantly with the new price
            if(random_roll(30)): change_reputation(1)
            change_player_currency(haggle_item.price - haggle_amount)
            stats["Items sold"] += 1
            stats["Haggles agreed upon"] += 1
            chosen_items.remove(haggle_item)
        elif random_roll(customer.haggle_abandon_chance):
            # The customer skips buying the item and it returns to storage
            print(get_dialogue(DialogueType.haggle_abandon))
            chosen_items.remove(haggle_item)
            smart_store(haggle_item, 1)
            stats["Haggles agreed upon"] += 1
        else:
            # The customer offered to pay full price for the item
            print(get_dialogue(DialogueType.haggle_failure))
            stats["Haggles agreed upon"] += 1
    if len(chosen_items) != 0:
        total_price = 0
        print("")
        for item in chosen_items:
            sleep(0.3)
            print(f"{item} - {get_adjusted_price(item)} silver")
            total_price += get_adjusted_price(item)
        sleep(0.3)
        print("")
        print(f"Total: {total_price}")
        print("")
        sleep(0.2)
        print(f"1: upcharge {round(total_price * 0.1)} silver ({100 - customer.upcharge_reject_chance}% chance)")
        sleep(0.2)
        print(f"2: discount {round(total_price * 0.1)} silver")
        sleep(0.2)
        print("3: accept")
        print("")
        sleep(0.35)
        player_choice = int_input(1, 3, "Choose:")
        if(player_choice == 1):
            stats["Upcharges attempted"] += 1
            sleep(0.3)
            if(random_roll(customer.upcharge_reject_chance)):
                print(get_dialogue(DialogueType.upcharge_failure))
                print(f"{customer.name} storms out.")
                return
            else: 
                print(get_dialogue(DialogueType.upcharge_success))
                change_player_currency(total_price + round(total_price * 0.1))
                stats['Upcharges succeeded'] += 1
            if random_roll(40): (change_reputation(-1))
        elif(player_choice == 2):
            sleep(0.3)
            print(get_dialogue(DialogueType.discount))
            change_player_currency(total_price - round(total_price * 0.1))
            if random_roll(55): (change_reputation(1))
        elif(player_choice == 3):
            change_player_currency(total_price)
            if(item_to_sell == None):
                sleep(0.3)
                print(get_dialogue(DialogueType.leave))
        stats["Items sold"] += len(chosen_items)
    if(item_to_sell != None):
        sleep(0.3)
        offer_item(item_to_sell)
        print("")
        sleep(0.3)
        print(get_dialogue(DialogueType.leave))

    print("")
    sleep(0.3)
    print(f"{customer.name} leaves.")

def get_adjusted_price(item) -> int:
    """
    adjusts for margins
    """
    adjusted = int(item.price * (margins[item.item_type] / 100 + 1))
    if adjusted < 1:
        return item.price + 1
    else:
        return adjusted

def change_reputation(amount):
    """
    Adds or removes player repuation
    Positive for add, negative for remove
    """
    global reputation
    reputation += amount

def reputation_to_name(reputation) -> str:
    """
    converts reputation to a catagory
    """
    if reputation <= -15:
        return "Infamous"
    elif reputation <= -10:
        return "Sketchy"
    elif reputation <= -5:
        return "Disliked"
    elif reputation <= 5:
        return "Neutral"
    elif reputation <= 10:
        return "Liked"
    elif reputation <= 15:
        return "Favorable"
    else:
        return "Esteemed"

def calculate_customer_bonus():
    """
    calculate customer bonus
    """
    global daily_customers
    reputation_customer_impact = floor(reputation / 5)
    if reputation_customer_impact > 3:
        reputation_customer_impact = 3
    elif reputation_customer_impact < -3:
        reputation_customer_impact = -3
    daily_customers += reputation_customer_impact
    daily_customers += (shop_level - 1) * 2

    if(daily_customers > (shop_level * max_customers_per_shop_level)):
        daily_customers = (shop_level * max_customers_per_shop_level)
    if(daily_customers < 2):
        daily_customers = 2
         
def offer_item(item_to_sell):
    """
    A customer will try to offer the player an item
    """
    print("")
    sleep(0.4)
    print(get_dialogue(DialogueType.sell))
    sleep(0.4)
    print(f"{item_to_sell} - {item_to_sell.price} silver")
    sleep(0.4)
    if(yes_no_input("Accept?")):
        if silver < item_to_sell.price:
                sleep(0.4)
                print("looks like you can't afford it. I'll go elsewhere.")
        else:
            change_player_currency(-item_to_sell.price)
            if(random_roll(35)): change_reputation(1)
            smart_store(item_to_sell, 1)

def random_roll(success_precentage) -> bool:
    """
    returns true if roll passed, false if fail
    """
    if(randint(0, 100) <= success_precentage):
        return True
    else: return False

def change_player_currency(amount):
    """
    Adds or removes player currency
    Positive for add, negative for remove
    """
    global silver
    #print(f"You now have {silver + amount} silver (was {silver})")
    silver += amount

    if(amount < 0):
        stats["Money spent"] += amount
    else:
        stats["Money made"] += amount

def smart_store(item_to_add: Item, quantity: int):
    """
    tries to add the item to any storage that accepts it.
    returns true if item is stored, false is not
    """
    found_storage = smart_validity_check(item_to_add, quantity)
    if(found_storage != None):
        found_storage.add_items(item_to_add, quantity)
        return True
    else: return False

def smart_remove(item_to_remove: Item, quantity: int):
    for storage in storages:
        # Tries to remove the item from every storage
        if storage.remove_items(item_to_remove, quantity):
            return True
    # If none work return false
    return False


def smart_validity_check(item_to_add: Item, quantity: int) -> Storage:
    """
    sees if an item of a certain type/quantity can be stored.
    returns the storage if true, returns None if not
    """
    
    for storage in storages:
        if storage.item_validity_check(item_to_add, quantity):
            return storage
    
    return None

def yes_no_input(prompt) -> bool:
    """
    gets a y (for yes) or "n" from the player.
    True for yes, false for no
    """
    getting_input = True
    while getting_input:
        # loop until y or n is typed
        player_input = input(f"{prompt} (y/n): ")
        if player_input == "y":
            getting_input = False
            return True
        elif player_input == "n":
            getting_input = False
            return False
        else: print("Please choose y or n")
    
def choose_items(customer: Customer):
    """
    fills a cart with valid items and removes them from storage
    """
    cart = []
    #
    buy_odds = 100
    while(len(cart) < customer.max_held_items and random_roll(buy_odds)):
        valid_items = customer.get_valid_stock([shelf, table, rack, stand], margins)
        #if there are no valid items remaining force end shopping
        if len(valid_items) == 0:
            break
        item_choice = choices(list(valid_items.keys()), k = 1)[0]

        # If the customer has already bought
        # an item twice reduce buy odds
        if(item_choice in cart):
            buy_odds = buy_odds * 0.65
        else:
            buy_odds = buy_odds * 0.8

        cart.append(item_choice)
        customer.budget -= item_choice.price
        
        smart_remove(item_choice, 1)

    return cart

def day_summary(day_start_silver):

    made_or_lost = "made"
    if(silver - day_start_silver < 0):
        made_or_lost = "lost"

    clear_console()
    print("------------ Summary ------------")
    sleep(0.3)
    print(f"Day {day} complete. You {made_or_lost} {abs(silver - day_start_silver)} silver.")
    sleep(0.3)
    print(f"{daily_customers} people visited your shop today!")
    sleep(0.3)
    print(f"Your store's reputation is {reputation_to_name(reputation)}.")
    sleep(0.3)
    print(f"You spent {calculate_operating_cost()} silver on operating costs today.")
    sleep(0.3)
    if(calculate_margin_ratio() >= high_margin_percent/100):
        print("Word around town is that your prices drive people away.")
    elif(calculate_margin_ratio() <= low_margin_percent/100):
        print("Word around town is that you offer generous prices.")
    sleep(0.3)
    print("---------------------------------")
    sleep(0.3)
    input("Press enter to continue ")

def options_menu():
    clear_console()
    print("------------ Options ------------")
    print("1: Manage shop")
    print("2: Adjust margins")
    print("3: View item catalogue")
    print("4: View stats")
    print("5: Proceed to stock purchasing")
    print("6: Quit game")
    print("---------------------------------")
    print("")

    player_choice = int_input(1, 6, "Choose: ")

    if(player_choice == 1):
        manage_shop()
    elif(player_choice == 2):
        adjust_margins()
    elif(player_choice == 3):
        show_item_catalogue()
    elif(player_choice == 4):
        view_stats()
    elif(player_choice == 5):
        return
    else: 
        if(yes_no_input("Are you sure?")):
            quit()
        else: options_menu()

def view_stats():
    clear_console()
    print("------------- Stats -------------")
    sleep(0.3)
    print("Your stats:")
    sleep(0.3)
    print_stats()
    sleep(0.3)
    print("---------------------------------")

    input("Press enter to go back ")
    options_menu()

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_item_catalogue():
    """
    Prints all items in the game.
    """
    clear_console()
    print("----------- Catalogue -----------")

    for type in list(ItemType):
        print(f"{type.name}:")
        for item in get_items_of_type(type):
            print(f"    {item}: {item.price} silver")
        if(list(ItemType).index(type) != len(list(ItemType))-1):
            print("")

    print("---------------------------------")
    print("")
    input("Press enter to go back ")
    options_menu()

def manage_shop():
    """
    handles shop upgrades
    """
    clear_console()
    print("------------- Stats -------------")
    print(f"Shop level: {shop_level}")
    print(f"Current operating costs: {calculate_operating_cost()}")
    print(f"Max customers: {shop_level * 6}")
    print("---------------------------------")

    print("1: Upgrade Shop")
    print("2: Back")

    player_choice = int_input(1, 2, "Choose: ")
    if(player_choice == 1):
        clear_console()
        print(f"---- Upgrade shop to level {shop_level + 1} ----")
        print(f"Max customers: {shop_level * max_customers_per_shop_level} -> {(shop_level + 1) * max_customers_per_shop_level}")
        for storage in storages:
            # Since upgrade step doesn't apply at shop level 1
            # you can multiply upgrade_step by shop_level instead of shop_level + 1
            print(f"{storage}: {storage.max_storage} -> {storage.max_storage + (storage.upgrade_step * shop_level)}")
        print(f"Operating cost multiplier: {(shop_level - 1) * precent_operating_cost_step}% -> {(shop_level) * precent_operating_cost_step}%")
        print("---------------------------------")
        print(f"Cost: {shop_upgrade_cost * shop_level} (You have {silver})")

        if(silver < shop_upgrade_cost * shop_level):
            print("")
            sleep(0.3)
            print("Can't afford!")
            sleep(0.3)
            print("")
            sleep(0.3)
            input("Press enter to go back. ")
        elif(yes_no_input("Confirm?")):
            upgrade_shop()
            print("")
            sleep(0.3)
            print(f"Shop upgraded to level {shop_level}.")
            sleep(0.3)
            input("Press enter to go back. ")
        manage_shop()
    if(player_choice == 2):
        options_menu()

def upgrade_shop():
    global shop_level
    change_player_currency(shop_upgrade_cost * shop_level)
    shop_level += 1
    for storage in storages:
        storage.max_storage += storage.upgrade_step
    
def adjust_margins():
    global margins
    clear_console()
    print("------------ Margins ------------")
    counter = 1
    for item_type in margins:
        print(f"{counter}: {item_type.name} - {margins[item_type]}%")
        counter += 1
    print(f"{counter}: Change all")
    print(f"{counter + 1}: Back")
    print("---------------------------------")

    margin_choice = int_input(1, len(margins.keys()) + 2, "Choose:")

    if margin_choice == len(margins.keys()) + 2:
        options_menu()
        return
    
    amount_choice = int_input(0, 100, "Set amount: ")

    # Change margins
    if margin_choice == len(margins.keys()) + 1:
        margins = {key: amount_choice for key in margins}
    else: set_margin(list(margins.keys())[margin_choice - 1], amount_choice)

    adjust_margins()

def calculate_operating_cost() -> int:
    # Increases per day
    operating_cost = (default_operating_cost + (day * 3))
    # adds 10% per shop level
    operating_cost * 1 + (shop_level/10 - 1)
    return int(operating_cost)

def set_margin(item_type: ItemType, new_margin: int):
    margins[item_type] = new_margin

def calculate_margin_ratio() -> float:
    """
    Calculate your margin percent
    """
    # Get max possible margins
    margin_max = len(list(ItemType)) * 100
    # Get current margins
    margin_points = 0
    for item_type in list(ItemType):
        margin_points += margins[item_type]
    # Chance to lower rep if margins are too high
    # and vice versa
    return margin_points/margin_max

def calculate_margin_impact():
    """
    Change reputation based on margins
    """
    ratio = calculate_margin_ratio()
    if(ratio >= high_margin_percent/100):
        if(random_roll(50)):
            change_reputation(-1)
        elif(random_roll(25)):
            change_reputation(-2)
    if(ratio <= low_margin_percent/100):
        if(random_roll(50)):
            change_reputation(1)
        elif(random_roll(25)):
            change_reputation(2)

def print_stats():
    for name, stat in stats.items():
        print(f"    {name}: {stat}")
        sleep(0.3)

def lose():
    print("You have gone bankrupt.")
    sleep(0.3)
    print("Your final stats:")
    print_stats()
    sleep(0.3)
    print("Better luck next time!")
    quit()

def win():
    print(f"You collected {goal_silver} and won!")
    sleep(0.3)
    print("Your final stats:")
    print_stats()
    sleep(0.3)
    print("Now you can retire in peace...")
    quit()

def init():
    global storages
    # Cache storages at the start of the game
    storages = get_storages()
    # cache default margins
    for item_type in list(ItemType):
        set_margin(item_type, 10)

def game_loop():
    global day
    while True:
        day_start_silver = silver
        options_menu()
        buy_phase()
        shop_phase()
        calculate_margin_impact()
        day_summary(day_start_silver)
        change_player_currency(-calculate_operating_cost())
        # if the player ends the day below 0 they lose
        if(silver <= 0):
            lose()

        calculate_customer_bonus()
        day += 1

def main_menu():
    print("""
⠀⠀⠀⠀⠀⠀⡠⠔⠒⠂⢤⡔⠁⠀⠀⠈⠢⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⡜⠀⢀⢠⣤⡀⠑⣾⣴⣷⡀⠀⢡⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢴⡇⠀⠸⣿⣿⣿⠀⡹⠿⠟⠀⢀⠲⣄⠀⠀⠀⠀
⠀⠀⢀⡾⠁⠘⠦⠤⣌⠉⢁⠴⠣⠤⠤⢐⠁⠀⠘⢷⡀⠀⠀
⢤⣤⡶⠁⠀⠀⠀⠀⣈⣿⣭⣍⣉⣽⣿⡇⠀⠀⠀⠈⢷⠠⣤
⢾⡀⠀⠀⠀⠀⠀⠉⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠈⡼⡑
⠈⢛⡄⠀⠀⠀⠀⠀⣿⣿⡿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⣿⠀
⠀⢸⡇⠀⠀⠀⠀⠀⢿⠇⠀⠀⠈⢻⣿⠇⠀⠀⠀⠀⠀⡿⠀
⠀⠀⢶⡀⠀⠀⠀⠀⠸⣦⠀⠀⠀⢀⠏⠀⠀⠀⠀⠀⡰⠆⠀
⠀⠀⠈⢳⣄⠀⠀⠀⠀⠘⠾⠭⠵⠋⠀⠀⠀⠀⢀⣴⠏⠀⠀
⠀⠀⠀⠀⠀⠳⢢⢄⣀⠀⠀⠀⠀⠀⠀⣀⣠⡴⠟⠁⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⠑⢧⣀⡟⣉⡝⡑⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    """)
    print("""
⠀⠀⠀⢀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⡀⠀⠀⠀
⠀⠀⢠⡿⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⢿⡄⠀⠀
⠀⣠⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣄⠀
⢠⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⡄
⣿⡟⠛⠛⠛⣻⣟⠛⠛⠛⢛⣿⡛⠛⠛⠛⣻⣟⠛⠛⠛⢛⣿
⠈⠻⣶⣶⠾⠋⠙⠷⣶⡶⠟⠉⠻⢶⣶⠾⠋⠙⠷⣶⣶⠟⠁
⠀⠀⣿⠀⠀⢀⣤⣤⣤⣤⡀⠀⣤⣤⣤⣤⣤⡄⠀⠀⣿⠀⠀
⠀⠀⣿⠀⠀⣿⠁⠀⠀⢹⡇⢸⣿⠀⠀⠀⠈⣿⠀⠀⣿⠀⠀
⠀⠀⣿⠀⠀⣿⠀⠀⠀⢸⡇⢸⣿⣀⣀⣀⣠⣿⠀⠀⣿⠀⠀
⠀⠀⣿⠀⠀⣿⠀⠀⠀⢸⡇⠀⠙⠛⠛⠛⠛⠁⠀⠀⣿⠀⠀
⠀⠀⣿⣀⣀⣿⣀⣀⣀⣸⣇⣀⣀⣀⣀⣀⣀⣀⣀⣀⣿⠀⠀
⠀⠀⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠀⠀

""")

    print("Welcome to shopkeeper!")
    input("Press enter to play...")

if __name__ == '__main__':
    init()
    main_menu()
    game_loop()
