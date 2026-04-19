"""乌啾 — generated from ArknightsGameData char_4224_turdus.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4224_turdus
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_turdus() -> UnitState:
    return UnitState(
        name='乌啾',
        faction=Faction.ALLY,
        max_hp=1830,
        atk=495,
        defence=175,
        res=0.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=18,
        redeploy_cd=70.0,
    )
