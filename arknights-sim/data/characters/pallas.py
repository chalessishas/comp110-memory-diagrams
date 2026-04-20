"""Pallas (帕拉斯) — 6★ Guard (Instructor archetype).

GUARD_INSTRUCTOR trait: Melee Guard with extended attack range. After each
  attack, grants all allied Operators in range a flat ATK bonus for a short
  duration ("inspiring" them). The buff refreshes on each hit.

Talent "Battle Inspiration" (战斗激励): After each attack that deals damage,
  all deployed allies within Pallas's attack range gain +80 flat ATK for 5s.
  If a buff is already present, its duration is refreshed rather than stacked.

S2 "Blessing of the Muses" (缪斯的祝福): 25s duration. Converts Pallas's
  attack damage to Arts, and adds ATK+30%. Wider swing + elemental shift
  lets her cut through armored enemies.
  sp_cost=35, initial_sp=15, AUTO_TIME, AUTO trigger, requires_target=True.

Base stats from ArknightsGameData (E2 max, trust 100, char_485_pallas).
  HP=2263, ATK=737, DEF=455, RES=0, atk_interval=1.05s, cost=17, block=2.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.pallas import make_pallas as _base_stats


# 3-column × 3-row forward range: reaches 0–2 tiles ahead, ±1 row
INSTRUCTOR_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 3) for dy in range(-1, 2)
))

_TALENT_TAG = "pallas_battle_inspiration"
_TALENT_BUFF_TAG = "pallas_inspire_atk"
_TALENT_ATK_FLAT = 80          # +80 flat ATK to in-range allies per hit
_TALENT_BUFF_DURATION = 5.0    # buff window in seconds

# S2: Blessing of the Muses
_S2_TAG = "pallas_s2_muses_blessing"
_S2_ATK_RATIO = 0.30           # +30% ATK
_S2_ATK_BUFF_TAG = "pallas_s2_atk"
_S2_DURATION = 25.0


def _ally_in_range(op: UnitState, ally: UnitState) -> bool:
    if op.position is None or ally.position is None:
        return False
    ox, oy = op.position
    ax, ay = ally.position
    dx = round(ax) - round(ox)
    dy = round(ay) - round(oy)
    return (dx, dy) in set(op.range_shape.tiles)


def _inspiration_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    if damage <= 0:
        return
    now = world.global_state.elapsed
    new_expires = now + _TALENT_BUFF_DURATION
    for ally in world.allies():
        if ally is attacker or not ally.alive or not ally.deployed:
            continue
        if not _ally_in_range(attacker, ally):
            continue
        existing = next(
            (b for b in ally.buffs if b.source_tag == _TALENT_BUFF_TAG), None
        )
        if existing is not None:
            existing.expires_at = new_expires
        else:
            ally.buffs.append(Buff(
                axis=BuffAxis.ATK, stack=BuffStack.FLAT,
                value=_TALENT_ATK_FLAT, source_tag=_TALENT_BUFF_TAG,
                expires_at=new_expires,
            ))
        world.log(
            f"Pallas inspiration → {ally.name}  +{_TALENT_ATK_FLAT} ATK  "
            f"expires={new_expires:.1f}s"
        )


register_talent(_TALENT_TAG, on_attack_hit=_inspiration_on_attack_hit)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.attack_type = AttackType.ARTS
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.attack_type = AttackType.PHYSICAL
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_ATK_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_pallas(slot: str = "S2") -> UnitState:
    """Pallas E2 max. GUARD_INSTRUCTOR: melee + inspire in-range allies. S2: Arts+ATK+30%."""
    op = _base_stats()
    op.name = "Pallas"
    op.archetype = RoleArchetype.GUARD_INSTRUCTOR
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = True
    op.range_shape = INSTRUCTOR_RANGE
    op.block = 2
    op.cost = 17

    op.talents = [TalentComponent(name="Battle Inspiration", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Blessing of the Muses",
            slot="S2",
            sp_cost=35,
            initial_sp=15,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
