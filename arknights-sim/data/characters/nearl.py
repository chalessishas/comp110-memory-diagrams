"""Nearl (临光) — 6* Defender (Knight archetype).

Talent "Holy Knight's Light" (E2): Every 25s, restores HP equal to 8% of max_hp
  to all allies within range (5-tile cross). Passive, fires via on_tick accumulator.

S2 "Justice": ATK +100%, DEF +55%, duration 30s.
  sp_cost=30, initial_sp=15, AUTO_TIME, AUTO trigger, requires_target=True.
  Dual-axis buff: both ATK and DEF buffs apply/clear together.

S3 "The Champion's Path": ATK +150%, DEF +55% self; allies within range gain
  ATK +20% and DEF +20% (TTL-stamp aura). Duration=45s, MANUAL.
  sp_cost=55, initial_sp=15, AUTO_TIME.

Base stats from ArknightsGameData (E2 max, trust 100, char_148_nearl).
  HP=2780, ATK=502, DEF=625, RES=10, atk_interval=1.2s, cost=21, block=3.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession, RoleArchetype,
    SPGainMode, SkillTrigger,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.nearl import make_nearl as _base_stats


DEFENDER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_TALENT_TAG = "nearl_holy_knight_light"
_HEAL_INTERVAL = 25.0    # seconds between each AoE heal pulse
_HEAL_RATIO = 0.08       # 8% of ally max_hp restored per pulse
_ACCUM_ATTR = "_nearl_heal_accum"

_HEAL_RANGE = {(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)}


def _on_tick(world, carrier: UnitState, dt: float) -> None:
    accum = getattr(carrier, _ACCUM_ATTR, 0.0) + dt
    if accum < _HEAL_INTERVAL:
        setattr(carrier, _ACCUM_ATTR, accum)
        return
    if carrier.position is not None:
        cx, cy = round(carrier.position[0]), round(carrier.position[1])
        for ally in world.allies():
            if not ally.deployed or ally.hp >= ally.max_hp or ally.position is None:
                continue
            ax, ay = round(ally.position[0]), round(ally.position[1])
            if (ax - cx, ay - cy) in _HEAL_RANGE:
                healed = ally.heal(int(ally.max_hp * _HEAL_RATIO))
                if healed > 0:
                    world.global_state.total_healing_done += healed
                    world.log(
                        f"Nearl Holy Knight → {ally.name}  heal={healed}  ({ally.hp}/{ally.max_hp})"
                    )
    setattr(carrier, _ACCUM_ATTR, accum - _HEAL_INTERVAL)


register_talent(_TALENT_TAG, on_tick=_on_tick)


# --- S2: Justice ---
_S2_TAG = "nearl_s2_justice"
_S2_ATK_RATIO = 1.00     # ATK +100%
_S2_DEF_RATIO = 0.55     # DEF +55%
_S2_SOURCE_TAG = "nearl_s2_justice"


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_SOURCE_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S2_DEF_RATIO, source_tag=_S2_SOURCE_TAG,
    ))
    world.log(f"Nearl S2 Justice — ATK +{_S2_ATK_RATIO:.0%}, DEF +{_S2_DEF_RATIO:.0%}")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_SOURCE_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


# --- S3: The Champion's Path ---
_S3_TAG = "nearl_s3_champions_path"
_S3_SELF_ATK_RATIO = 1.50     # self ATK +150%
_S3_SELF_DEF_RATIO = 0.55     # self DEF +55%
_S3_ALLY_ATK_RATIO = 0.20     # ally ATK +20% aura
_S3_ALLY_DEF_RATIO = 0.20     # ally DEF +20% aura
_S3_SELF_ATK_TAG = "nearl_s3_self_atk"
_S3_SELF_DEF_TAG = "nearl_s3_self_def"
_S3_ALLY_ATK_TAG = "nearl_s3_ally_atk"
_S3_ALLY_DEF_TAG = "nearl_s3_ally_def"
_S3_AURA_TTL = 0.3
_S3_DURATION = 45.0


def _in_range(carrier: UnitState, ally: UnitState) -> bool:
    if carrier.position is None or ally.position is None:
        return False
    ox, oy = carrier.position; ax, ay = ally.position
    return (round(ax) - round(ox), round(ay) - round(oy)) in set(carrier.range_shape.tiles)


def _stamp_ally_aura(world, carrier: UnitState) -> None:
    now = world.global_state.elapsed
    expires = now + _S3_AURA_TTL + 0.15
    for ally in world.allies():
        if ally is carrier or not ally.alive or not ally.deployed:
            continue
        if not _in_range(carrier, ally):
            continue
        for tag, axis, ratio in (
            (_S3_ALLY_ATK_TAG, BuffAxis.ATK, _S3_ALLY_ATK_RATIO),
            (_S3_ALLY_DEF_TAG, BuffAxis.DEF, _S3_ALLY_DEF_RATIO),
        ):
            existing = next((b for b in ally.buffs if b.source_tag == tag), None)
            if existing:
                existing.expires_at = expires
            else:
                ally.buffs.append(Buff(
                    axis=axis, stack=BuffStack.RATIO,
                    value=ratio, source_tag=tag, expires_at=expires,
                ))


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_SELF_ATK_RATIO, source_tag=_S3_SELF_ATK_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S3_SELF_DEF_RATIO, source_tag=_S3_SELF_DEF_TAG,
    ))
    _stamp_ally_aura(world, carrier)
    world.log(
        f"Nearl S3 Champion's Path — self ATK+{_S3_SELF_ATK_RATIO:.0%}, "
        f"DEF+{_S3_SELF_DEF_RATIO:.0%}; allies +{_S3_ALLY_ATK_RATIO:.0%} ATK/DEF"
    )


def _s3_on_tick(world, carrier: UnitState, dt: float) -> None:
    _stamp_ally_aura(world, carrier)


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [
        b for b in carrier.buffs
        if b.source_tag not in (_S3_SELF_ATK_TAG, _S3_SELF_DEF_TAG)
    ]
    for ally in world.allies():
        ally.buffs = [
            b for b in ally.buffs
            if b.source_tag not in (_S3_ALLY_ATK_TAG, _S3_ALLY_DEF_TAG)
        ]


register_skill(_S3_TAG, on_start=_s3_on_start, on_tick=_s3_on_tick, on_end=_s3_on_end)


def make_nearl(slot: str = "S2") -> UnitState:
    """Nearl E2 max. Talent: 25s passive AoE heal. S2: ATK+100%/DEF+55% 30s. S3: dual-axis ally aura."""
    op = _base_stats()
    op.name = "Nearl"
    op.archetype = RoleArchetype.DEF_GUARDIAN
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = DEFENDER_RANGE
    op.cost = 21

    op.talents = [TalentComponent(name="Holy Knight's Light", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Justice",
            slot="S2",
            sp_cost=30,
            initial_sp=15,
            duration=30.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S3":
        op.skill = SkillComponent(
            name="The Champion's Path",
            slot="S3",
            sp_cost=55,
            initial_sp=15,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
