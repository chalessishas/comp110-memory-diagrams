"""忍冬 — generated from ArknightsGameData char_4026_vulpis.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4026_vulpis
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_vulpis() -> UnitState:
    return UnitState(
        name='忍冬',
        faction=Faction.ALLY,
        max_hp=2180,
        atk=622,
        defence=380,
        res=0.0,
        atk_interval=1.05,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=14,
        redeploy_cd=70.0,
    )
