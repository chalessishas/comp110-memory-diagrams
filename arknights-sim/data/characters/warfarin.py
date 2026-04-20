"""Warfarin — 5* Medic (Single-target archetype).

Talent "Blood Sample Recycle": When any enemy within Warfarin's range dies,
  Warfarin and one random deployed ally also in range each gain +1 SP.

Base stats from ArknightsGameData (E2 max, trust 100).
S2 Sanguinelant: +35% ATK to all deployed allies for 10s (sp_cost=3, fires unconditionally).
"""
from __future__ import annotations
import random as _random
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_enemy_killed_watcher
from data.characters.generated.warfarin import make_warfarin as _base_stats


# --- Talent: Blood Sample Recycle ---
_TALENT_TAG = "warfarin_blood_sample_recycle"
_TALENT_SP_GAIN = 1.0


def _blood_sample_on_enemy_killed(world, carrier: UnitState, killed) -> None:
    """Enemy dies in Warfarin's range → Warfarin + random in-range ally gain +1 SP."""
    if carrier.position is None or killed.position is None:
        return
    cx, cy = carrier.position
    kx, ky = killed.position
    if (round(kx) - round(cx), round(ky) - round(cy)) not in set(carrier.range_shape.tiles):
        return
    # SP gain for Warfarin (skips if skill is active)
    sk = carrier.skill
    if sk is not None and not sk.active_remaining > 0:
        sk.sp = min(sk.sp + _TALENT_SP_GAIN, float(sk.sp_cost))
    # SP gain for a random ally in range with a skill
    range_tiles = set(carrier.range_shape.tiles)
    candidates = [
        a for a in world.allies()
        if a is not carrier and a.skill is not None and a.position is not None
        and (round(a.position[0]) - round(cx), round(a.position[1]) - round(cy)) in range_tiles
    ]
    if candidates:
        chosen = _random.choice(candidates)
        if not chosen.skill.active_remaining > 0:
            chosen.skill.sp = min(chosen.skill.sp + _TALENT_SP_GAIN, float(chosen.skill.sp_cost))
        world.log(f"Warfarin Blood Sample: +1 SP → {chosen.name}")


register_enemy_killed_watcher(_TALENT_TAG, _blood_sample_on_enemy_killed)


MEDIC_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0),
))

_S2_TAG = "warfarin_s2_sanguinelant"
_S2_ATK_RATIO = 0.35
_S2_BUFF_TAG = "warfarin_s2_atk"


def _s2_on_start(world, carrier: UnitState) -> None:
    for ally in world.allies():
        if not ally.alive or not ally.deployed:
            continue
        ally.buffs.append(Buff(
            axis=BuffAxis.ATK, stack=BuffStack.RATIO,
            value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
        ))


def _s2_on_end(world, carrier: UnitState) -> None:
    for ally in world.allies():
        ally.buffs = [b for b in ally.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_warfarin(slot: str = "S2") -> UnitState:
    """Warfarin E2 max. Talent: Blood Sample Recycle (+1 SP on enemy kill in range). S2: team ATK buff."""
    op = _base_stats()
    op.name = "Warfarin"
    op.archetype = RoleArchetype.MEDIC_ST
    op.range_shape = MEDIC_RANGE
    op.attack_type = AttackType.HEAL
    op.cost = 12

    op.talents = [TalentComponent(name="Blood Sample Recycle", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Sanguinelant",
            slot="S2",
            sp_cost=3,
            initial_sp=1,
            duration=10.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            behavior_tag=_S2_TAG,
            requires_target=False,   # fires unconditionally — no heal target needed
        )
    return op
