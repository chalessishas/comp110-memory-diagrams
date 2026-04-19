"""魔王 — generated from ArknightsGameData char_4134_cetsyr.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4134_cetsyr
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_cetsyr() -> UnitState:
    return UnitState(
        name='魔王',
        faction=Faction.ALLY,
        max_hp=1928,
        atk=399,
        defence=236,
        res=0.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=10,
        redeploy_cd=80.0,
    )
