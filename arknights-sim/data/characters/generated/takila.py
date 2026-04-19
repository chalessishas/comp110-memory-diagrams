"""龙舌兰 — generated from ArknightsGameData char_486_takila.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_486_takila
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_takila() -> UnitState:
    return UnitState(
        name='龙舌兰',
        faction=Faction.ALLY,
        max_hp=3987,
        atk=352,
        defence=501,
        res=15.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=13,
        redeploy_cd=80.0,
    )
