"""Ch'en — 6* Guard (Lord archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
S2 "Sheathed Strike": MANUAL instant — deals 380% ATK arts damage to all enemies in range.
sp_cost=20, initial_sp=10.
"""
from __future__ import annotations
from math import floor
from core.state.unit_state import UnitState, SkillComponent, RangeShape, TalentComponent
from core.types import (
    AttackType, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill, manual_trigger
from core.systems.talent_registry import register_talent
from data.characters.generated.chen import make_chen as _base_stats


# --- Talent: Swordsman ---
_TALENT_TAG = "chen_swordsman"
_SWORD_SPAWNED_ATTR = "_chen_sword_spawned"
_SWORD_NAME = "Heartless Act"
_SWORD_HP = 1500
_SWORD_ATK = 600
_SWORD_DEF = 200


def _make_sword(position: tuple) -> UnitState:
    t = UnitState(
        name=_SWORD_NAME,
        faction=Faction.ALLY,
        max_hp=_SWORD_HP, hp=_SWORD_HP,
        atk=_SWORD_ATK, defence=_SWORD_DEF, res=0.0,
        atk_interval=1.3,
        attack_range_melee=True,
        block=2,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
    )
    t.range_shape = RangeShape(tiles=((0, 0), (1, 0)))
    t.deployed = True
    t.position = position
    return t


def _swordsman_on_kill(world, killer: UnitState, victim) -> None:
    if getattr(killer, _SWORD_SPAWNED_ATTR, False):
        return   # only first kill triggers
    if killer.position is None:
        return
    setattr(killer, _SWORD_SPAWNED_ATTR, True)
    world.add_unit(_make_sword(killer.position))
    world.log(f"Ch'en Swordsman — Heartless Act summoned at {killer.position}")


register_talent(_TALENT_TAG, on_kill=_swordsman_on_kill)


LORD_RANGE = RangeShape(tiles=((0, 0), (1, 0), (2, 0)))

_S2_TAG = "chen_s2_sheathed_strike"
_S2_ATK_MULTIPLIER = 3.80   # 380% ATK at M3


def _s2_on_start(world, carrier: UnitState) -> None:
    """Instant arts burst to all enemies in range."""
    if carrier.position is None:
        return
    ox, oy = carrier.position
    tiles = set(carrier.range_shape.tiles)
    burst_atk = int(floor(carrier.effective_atk * _S2_ATK_MULTIPLIER))
    for enemy in world.enemies():
        if not enemy.alive or enemy.position is None:
            continue
        dx = round(enemy.position[0]) - round(ox)
        dy = round(enemy.position[1]) - round(oy)
        if (dx, dy) not in tiles:
            continue
        dealt = enemy.take_arts(burst_atk)
        world.global_state.total_damage_dealt += dealt
        world.log(
            f"Ch'en S2 → {enemy.name}  dmg={dealt}  ({enemy.hp}/{enemy.max_hp})"
        )


register_skill(_S2_TAG, on_start=_s2_on_start)


def make_chen(slot: str = "S2") -> UnitState:
    """Ch'en E2 max, trust 100. S2 Sheathed Strike wired (MANUAL)."""
    op = _base_stats()
    op.name = "Ch'en"
    op.archetype = RoleArchetype.GUARD_LORD
    op.range_shape = LORD_RANGE
    op.cost = 23
    op.talents = [TalentComponent(name="Swordsman", behavior_tag=_TALENT_TAG)]
    if slot == "S2":
        op.skill = SkillComponent(
            name="Sheathed Strike",
            slot="S2",
            sp_cost=20,
            initial_sp=10,
            duration=0.0,   # instant
            sp_gain_mode=SPGainMode.AUTO_ATTACK,   # charges on hit
            trigger=SkillTrigger.MANUAL,
            behavior_tag=_S2_TAG,
        )
    return op
