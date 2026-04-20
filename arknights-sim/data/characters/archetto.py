"""Archetto (空弦) — 6* Sniper (Deadeye archetype).

Talent "Heartseeker": every 3rd attack applies DEF_DOWN (flat -100 DEF)
  to the target for 3s. Refresh on every 3rd hit. Introduces the first
  DEF_DOWN status+buff pair (parallel to Gnosis's RES_DOWN pattern).

S2 "Tactical Positioning": ATK +80%, 15s duration.
  sp_cost=20, initial_sp=10, AUTO_TIME, AUTO trigger.

Base stats from ArknightsGameData (E2 max, trust 100).
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
from data.characters.generated.archet import make_archet as _base_stats


DEADEYE_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 4) for dy in range(-1, 2)
))

# --- Talent: Heartseeker ---
_TALENT_TAG = "archetto_heartseeker"
_HIT_MODULO = 3          # every 3rd attack triggers
_DEF_DOWN_AMOUNT = 100   # flat DEF reduction
_DEF_DOWN_DURATION = 3.0
_DEF_DOWN_TAG = "archetto_def_down"

# --- S2: Tactical Positioning ---
_S2_TAG = "archetto_s2_tactical"
_S2_ATK_RATIO = 0.80
_S2_BUFF_TAG = "archetto_s2_atk"
_S2_DURATION = 15.0


def _talent_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    tc = next(t for t in attacker.talents if t.behavior_tag == _TALENT_TAG)
    count = int(tc.params.get("hit_count", 0)) + 1
    tc.params["hit_count"] = count

    if count % _HIT_MODULO != 0:
        return

    elapsed = world.global_state.elapsed
    expires = elapsed + _DEF_DOWN_DURATION

    target.statuses = [s for s in target.statuses if s.source_tag != _DEF_DOWN_TAG]
    target.buffs = [b for b in target.buffs if b.source_tag != _DEF_DOWN_TAG]

    target.statuses.append(StatusEffect(
        kind=StatusKind.DEF_DOWN,
        source_tag=_DEF_DOWN_TAG,
        expires_at=expires,
        params={"amount": _DEF_DOWN_AMOUNT},
    ))
    target.buffs.append(Buff(
        axis=BuffAxis.DEF,
        stack=BuffStack.FLAT,
        value=-_DEF_DOWN_AMOUNT,
        source_tag=_DEF_DOWN_TAG,
        expires_at=expires,
    ))
    world.log(
        f"Archetto Heartseeker → {target.name}  "
        f"DEF_DOWN -{_DEF_DOWN_AMOUNT} ({_DEF_DOWN_DURATION}s)"
    )


register_talent(_TALENT_TAG, on_attack_hit=_talent_on_attack_hit)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_archetto(slot: str = "S2") -> UnitState:
    """Archetto E2 max. Talent: DEF_DOWN -100 on every 3rd hit. S2: ATK +80%."""
    op = _base_stats()
    op.name = "Archetto"
    op.archetype = RoleArchetype.SNIPER_DEADEYE
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = DEADEYE_RANGE
    op.cost = 14

    op.talents = [TalentComponent(name="Heartseeker", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Tactical Positioning",
            slot="S2",
            sp_cost=20,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    return op
