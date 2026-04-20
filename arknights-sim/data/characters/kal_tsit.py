"""Kal'tsit (凯尔希) — 6★ Medic (SUP_SUMMONER archetype) + Mon3tr summon.

Talent "Mon3tr": Kal'tsit is always accompanied by Mon3tr, a powerful summon that
  deploys alongside her at battle start. Mon3tr vanishes if Kal'tsit dies or retreats.

Mon3tr talent "Non-Damaging Restructuring":
  On Mon3tr's death: deals _MON3TR_TRUE_DAMAGE True damage and applies _MON3TR_STUN_DURATION
  seconds of Stun to all enemies within Chebyshev distance 1 (the 8 surrounding tiles).

S3 "All-Out": ATK +80% for 40s, sp_cost=40, initial_sp=20, AUTO trigger.

Base stats from ArknightsGameData (E2 max, trust 100, char_003_kalts):
  HP=2033, ATK=490, DEF=255, RES=0, atk_interval=2.85, block=1.

Mon3tr stats (approximate, char_4013_mon3tr E2 max):
  HP=8000, ATK=1200, DEF=400, RES=0, atk_interval=2.0, block=2.
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape, TalentComponent, StatusEffect,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode, StatusKind,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.kalts import make_kalts as _base_stats


KAL_TSIT_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 3) for dy in range(-1, 2)
))
MON3TR_RANGE = RangeShape(tiles=((0, 0), (1, 0), (2, 0)))

_KAL_TSIT_TALENT_TAG = "kal_tsit_companion"
_MON3TR_TALENT_TAG = "mon3tr_non_damaging_restructuring"

_MON3TR_HP = 8000
_MON3TR_ATK = 1200
_MON3TR_DEF = 400
_MON3TR_TRUE_DAMAGE = 700     # true damage per enemy on Mon3tr's death
_MON3TR_STUN_DURATION = 3.0  # seconds
_MON3TR_BURST_TAG = "mon3tr_death_burst"

_S3_TAG = "kal_tsit_s3_all_out"
_S3_ATK_RATIO = 0.80
_S3_ATK_BUFF_TAG = "kal_tsit_s3_atk"
_S3_DURATION = 40.0


# ---------------------------------------------------------------------------
# Mon3tr unit + its own talent (death burst)
# ---------------------------------------------------------------------------

def _mon3tr_on_death(world, unit: UnitState) -> None:
    """Mon3tr dies → True damage + Stun to all enemies in surrounding 8 tiles."""
    if unit.position is None:
        return
    mx, my = unit.position
    now = world.global_state.elapsed
    for e in world.enemies():
        if not e.alive or e.position is None:
            continue
        ex, ey = e.position
        # Chebyshev distance ≤ 1 = 3×3 grid surrounding Mon3tr
        if max(abs(round(ex) - round(mx)), abs(round(ey) - round(my))) <= 1:
            dmg = e.take_true(_MON3TR_TRUE_DAMAGE)
            world.global_state.total_damage_dealt += dmg
            e.statuses.append(StatusEffect(
                kind=StatusKind.STUN,
                source_tag=_MON3TR_BURST_TAG,
                expires_at=now + _MON3TR_STUN_DURATION,
            ))
            world.log(
                f"Mon3tr death burst → {e.name}  "
                f"true_dmg={dmg}  stun={_MON3TR_STUN_DURATION}s"
            )


register_talent(_MON3TR_TALENT_TAG, on_death=_mon3tr_on_death)


def _make_mon3tr(position: tuple[float, float]) -> UnitState:
    """Mon3tr summon — heavy melee ally. Carries its death-burst talent."""
    mon3tr = UnitState(
        name="Mon3tr",
        faction=Faction.ALLY,
        max_hp=_MON3TR_HP,
        hp=_MON3TR_HP,
        atk=_MON3TR_ATK,
        defence=_MON3TR_DEF,
        res=0.0,
        atk_interval=2.0,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=True,
        range_shape=MON3TR_RANGE,
        block=2,
        cost=0,
        deployed=True,
        position=position,
    )
    mon3tr.talents = [TalentComponent(name="Non-Damaging Restructuring", behavior_tag=_MON3TR_TALENT_TAG)]
    return mon3tr


# ---------------------------------------------------------------------------
# Kal'tsit's talent — Mon3tr lifecycle
# ---------------------------------------------------------------------------

def _despawn_mon3tr(world, carrier: UnitState) -> None:
    mon3tr_id = getattr(carrier, "_kal_tsit_mon3tr_id", None)
    if mon3tr_id is not None:
        unit = world.unit_by_id(mon3tr_id)
        if unit is not None and unit.alive:
            unit.alive = False
            unit.hp = 0
            unit.deployed = False
    carrier._kal_tsit_mon3tr_id = None


def _kal_tsit_on_battle_start(world, carrier: UnitState) -> None:
    pos = carrier.position if carrier.position is not None else (0.0, 0.0)
    mon3tr = _make_mon3tr(pos)
    world.add_unit(mon3tr)
    carrier._kal_tsit_mon3tr_id = mon3tr.unit_id
    world.log(f"Kal'tsit: Mon3tr deployed  HP={mon3tr.hp}  pos={pos}")


register_talent(
    _KAL_TSIT_TALENT_TAG,
    on_battle_start=_kal_tsit_on_battle_start,
    on_death=_despawn_mon3tr,
    on_retreat=_despawn_mon3tr,
)


# ---------------------------------------------------------------------------
# S3: All-Out
# ---------------------------------------------------------------------------

def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_ATK_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def make_kal_tsit(slot: str = "S3") -> UnitState:
    """Kal'tsit E2 max, trust 100. Mon3tr auto-deploys on battle start. S3: ATK +80% for 40s."""
    op = _base_stats()
    op.name = "Kal'tsit"
    op.archetype = RoleArchetype.SUP_SUMMONER
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.ARTS
    op.attack_range_melee = False
    op.range_shape = KAL_TSIT_RANGE
    op.block = 1
    op.cost = 16

    op.talents = [TalentComponent(name="Mon3tr", behavior_tag=_KAL_TSIT_TALENT_TAG)]

    if slot == "S3":
        op.skill = SkillComponent(
            name="All-Out",
            slot="S3",
            sp_cost=40,
            initial_sp=20,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
