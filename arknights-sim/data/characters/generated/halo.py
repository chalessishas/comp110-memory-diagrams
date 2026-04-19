"""星源 — generated from ArknightsGameData char_135_halo.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_135_halo
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_halo() -> UnitState:
    return UnitState(
        name='星源',
        faction=Faction.ALLY,
        max_hp=1440,
        atk=705,
        defence=122,
        res=20.0,
        atk_interval=2.3,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=34,
        redeploy_cd=80.0,
    )
