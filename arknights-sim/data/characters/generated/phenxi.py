"""菲亚梅塔 — generated from ArknightsGameData char_300_phenxi.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_300_phenxi
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_phenxi() -> UnitState:
    return UnitState(
        name='菲亚梅塔',
        faction=Faction.ALLY,
        max_hp=1926,
        atk=961,
        defence=156,
        res=0.0,
        atk_interval=2.8,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=29,
        redeploy_cd=70.0,
    )
