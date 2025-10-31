"""
Infinite Tower Engine - Loot System Module

Copyright (c) 2025 CosmicPhoenix171. All Rights Reserved.
"""

import random
import pygame
from enum import Enum
from typing import Optional, Dict, Tuple


class Rarity(Enum):
    """Item rarity levels."""
    COMMON = ("common", (200, 200, 200), 0.50)      # Gray, 50% drop chance
    UNCOMMON = ("uncommon", (100, 255, 100), 0.25)  # Green, 25%
    RARE = ("rare", (100, 100, 255), 0.15)          # Blue, 15%
    EPIC = ("epic", (200, 100, 255), 0.08)          # Purple, 8%
    LEGENDARY = ("legendary", (255, 150, 0), 0.02)  # Orange, 2%
    
    def __init__(self, name: str, color: Tuple[int, int, int], drop_chance: float):
        self.rarity_name = name
        self.color = color
        self.drop_chance = drop_chance


class ItemType(Enum):
    """Types of items."""
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    KEY_ITEM = "key_item"


class Item:
    """
    Base item class for all loot.
    
    Attributes:
        name: Item name
        item_type: Type of item
        rarity: Rarity level
        stackable: Can this item stack
        quantity: Current stack quantity
        value: Gold/sell value
        stats: Dictionary of stat modifiers
        description: Item description
    """
    
    def __init__(self, name: str, item_type: ItemType, rarity: Rarity,
                 stackable: bool = False, max_stack: int = 99, value: int = 10):
        self.name = name
        self.item_type = item_type
        self.rarity = rarity
        self.stackable = stackable
        self.max_stack = max_stack if stackable else 1
        self.quantity = 1
        self.value = value
        self.stats = {}
        self.description = ""
        self.level_requirement = 1
        
        # Position in world (if dropped)
        self.position = None
        self.rect = None
    
    def can_stack_with(self, other: 'Item') -> bool:
        """
        Check if this item can stack with another.
        
        Args:
            other: Other item to check
            
        Returns:
            True if items can stack
        """
        return (self.stackable and 
                other.stackable and
                self.name == other.name and
                self.item_type == other.item_type and
                self.rarity == other.rarity)
    
    def stack(self, amount: int = 1) -> int:
        """
        Add to item stack.
        
        Args:
            amount: Amount to add
            
        Returns:
            Overflow amount (if stack is full)
        """
        if not self.stackable:
            return amount
        
        total = self.quantity + amount
        if total <= self.max_stack:
            self.quantity = total
            return 0
        else:
            self.quantity = self.max_stack
            return total - self.max_stack
    
    def split(self, amount: int) -> Optional['Item']:
        """
        Split a stack into two.
        
        Args:
            amount: Amount to split off
            
        Returns:
            New item with split amount, or None
        """
        if not self.stackable or amount >= self.quantity:
            return None
        
        self.quantity -= amount
        new_item = Item(self.name, self.item_type, self.rarity, 
                       self.stackable, self.max_stack, self.value)
        new_item.quantity = amount
        new_item.stats = self.stats.copy()
        new_item.description = self.description
        
        return new_item
    
    def set_position(self, x: float, y: float):
        """
        Set item position in world for rendering.
        
        Args:
            x, y: World coordinates
        """
        self.position = (x, y)
        self.rect = pygame.Rect(int(x) - 8, int(y) - 8, 16, 16)
    
    def draw(self, surface: pygame.Surface):
        """
        Draw item in world.
        
        Args:
            surface: Pygame surface
        """
        if self.position and self.rect:
            # Draw item as colored square (will be replaced with sprites)
            pygame.draw.rect(surface, self.rarity.color, self.rect)
            pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
    
    def __str__(self):
        stack_info = f"x{self.quantity}" if self.stackable else ""
        return f"{self.name} ({self.rarity.rarity_name}) {stack_info}"


class Weapon(Item):
    """Weapon item with attack stats."""
    
    def __init__(self, name: str, rarity: Rarity, damage: int, 
                 attack_speed: float = 1.0, value: int = 50):
        super().__init__(name, ItemType.WEAPON, rarity, stackable=False, value=value)
        self.stats['damage'] = damage
        self.stats['attack_speed'] = attack_speed
        self.description = f"Weapon: {damage} damage, {attack_speed}x speed"


class Armor(Item):
    """Armor item with defense stats."""
    
    def __init__(self, name: str, rarity: Rarity, defense: int, value: int = 40):
        super().__init__(name, ItemType.ARMOR, rarity, stackable=False, value=value)
        self.stats['defense'] = defense
        self.description = f"Armor: +{defense} defense"


class Consumable(Item):
    """Consumable item with effects."""
    
    def __init__(self, name: str, rarity: Rarity, effect: str, 
                 effect_value: int, max_stack: int = 99, value: int = 20):
        super().__init__(name, ItemType.CONSUMABLE, rarity, 
                        stackable=True, max_stack=max_stack, value=value)
        self.stats['effect'] = effect
        self.stats['effect_value'] = effect_value
        self.description = f"{effect.capitalize()}: {effect_value}"
    
    def use(self, target) -> bool:
        """
        Use consumable on target.
        
        Args:
            target: Entity to apply effect to
            
        Returns:
            True if successfully used
        """
        effect = self.stats.get('effect')
        value = self.stats.get('effect_value', 0)
        
        if effect == 'heal' and hasattr(target, 'heal'):
            target.heal(value)
        elif effect == 'mana' and hasattr(target, 'mana'):
            target.mana = min(target.max_mana, target.mana + value)
        elif effect == 'buff':
            # Apply temporary stat buff
            pass
        
        self.quantity -= 1
        return True


class LootGenerator:
    """
    System for generating random loot based on rarity and level.
    """
    
    def __init__(self, seed: Optional[int] = None):
        if seed:
            random.seed(seed)
        
        # Loot tables
        self.weapon_names = [
            "Sword", "Axe", "Dagger", "Mace", "Spear", "Bow", 
            "Staff", "Wand", "Hammer", "Scythe"
        ]
        self.armor_names = [
            "Helmet", "Chestplate", "Leggings", "Boots", 
            "Shield", "Gauntlets", "Cape", "Belt"
        ]
        self.consumable_names = [
            ("Health Potion", "heal", 50),
            ("Mana Potion", "mana", 30),
            ("Stamina Potion", "stamina", 40),
            ("Antidote", "cure_poison", 1),
        ]
        self.material_names = [
            "Iron Ore", "Gold Nugget", "Crystal Shard", "Leather", 
            "Wood", "Stone", "Gem Fragment"
        ]
    
    def generate_random_item(self, floor_level: int = 1) -> Item:
        """
        Generate a random item based on floor level.
        
        Args:
            floor_level: Current floor number (affects rarity chance)
            
        Returns:
            Generated item
        """
        # Determine rarity (higher floor = better rarity chance)
        rarity = self._roll_rarity(floor_level)
        
        # Determine item type
        item_type = random.choice(list(ItemType))
        
        # Generate specific item
        if item_type == ItemType.WEAPON:
            return self._generate_weapon(rarity, floor_level)
        elif item_type == ItemType.ARMOR:
            return self._generate_armor(rarity, floor_level)
        elif item_type == ItemType.CONSUMABLE:
            return self._generate_consumable(rarity)
        else:
            return self._generate_material(rarity)
    
    def _roll_rarity(self, floor_level: int) -> Rarity:
        """
        Roll for item rarity based on floor level.
        
        Args:
            floor_level: Current floor
            
        Returns:
            Rarity enum
        """
        # Increase rarity chances with floor level
        luck_modifier = min(floor_level * 0.01, 0.3)  # Max 30% boost
        roll = random.random()
        
        cumulative = 0.0
        for rarity in reversed(list(Rarity)):  # Check legendary first
            cumulative += rarity.drop_chance + luck_modifier
            if roll < cumulative:
                return rarity
        
        return Rarity.COMMON
    
    def _generate_weapon(self, rarity: Rarity, floor_level: int) -> Weapon:
        """Generate a weapon."""
        name = random.choice(self.weapon_names)
        prefix = self._get_rarity_prefix(rarity)
        full_name = f"{prefix} {name}"
        
        base_damage = 10 + floor_level * 2
        rarity_multiplier = {
            Rarity.COMMON: 1.0,
            Rarity.UNCOMMON: 1.2,
            Rarity.RARE: 1.5,
            Rarity.EPIC: 2.0,
            Rarity.LEGENDARY: 3.0
        }
        
        damage = int(base_damage * rarity_multiplier[rarity])
        value = damage * 5
        
        return Weapon(full_name, rarity, damage, value=value)
    
    def _generate_armor(self, rarity: Rarity, floor_level: int) -> Armor:
        """Generate armor."""
        name = random.choice(self.armor_names)
        prefix = self._get_rarity_prefix(rarity)
        full_name = f"{prefix} {name}"
        
        base_defense = 5 + floor_level
        rarity_multiplier = {
            Rarity.COMMON: 1.0,
            Rarity.UNCOMMON: 1.3,
            Rarity.RARE: 1.7,
            Rarity.EPIC: 2.2,
            Rarity.LEGENDARY: 3.5
        }
        
        defense = int(base_defense * rarity_multiplier[rarity])
        value = defense * 8
        
        return Armor(full_name, rarity, defense, value=value)
    
    def _generate_consumable(self, rarity: Rarity) -> Consumable:
        """Generate a consumable."""
        name, effect, base_value = random.choice(self.consumable_names)
        
        rarity_multiplier = {
            Rarity.COMMON: 1.0,
            Rarity.UNCOMMON: 1.5,
            Rarity.RARE: 2.0,
            Rarity.EPIC: 3.0,
            Rarity.LEGENDARY: 5.0
        }
        
        effect_value = int(base_value * rarity_multiplier[rarity])
        value = effect_value
        
        return Consumable(name, rarity, effect, effect_value, value=value)
    
    def _generate_material(self, rarity: Rarity) -> Item:
        """Generate a material item."""
        name = random.choice(self.material_names)
        item = Item(name, ItemType.MATERIAL, rarity, stackable=True, max_stack=999, value=5)
        item.quantity = random.randint(1, 10)
        return item
    
    def _get_rarity_prefix(self, rarity: Rarity) -> str:
        """Get a name prefix based on rarity."""
        prefixes = {
            Rarity.COMMON: "",
            Rarity.UNCOMMON: "Fine",
            Rarity.RARE: "Superior",
            Rarity.EPIC: "Masterwork",
            Rarity.LEGENDARY: "Legendary"
        }
        return prefixes[rarity]
    
    def generate_loot_drop(self, floor_level: int, enemy_type: str = "basic") -> list:
        """
        Generate loot drops for an enemy.
        
        Args:
            floor_level: Current floor level
            enemy_type: Type of enemy (affects quantity/quality)
            
        Returns:
            List of items
        """
        drops = []
        
        # Boss enemies drop more/better loot
        if enemy_type == "boss":
            num_drops = random.randint(3, 6)
            floor_level = floor_level + 5  # Better quality
        else:
            drop_chance = 0.3
            if random.random() > drop_chance:
                return drops
            num_drops = random.randint(1, 2)
        
        for _ in range(num_drops):
            item = self.generate_random_item(floor_level)
            drops.append(item)
        
        return drops


class Loot(Item):
    """Legacy Loot class for backward compatibility."""
    
    def __init__(self, name: str, rarity: Rarity, stackable: bool = True):
        item_type = ItemType.MATERIAL if stackable else ItemType.WEAPON
        super().__init__(name, item_type, rarity, stackable)
    
    def generate_loot(self):
        """Legacy method - use LootGenerator instead."""
        pass