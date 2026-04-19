"""阿兰娜 — generated from ArknightsGameData char_4178_alanna.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4178_alanna
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_alanna() -> UnitState:
    return UnitState(
        name='阿兰娜',
        faction=Faction.ALLY,
        max_hp=2560,
        atk=610,
        defence=467,
        res=0.0,
        atk_interval=1.5,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=18,
        redeploy_cd=80.0,
    )
