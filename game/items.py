"""
A container of items
"""

from enum import Enum     
from random import choice

items = []

class ItemType(Enum):
    Valuables = 1
    Materials = 2
    Armor = 3
    Weapons = 4
    Tools = 5
    Supplies = 6
    Loot = 7
    Consumables = 8
    Common = 9


class Item:
    """
    The bread and butter of the game, buy and sell
    """
    def __init__(self, name, price, item_type: ItemType):
        self.name = name
        self.price = price
        items.append(self)
        self.item_type = item_type

    def __str__(self):
        return self.name

class Storage:
    """
    Storages hold items.
    """
    
    # stored_types is a list of ItemTypes
    def __init__(self, max_storage: int, stored_types, name: str, upgrade_step:int):
        self.max_storage = max_storage
        # how much is added per shop level
        self.upgrade_step = upgrade_step
        # Item and amount (INT)
        self.held_items = {}
        self.stored_types = stored_types
        self.name = name

    def get_all_valid_items(self) -> dict:
        """
        returns a dictionary of valid items
        key: item type value: list of items
        """

        to_return = {}
        for type in self.stored_types:
            to_return[type] = get_items_of_type(type)

        return to_return

    def get_status(self) -> int:
        """
        returns amount of items in storage
        """
        return sum(self.held_items.values())

    def add_items(self, item: Item, amount: int) -> bool:
        """
        Adds items to the storage. Returns true if succeeded, returns false is not
        """
        
        if self.item_validity_check(item, amount):
            # item is valid, so add
            if item not in self.held_items:
                self.held_items[item] = amount
            else: 
                self.held_items[item] += amount
            return True
        else: return False
    
    def item_validity_check(self, item: Item, amount: int) -> bool:
        """
        Checks to see if the item can fit in storage.
        Checks availible space, and makes sure item type fits
        """
        # Check if item is compatible with storage
        if(item.item_type not in self.stored_types):
            return False
        # Check if you have room for the item in this storage
        elif int(amount) + self.get_status() > self.max_storage:
            return False 
        # All checks passed, item is valid
        return True   

    def remove_items(self, item: Item, quantity) -> bool:
        # Check if item is in storage
        if item in self.held_items:
            # check if there are enough items
            if self.held_items[item] >= quantity:
                self.held_items[item] -= quantity
                # if all of the item has been removed clear it from 
                # the dictionary
                if self.held_items[item] == 0:
                    del self.held_items[item]
                return True
        return False
    
    def list_items(self):
        for item in self.held_items:
            print(f"{item} - {self.held_items[item]}")
    
    def __str__(self):
        return self.name

# Common goods - bread and butter early game stock for peasants
firewood = Item("Firewood", 6, ItemType.Common)
cook_pot = Item("Cooking Pot", 15, ItemType.Common)
candle = Item("Candle", 9, ItemType.Common)
ale = Item("Ale", 8, ItemType.Common)
herbal = Item("Herbal Remedy", 10, ItemType.Common)
shoes = Item("Simple shoes", 12, ItemType.Common)

# Crafting Materials - Mid game bulk for aritsans
leather = Item("Leather", 15, ItemType.Materials)
clay = Item("Clay", 12, ItemType.Materials)
iron = Item("Iron", 20, ItemType.Materials)
charcoal = Item("Charcoal", 10, ItemType.Materials)
cloth = Item("Cloth", 18, ItemType.Materials)

# Supplies - Bulk adventurer items
rope = Item("Rope", 10, ItemType.Supplies)
compass = Item("Compass", 30, ItemType.Supplies)
flask = Item("Flask", 20, ItemType.Supplies)
torch = Item("Torch", 15, ItemType.Supplies)

# Consumables - mid-tier adventurer items
healing_potion = Item("Healing Potion", 50, ItemType.Consumables)
teleport_scroll = Item("Teleport scroll", 125, ItemType.Consumables)
mana_crystal = Item("Mana crystal", 35, ItemType.Consumables)

# Weapons - 
sword = Item("Sword", 120, ItemType.Weapons)
shield = Item("Shield", 85, ItemType.Weapons)
magic_staff = Item("Magic Staff", 160, ItemType.Weapons)
bow = Item("Bow", 100, ItemType.Weapons)

# Valuables
gemstones = Item("Gemstones", 120, ItemType.Valuables)
jewlery = Item("Jewlery", 175, ItemType.Valuables)
gold = Item("Gold", 90, ItemType.Valuables)
enchanted_ring = Item("Enchanted Ring", 300, ItemType.Valuables)

# Monster loot
feather = Item("Harpy feather", 60, ItemType.Loot)
slime = Item("Slime chunk", 20, ItemType.Loot)
fur = Item("Heavy fur", 40, ItemType.Loot)
wing = Item("Delicate wing", 30, ItemType.Loot)


# Armor - high tier items for adventurers and nobles
leather_armor = Item("Leather Armor", 75, ItemType.Armor)
mage_robes = Item("Mage Robes", 130, ItemType.Armor)
plate_armor = Item("Plate Armor", 220, ItemType.Armor)
chainmail = Item("Chainmail Armor", 125, ItemType.Armor)

# Tools - mid tier items for peasants and artisans
spade = Item("Spade", 30, ItemType.Tools)
hammer = Item("Hammer", 25, ItemType.Tools)
pitchfork = Item("Pitchfork", 50, ItemType.Tools)
saw = Item("Saw", 35, ItemType.Tools)
sickle = Item("Sickle", 40, ItemType.Tools)

def get_items_of_type(type: ItemType):
    toReturn = []
    for item in items:
        if item.item_type == type:
            toReturn.append(item)
    return toReturn

def random_valid_item(price, itemtype: ItemType):
    """
    returns a random valid item of the type and within the price
    """
    random_items = []
    for item in get_items_of_type(itemtype):
        if(item.price <= price):
            random_items.append(item)
    
    if len(random_items) == 0:
        return None

    return choice(random_items)

