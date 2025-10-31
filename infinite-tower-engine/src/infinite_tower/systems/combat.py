"""
Infinite Tower Engine - Combat System Module

Copyright (c) 2025 CosmicPhoenix171. All Rights Reserved.
"""

import random
from typing import Optional, List, Tuple
from enum import Enum


class DamageType(Enum):
    """Types of damage that can be dealt."""
    PHYSICAL = "physical"
    MAGICAL = "magical"
    FIRE = "fire"
    ICE = "ice"
    POISON = "poison"
    TRUE = "true"  # Ignores defense


class AttackResult:
    """Result of an attack with detailed information."""
    
    def __init__(self, damage: int, was_critical: bool = False, 
                 was_blocked: bool = False, damage_type: DamageType = DamageType.PHYSICAL):
        self.damage = damage
        self.was_critical = was_critical
        self.was_blocked = was_blocked
        self.damage_type = damage_type
        self.target_defeated = False


class CombatSystem:
    """
    Comprehensive combat system handling damage calculation, attacks, and effects.
    
    Features:
    - Melee and ranged combat
    - Critical hits
    - Defense and blocking
    - Status effects
    - Damage types
    """
    
    def __init__(self):
        self.damage_multiplier = 1.0
        self.critical_chance = 0.15  # 15% base crit chance
        self.critical_multiplier = 1.5
        self.active_effects = {}  # entity_id: [effects]
    
    def calculate_damage(self, base_damage: int, defender_defense: int,
                        damage_type: DamageType = DamageType.PHYSICAL,
                        attacker_power: float = 1.0) -> int:
        """
        Calculate effective damage after defense and modifiers.
        
        Args:
            base_damage: Base damage value
            defender_defense: Target's defense stat
            damage_type: Type of damage being dealt
            attacker_power: Attacker's power multiplier
            
        Returns:
            Final damage value
        """
        # True damage ignores defense
        if damage_type == DamageType.TRUE:
            return int(base_damage * attacker_power * self.damage_multiplier)
        
        # Apply defense reduction
        damage_reduction = defender_defense * 0.5  # Defense reduces damage by 50% of its value
        effective_damage = base_damage * attacker_power * self.damage_multiplier - damage_reduction
        
        # Minimum 1 damage if attack hits
        return max(1, int(effective_damage))
    
    def check_critical_hit(self, attacker) -> bool:
        """
        Check if an attack is a critical hit.
        
        Args:
            attacker: Attacking entity (can have crit_chance attribute)
            
        Returns:
            True if attack is critical
        """
        crit_chance = getattr(attacker, 'crit_chance', self.critical_chance)
        return random.random() < crit_chance
    
    def check_block(self, defender) -> bool:
        """
        Check if an attack is blocked.
        
        Args:
            defender: Defending entity (can have block_chance attribute)
            
        Returns:
            True if attack is blocked
        """
        block_chance = getattr(defender, 'block_chance', 0.0)
        return random.random() < block_chance
    
    def perform_attack(self, attacker, defender, 
                      damage_type: DamageType = DamageType.PHYSICAL) -> AttackResult:
        """
        Perform a complete attack with all combat mechanics.
        
        Args:
            attacker: Attacking entity
            defender: Defending entity
            damage_type: Type of damage
            
        Returns:
            AttackResult with combat details
        """
        # Get base damage
        base_damage = getattr(attacker, 'attack_power', 10)
        defender_defense = getattr(defender, 'defense', 0)
        
        # Check for critical hit
        is_critical = self.check_critical_hit(attacker)
        if is_critical:
            base_damage = int(base_damage * self.critical_multiplier)
        
        # Check for block
        is_blocked = self.check_block(defender)
        if is_blocked:
            base_damage = int(base_damage * 0.5)  # 50% damage on block
        
        # Calculate final damage
        damage = self.calculate_damage(base_damage, defender_defense, damage_type)
        
        # Apply damage
        defender.health -= damage
        
        # Create result
        result = AttackResult(damage, is_critical, is_blocked, damage_type)
        result.target_defeated = defender.health <= 0
        
        return result
    
    def perform_melee_attack(self, attacker, defender) -> AttackResult:
        """
        Perform a melee attack (close range).
        
        Args:
            attacker: Attacking entity
            defender: Defending entity
            
        Returns:
            AttackResult
        """
        return self.perform_attack(attacker, defender, DamageType.PHYSICAL)
    
    def perform_ranged_attack(self, attacker, defender, distance: float) -> Optional[AttackResult]:
        """
        Perform a ranged attack with distance falloff.
        
        Args:
            attacker: Attacking entity
            defender: Defending entity
            distance: Distance between entities
            
        Returns:
            AttackResult or None if out of range
        """
        max_range = getattr(attacker, 'attack_range', 200)
        
        if distance > max_range:
            return None
        
        # Damage falloff with distance
        range_multiplier = 1.0 - (distance / max_range) * 0.3  # Up to 30% damage reduction
        attacker.attack_power = int(attacker.attack_power * range_multiplier)
        
        result = self.perform_attack(attacker, defender, DamageType.PHYSICAL)
        
        # Restore attack power
        attacker.attack_power = int(attacker.attack_power / range_multiplier)
        
        return result
    
    def apply_area_damage(self, attacker, targets: List, radius: float, 
                         center: Tuple[float, float]) -> List[AttackResult]:
        """
        Apply area of effect damage to multiple targets.
        
        Args:
            attacker: Attacking entity
            targets: List of potential targets
            radius: Effect radius
            center: (x, y) center of effect
            
        Returns:
            List of AttackResults for each hit target
        """
        results = []
        
        for target in targets:
            if not hasattr(target, 'position') or not hasattr(target, 'health'):
                continue
            
            # Check if target is in radius
            target_pos = target.position if isinstance(target.position, tuple) else tuple(target.position)
            dx = target_pos[0] - center[0]
            dy = target_pos[1] - center[1]
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance <= radius:
                # Reduced damage based on distance from center
                distance_multiplier = 1.0 - (distance / radius) * 0.5
                original_power = attacker.attack_power
                attacker.attack_power = int(original_power * distance_multiplier)
                
                result = self.perform_attack(attacker, target)
                results.append(result)
                
                # Restore attack power
                attacker.attack_power = original_power
        
        return results
    
    def is_enemy_defeated(self, enemy) -> bool:
        """
        Check if an enemy is defeated.
        
        Args:
            enemy: Enemy entity
            
        Returns:
            True if enemy health is 0 or below
        """
        return enemy.health <= 0
    
    def apply_damage_over_time(self, target, damage_per_tick: int, 
                              duration_ticks: int, tick_rate: int = 60) -> dict:
        """
        Apply damage over time effect.
        
        Args:
            target: Target entity
            damage_per_tick: Damage per tick
            duration_ticks: Total number of ticks
            tick_rate: Ticks per second
            
        Returns:
            Effect dictionary
        """
        effect = {
            'type': 'damage_over_time',
            'damage_per_tick': damage_per_tick,
            'remaining_ticks': duration_ticks,
            'tick_rate': tick_rate,
            'current_tick': 0
        }
        
        target_id = id(target)
        if target_id not in self.active_effects:
            self.active_effects[target_id] = []
        self.active_effects[target_id].append(effect)
        
        return effect
    
    def apply_heal_over_time(self, target, heal_per_tick: int, duration_ticks: int) -> dict:
        """
        Apply healing over time effect.
        
        Args:
            target: Target entity
            heal_per_tick: Healing per tick
            duration_ticks: Total number of ticks
            
        Returns:
            Effect dictionary
        """
        effect = {
            'type': 'heal_over_time',
            'heal_per_tick': heal_per_tick,
            'remaining_ticks': duration_ticks,
            'current_tick': 0
        }
        
        target_id = id(target)
        if target_id not in self.active_effects:
            self.active_effects[target_id] = []
        self.active_effects[target_id].append(effect)
        
        return effect
    
    def update_effects(self, entities: List) -> None:
        """
        Update all active combat effects.
        
        Args:
            entities: List of entities to update
        """
        for entity in entities:
            entity_id = id(entity)
            
            if entity_id not in self.active_effects:
                continue
            
            effects_to_remove = []
            
            for effect in self.active_effects[entity_id]:
                effect['current_tick'] += 1
                
                # Apply effect based on type
                if effect['type'] == 'damage_over_time':
                    if effect['current_tick'] % effect['tick_rate'] == 0:
                        entity.health -= effect['damage_per_tick']
                        effect['remaining_ticks'] -= 1
                
                elif effect['type'] == 'heal_over_time':
                    entity.health += effect['heal_per_tick']
                    effect['remaining_ticks'] -= 1
                
                # Remove expired effects
                if effect['remaining_ticks'] <= 0:
                    effects_to_remove.append(effect)
            
            # Clean up expired effects
            for effect in effects_to_remove:
                self.active_effects[entity_id].remove(effect)
            
            # Remove entity from active_effects if no effects remain
            if not self.active_effects[entity_id]:
                del self.active_effects[entity_id]
    
    def heal(self, target, heal_amount: int) -> int:
        """
        Heal a target entity.
        
        Args:
            target: Target entity
            heal_amount: Amount to heal
            
        Returns:
            Actual amount healed (capped by max health)
        """
        if not hasattr(target, 'health') or not hasattr(target, 'max_health'):
            return 0
        
        old_health = target.health
        target.health = min(target.max_health, target.health + heal_amount)
        actual_heal = target.health - old_health
        
        return actual_heal
    
    def get_combat_stats(self, entity) -> dict:
        """
        Get combat-relevant stats for an entity.
        
        Args:
            entity: Entity to get stats for
            
        Returns:
            Dictionary of combat stats
        """
        return {
            'health': getattr(entity, 'health', 0),
            'max_health': getattr(entity, 'max_health', 100),
            'attack_power': getattr(entity, 'attack_power', 10),
            'defense': getattr(entity, 'defense', 0),
            'crit_chance': getattr(entity, 'crit_chance', self.critical_chance),
            'block_chance': getattr(entity, 'block_chance', 0.0),
            'active_effects': len(self.active_effects.get(id(entity), []))
        }