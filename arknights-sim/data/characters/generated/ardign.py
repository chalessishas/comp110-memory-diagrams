"""卡缇 — generated from ArknightsGameData char_209_ardign.
Source: E1 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_209_ardign
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_ardign() -> UnitState:
    return UnitState(
        name='卡缇',
        faction=Faction.ALLY,
        max_hp=2430,
        atk=305,
        defence=475,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=18,
        redeploy_cd=70.0,
    )
