"""
handles customers and their behaviors

also dialogue
"""

from random import randint, choice, choices
from items import ItemType, Storage, get_items_of_type
from enum import Enum

# Potential names
male_names = [
    "Aethelred", "Aldous", "Almeric", "Ancel", "Baldric", "Bartholomew", "Bertram", "Cedric", "Cuthbert", "Damian",
    "Edmund", "Eldred", "Engelbert", "Ethelbert", "Francis", "Geoffrey", "Godefroi", "Godwin", "Hamlin", "Henry",
    "Hugh", "Ivo", "Kenric", "Leofric", "Milo", "Miles", "Nicholas", "Nigel", "Osbert", "Osric", "Otto", "Peregrine",
    "Peter", "Ranulf", "Raymond", "Reginald", "Richard", "Robert", "Roger", "Simon", "Stephen", "Thaddeus", 
    "Theobald", "Thomas", "Tristram", "Ulf", "Walter", "Wilfred", "William", "Wulfric", "Alban", "Basil", "Benedict",
    "Clement", "Conrad", "Edgar", "Ernest", "Ferdinand", "Gilbert", "Godfrey", "Graham", "Harold", "Humphrey", 
    "Ivan", "Laurence", "Leonard", "Lionel", "Maurice", "Randolph", "Sebastian", "Victor", "Waldemar"
]

female_names = [
    "Adelina", "Agnes", "Alice", "Amice", "Anastasia", "Beatrice", "Blanche", "Cecily", "Clarice", "Dulcibella",
    "Edith", "Eleanor", "Elfreda", "Eva", "Frederica", "Gisela", "Guinevere", "Gundred", "Gwenllian", "Heloise",
    "Hilda", "Ida", "Isabeau", "Joan", "Jocelyn", "Judith", "Letitia", "Lucia", "Maud", "Matilda", "Philippa", 
    "Rosamund", "Rowena", "Sibyl", "Sybil", "Theodora", "Ursula", "Winifred", "Yolande", "Ysabel", "Yvette", 
    "Zara", "Zoe", "Aeliana", "Alix", "Amabel", "Avelina", "Bertha", "Briar", "Catherine", "Clotilde", "Diana", 
    "Edelina", "Elys", "Esme", "Felicity", "Flora", "Genevieve", "Gillian", "Helena", "Isolda", "Juliana", "Katherine",
    "Margaret", "Mirabel", "Rohese", "Sabina", "Serena", "Sophia", "Therese", "Wilhelmina"
]

artisan_titles = ["Basket Weaver", "Mason", "Alchemist", "Leather Worker", "Smith"]
male_noble_titles = ["Knight", "Duke", "Baron"]
female_noble_titles = ["Baroness", "Dame", "Duchess"]
adventurer_titles = ["Bard", "Cleric", "Ranger", "Rouge", "Fighter", "Paladin", "Druid"]
peasant_titles = ["Farmer", "Woodsman", "Butcher", "Laborer", "Hunter", "Vagrant"]

buy_dialogue = ["I'd like to buy these", "I'll take these"]
discount_dialogue = ["Thank you!", "That's very kind.", "What a selfless gesture...", "I am in your debt.", "Thanks.", "Appreciate it."]
sell_dialogue = ["I have something you might be interested in.", "Would you take this?", "Can I sell this here?", "Would you take this off my hands?",
                 "This thing is weighing down my bag, do you want it?"]
upcharge_success_dialogue = ["I suppose I can afford that...", "Fine, but I'm never visiting this establishment again!", 
                             "That wasn't on the label. Oh well...", "I suppose that is still a fair price.", "I really do need it... alright, sure."]
upcharge_failure_dialogue = ["You must take me for a fool.", "A donkey wouldn't pay that price!", "No way.", "Not in a million years!", 
                             "Your dirty tricks won't work on me.", "I will not be charged above the standard price!"]
haggle_attempt_dialogue = ["I think we can come to an agreement on this..."]
# failure means they still buy it, abandon means they won't buy the item
haggle_failure_dialogue = ["Worth a shot, right?", "You strike a hard bargain.", "I can respect a proprietor with a backbone.", "Standing firm, eh? Alright, fine."]
haggle_abandon_dialogue = ["Forget it then.", "A shame.", "Well I suppose that's that.", "If it must be so."]
leave_dialogue = ["Farewell.", "Until next time.", "Thanks.", "I'll be on my way.", "Goodbye."]

# Idea, if one adventurer comes in make others more common for the day (to simulate a party)
class Customer:
    # Items of interest is a list of ItemTypes
    # titles are added after the name, hinting at the customer's profession
    # titles should be a list of strings
    # names should be a list of names
    # rarity should increase by
    def __init__(self, min_budget, max_budget, items_of_interest, titles, names):
        self.budget = randint(min_budget, max_budget)
        self.items_of_interest = items_of_interest
        self.title = choice(titles)
        self.name = choice(names)
        self.inventory_size = 3
    
    def get_valid_stock(self, storages_to_check: list, margins: dict) -> dict:
        """
        takes a list of storages and returns dict of items 
        that are in budget and of interest to the customer.
        also returns the storage where the item was found.

        dict is item and quantity
        """

        valid_items = {}

        for storage in storages_to_check:
            for item in storage.held_items:
                if item.item_type in self.items_of_interest and int(item.price * (margins[item.item_type] / 100 + 1)) <= self.budget:
                    if item not in valid_items:
                        valid_items[item] = storage.held_items[item]
                    else: valid_items[item] += storage.held_items[item]
        
        return valid_items

    # Rarity of the customer, in precentage
    rarity = 0
    # Chance the customer leaves after being upcharged
    upcharge_reject_chance = 50
    # Chance the customer offers to sell you loot
    offer_item_chance = 0
    # Chance the customer tries to haggle
    haggle_chance = 25
    # Chance the customer abandons an item after haggle fail
    haggle_abandon_chance = 40
    # max items the customer can carry
    max_held_items = 3


class Artisan(Customer):
    rarity = 20
    haggle_chance = 25
    upcharge_reject_chance = 35
    def __init__(self):
        super().__init__(75, 150, [ItemType.Materials, ItemType.Tools, ItemType.Loot], artisan_titles, male_names + female_names)

    def __str__(self):
        return "Artisan"

class Adventurer(Customer):
    rarity = 7.5
    haggle_chance = 35
    offer_item_chance = 75
    upcharge_reject_chance = 75
    def __init__(self):
        super().__init__(175, 225, [ItemType.Weapons, ItemType.Armor, ItemType.Consumables, ItemType.Supplies], adventurer_titles, male_names + female_names)

    def __str__(self):
        return "Adventurer"
    
class Peasant(Customer):
    rarity = 70
    haggle_chance = 65
    upcharge_reject_chance = 45
    def __init__(self):
        super().__init__(10, 35, [ItemType.Common, ItemType.Tools], peasant_titles, male_names + female_names)
    
    def __str__(self):
        return "Peasant"

class Noble(Customer):
    rarity = 1.25
    haggle_chance = 0
    upcharge_reject_chance = 25
    def __init__(self):
        super().__init__(400, 750, [ItemType.Valuables, ItemType.Loot, ItemType.Armor], male_noble_titles, male_names)
    
    def __str__(self):
        return "Noble"

class NobleWoman(Customer):
    rarity = 1.25
    haggle_chance = 0
    upcharge_reject_chance = 25
    def __init__(self):
        super().__init__(400, 750, [ItemType.Valuables, ItemType.Loot, ItemType.Armor], female_noble_titles, female_names)

    def __str__(self):
        return "Noble"

def get_customer():
    customer_types = Customer.__subclasses__()

    weights = []
    for customer in customer_types:
        weights.append(customer.rarity)

    choice = choices(customer_types, weights = weights, k = 1)[0]

    new_customer = choice()

    return new_customer

def profession_occurrence_test(trials):
    """
    generates customers and prints out their professions
    as a precentage. More trials means more accuracy
    """
    random_customers = {}

    for x in range(trials):
        c = get_customer(10)

        if str(c) not in random_customers:
            random_customers[str(c)] = 0
        random_customers[str(c)] += 1

    for c in random_customers:
        print(f"{c}: {random_customers[c]} ({(random_customers[c]/trials * 100):.1f}%)")

class DialogueType(Enum):
    sell = 1
    haggle_attempt = 2
    haggle_abandon = 3
    haggle_failure = 4
    upcharge_success = 5
    upcharge_failure = 6
    discount = 7
    buy = 8
    leave = 9

def get_dialogue(dialogue_type: DialogueType) -> str:
    """
    returns a random line of dialogue
    """
    if dialogue_type == DialogueType.sell:
        return choice(sell_dialogue)
    if dialogue_type == DialogueType.haggle_attempt:
        return choice(haggle_attempt_dialogue)
    if dialogue_type == DialogueType.haggle_abandon:
        return choice(haggle_abandon_dialogue)
    if dialogue_type == DialogueType.haggle_failure:
        return choice(haggle_failure_dialogue)
    if dialogue_type == DialogueType.upcharge_success:
        return choice(upcharge_success_dialogue)
    if dialogue_type == DialogueType.upcharge_failure:
        return choice(upcharge_failure_dialogue)
    if dialogue_type == DialogueType.discount:
        return choice(discount_dialogue)
    if dialogue_type == DialogueType.buy:
        return choice(buy_dialogue)
    if dialogue_type == DialogueType.leave:
        return choice(leave_dialogue)


if __name__ == '__main__':
    profession_occurrence_test(1000)

    # random_customer = get_customer()

    # print(f"{random_customer.name}, {random_customer.title} ({random_customer.budget} silver)")


    # for x in range(6):
    #     c = Peasant()
    #     print(f"{c.name}, {c.title}")
