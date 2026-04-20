"""Mayer (梅尔) — 5★ Supporter (Summoner archetype).

SUP_SUMMONER trait: Can deploy up to _TALENT_MAX_TOKENS mech-otter tokens.
  Tokens are independent units (physical ranged, block=1) that fight alongside Mayer.

Talent "Mechanical Mechanic": On deploy, summon 1 mech-otter token at Mayer's position.

S2 "EMP Pattern": MANUAL.
  ATK +_S2_ATK_RATIO for _S2_DURATION seconds.
  Also summons an additional mech-otter token.
  sp_cost=35, initial_sp=15, AUTO_TIME.

Mech-otter token stats (from char_4062_totter E2):
  HP=1550, ATK=970, DEF=145, RES=0, atk_interval=2.4s, block=1, PHYSICAL ranged.

Base stats from ArknightsGameData (E2 max, trust 100, char_242_otter):
  HP=1268, ATK=478, DEF=130, RES=20, atk_interval=1.6s, cost=11, block=1.
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape, TalentComponent,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.otter import make_otter as _base_stats


SUMMONER_RANGE = RangeShape(tiles=((1, 0), (2, 0), (3, 0), (1, -1), (1, 1), (2, -1), (2, 1)))
TOKEN_RANGE = RangeShape(tiles=((1, 0), (2, 0), (3, 0)))

_TALENT_TAG = "mayer_mechanical_mechanic"

_S2_TAG = "mayer_s2_emp_pattern"
_S2_ATK_RATIO = 0.40
_S2_ATK_BUFF_TAG = "mayer_s2_atk"
_S2_DURATION = 25.0

_TOKEN_HP = 1550
_TOKEN_ATK = 970
_TOKEN_DEF = 145
_TOKEN_NAME = "Mech-Otter"

_MAYER_TOKENS_ATTR = "_mayer_token_ids"
_MAYER_SUMMON_BUDGET = 4   # E2 max: talent(1) + up to 3 S2 fires


def _make_token(position: tuple) -> UnitState:
    t = UnitState(
        name=_TOKEN_NAME,
        faction=Faction.ALLY,
        max_hp=_TOKEN_HP,
        atk=_TOKEN_ATK,
        defence=_TOKEN_DEF,
        res=0.0,
        atk_interval=2.4,
        attack_range_melee=False,
        block=1,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
    )
    t.range_shape = TOKEN_RANGE
    t.deployed = True
    t.position = position
    return t


def _spawn_token(world, carrier: UnitState) -> None:
    if carrier.position is None:
        return
    remaining = getattr(carrier, "_summons_remaining", _MAYER_SUMMON_BUDGET)
    if remaining <= 0:
        world.log(f"Mayer summon budget exhausted ({_MAYER_SUMMON_BUDGET} total)")
        return
    setattr(carrier, "_summons_remaining", remaining - 1)
    token = _make_token(carrier.position)
    world.add_unit(token)
    ids = getattr(carrier, _MAYER_TOKENS_ATTR, [])
    ids.append(token.unit_id)
    setattr(carrier, _MAYER_TOKENS_ATTR, ids)


def _talent_on_battle_start(world, carrier: UnitState) -> None:
    if not carrier.deployed:
        return
    _spawn_token(world, carrier)


def _talent_on_death(world, carrier: UnitState) -> None:
    """When Mayer dies, despawn all her mech-otter tokens."""
    token_ids = getattr(carrier, _MAYER_TOKENS_ATTR, [])
    for unit in world.units:
        if unit.unit_id in token_ids and unit.alive:
            unit.alive = False
            unit.deployed = False


def _talent_on_retreat(world, carrier: UnitState) -> None:
    """Mayer retreats → despawn all mech-otter tokens."""
    _talent_on_death(world, carrier)


register_talent(_TALENT_TAG, on_battle_start=_talent_on_battle_start, on_death=_talent_on_death, on_retreat=_talent_on_retreat)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG,
    ))
    _spawn_token(world, carrier)


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_ATK_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_mayer(slot: str = "S2") -> UnitState:
    """Mayer E2 max. Talent: spawn 1 mech-otter token on deploy. S2: spawn extra token + ATK+40%."""
    op = _base_stats()
    op.name = "Mayer"
    op.archetype = RoleArchetype.SUP_SUMMONER
    op.profession = Profession.SUPPORTER
    op.attack_type = AttackType.ARTS
    op.attack_range_melee = False
    op.range_shape = SUMMONER_RANGE
    op.block = 1
    op.cost = 11

    op.talents = [TalentComponent(name="Mechanical Mechanic", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="EMP Pattern",
            slot="S2",
            sp_cost=35,
            initial_sp=15,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    return op
