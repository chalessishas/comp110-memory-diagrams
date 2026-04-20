"""Kal'tsit (凯尔希) — 6★ Medic (MED_PROTECTOR archetype).

Summons Mon3tr as a deployed allied tank (physical melee, block=3).
  Mon3tr spawns when Kal'tsit is added to the world (on_battle_start).

Talent "Non-Damaging Restructuring" (on Mon3tr's on_death):
  When Mon3tr is defeated, deal True damage = 30% of Mon3tr's max HP
  to all enemies within Chebyshev distance 1 (8 surrounding tiles),
  and stun those enemies for _BURST_STUN_DURATION seconds.

Lifecycle:
  - Kal'tsit on_death/on_retreat → Mon3tr despawns.
  - Mon3tr on_death → AoE True damage + Stun burst fires.

S3 "All-Out" (simplified — ATK +_S3_ATK_RATIO for duration, requires_target=False):
  Also sets Mon3tr's ATK to buffed value during skill. Full S3 in real game
  also significantly buffs Mon3tr stats, but we model Kal'tsit's own ATK.
  sp_cost=40, initial_sp=20, AUTO_TIME, AUTO trigger.

Base stats from ArknightsGameData (E2 max, trust 100, char_003_kalts):
  HP=2033, ATK=490, DEF=255, RES=0, atk_interval=2.85, block=1.

Mon3tr E2 max (char_4179_monstr combat form, approximate):
  HP=5472, ATK=776, DEF=920, RES=0, atk_interval=2.0, block=3, physical melee.
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape,
    TalentComponent, StatusEffect,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode, StatusKind,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.kalts import make_kalts as _base_stats


MEDIC_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0),
    (1, 1), (2, 1), (1, -1), (2, -1),
))
MONSTR_MELEE_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# Kal'tsit talent tag — drives on_battle_start spawn + on_death/on_retreat lifecycle
_KALTSIT_TALENT_TAG = "kaltsit_summon_monstr"

# Mon3tr talent tag — drives on_death AoE burst
_MONSTR_TALENT_TAG = "monstr_non_damaging_restructuring"

# Burst parameters
_BURST_DAMAGE_RATIO = 0.30     # True damage = 30% Mon3tr max HP
_BURST_STUN_DURATION = 3.0    # seconds
_BURST_STUN_TAG = "monstr_burst_stun"
_BURST_RADIUS = 1              # Chebyshev distance ≤ 1 (8 surrounding tiles)

# S3 parameters
_S3_TAG = "kaltsit_s3_all_out"
_S3_ATK_RATIO = 0.80          # +80% ATK
_S3_ATK_BUFF_TAG = "kaltsit_s3_atk"
_S3_DURATION = 40.0

# Mon3tr stats (E2 max approximate)
_MONSTR_HP = 5472
_MONSTR_ATK = 776
_MONSTR_DEF = 920

_KALTSIT_MONSTR_ATTR = "_kaltsit_monstr_id"


def _make_monstr(position: tuple) -> UnitState:
    """Mon3tr — summoned physical melee tank. block=3."""
    m = UnitState(
        name="Mon3tr",
        faction=Faction.ALLY,
        max_hp=_MONSTR_HP,
        hp=_MONSTR_HP,
        atk=_MONSTR_ATK,
        defence=_MONSTR_DEF,
        res=0.0,
        atk_interval=2.0,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=True,
        range_shape=MONSTR_MELEE_RANGE,
        block=3,
        cost=0,
        deployed=True,
        position=position,
    )
    m.talents = [TalentComponent(name="Non-Damaging Restructuring", behavior_tag=_MONSTR_TALENT_TAG)]
    return m


# ─── Mon3tr on_death: True damage + Stun burst ────────────────────────────────

def _monstr_on_death(world, monstr: UnitState) -> None:
    """Mon3tr defeated → burst True damage + Stun to adjacent 8 tiles."""
    if monstr.position is None:
        return
    mx, my = monstr.position
    true_dmg = int(monstr.max_hp * _BURST_DAMAGE_RATIO)
    elapsed = world.global_state.elapsed

    for e in world.enemies():
        if not e.alive or e.position is None:
            continue
        ex, ey = e.position
        if max(abs(round(ex) - round(mx)), abs(round(ey) - round(my))) <= _BURST_RADIUS:
            dealt = e.take_true(true_dmg)
            world.global_state.total_damage_dealt += dealt
            e.statuses = [s for s in e.statuses if s.source_tag != _BURST_STUN_TAG]
            e.statuses.append(StatusEffect(
                kind=StatusKind.STUN,
                source_tag=_BURST_STUN_TAG,
                expires_at=elapsed + _BURST_STUN_DURATION,
            ))
            world.log(
                f"Mon3tr burst → {e.name}  true={dealt}  stun={_BURST_STUN_DURATION}s"
            )


register_talent(_MONSTR_TALENT_TAG, on_death=_monstr_on_death)


# ─── Kal'tsit talent: spawn Mon3tr + lifecycle ────────────────────────────────

def _kaltsit_spawn_monstr(world, carrier: UnitState) -> None:
    """Spawn Mon3tr at Kal'tsit's position when Kal'tsit is added."""
    if not carrier.deployed or carrier.position is None:
        return
    monstr = _make_monstr(carrier.position)
    world.add_unit(monstr)
    setattr(carrier, _KALTSIT_MONSTR_ATTR, monstr.unit_id)
    world.log(
        f"Kal'tsit: Mon3tr deployed  HP={monstr.hp}  ATK={monstr.atk}  pos={monstr.position}"
    )


def _kaltsit_despawn_monstr(world, carrier: UnitState) -> None:
    """Kal'tsit dies or retreats → despawn Mon3tr if still alive."""
    monstr_id = getattr(carrier, _KALTSIT_MONSTR_ATTR, None)
    if monstr_id is not None:
        unit = world.unit_by_id(monstr_id)
        if unit is not None and unit.alive:
            unit.alive = False
            unit.hp = 0
            unit.deployed = False
    setattr(carrier, _KALTSIT_MONSTR_ATTR, None)


register_talent(
    _KALTSIT_TALENT_TAG,
    on_battle_start=_kaltsit_spawn_monstr,
    on_death=_kaltsit_despawn_monstr,
    on_retreat=_kaltsit_despawn_monstr,
)


# ─── S3: All-Out ──────────────────────────────────────────────────────────────

def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_ATK_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_kaltsit(slot: str = "S3") -> UnitState:
    """Kal'tsit E2 max. Talent: spawn Mon3tr on deploy. S3: ATK +80% for 40s."""
    op = _base_stats()
    op.name = "Kal'tsit"
    op.archetype = RoleArchetype.SUP_SUMMONER
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.HEAL
    op.attack_range_melee = False
    op.range_shape = MEDIC_RANGE
    op.block = 1
    op.cost = 20

    op.talents = [TalentComponent(name="Summon Mon3tr", behavior_tag=_KALTSIT_TALENT_TAG)]

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
