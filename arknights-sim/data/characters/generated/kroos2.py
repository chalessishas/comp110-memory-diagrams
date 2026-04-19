"""寒芒克洛丝 — generated from ArknightsGameData char_1021_kroos2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1021_kroos2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_kroos2() -> UnitState:
    return UnitState(
        name='寒芒克洛丝',
        faction=Faction.ALLY,
        max_hp=1520,
        atk=577,
        defence=176,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=15,
        redeploy_cd=80.0,
    )
