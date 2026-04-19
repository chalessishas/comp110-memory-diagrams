"""Liskarm — 5* Defender (Sentinel archetype).

SOURCE: PRTS wiki, E2 L90, 信赖 100, no potentials, no module.
VERIFY: replace with akgd values next iteration.

Sentinel special: electric arc damage to attacker on being hit (talent).
TODO: implement the reflective damage via a hit_received event hook once
event_queue supports damage events.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape
from core.types import (
    AttackType, Faction, Profession, RoleArchetype,
)


DEFENDER_MELEE_1 = RangeShape(tiles=((0, 0),))


def make_liskarm() -> UnitState:
    return UnitState(
        name="Liskarm",
        faction=Faction.ALLY,
        max_hp=2200,
        atk=495,
        defence=431,
        res=20.0,
        atk_interval=1.2,
        profession=Profession.DEFENDER,
        archetype=RoleArchetype.DEF_SENTINEL,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=True,
        block=1,
        range_shape=DEFENDER_MELEE_1,
        cost=21,
        redeploy_cd=70.0,
    )
