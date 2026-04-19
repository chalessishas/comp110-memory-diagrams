"""贝娜 — generated from ArknightsGameData char_369_bena.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_369_bena
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_bena() -> UnitState:
    return UnitState(
        name='贝娜',
        faction=Faction.ALLY,
        max_hp=2535,
        atk=742,
        defence=315,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=17,
        redeploy_cd=80.0,
    )
