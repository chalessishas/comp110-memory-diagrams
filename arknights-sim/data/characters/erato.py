"""Erato (埃拉托) — 5* Sniper (Besieger archetype).

Class trait: Prioritizes attacking heaviest enemy; deals 1.5× ATK to blocked enemies.

Talent "Song of Dreams" (E2): Attacks do not wake sleeping enemies.
  When hitting a SLEEP target: ignores 50% of target's DEF (bonus true damage).
  Target remains asleep after the hit (SLEEP status re-applied).

S1 "Strafing Fire": ATK +100% for 20s.
  sp_cost=30, initial_sp=10, AUTO_TIME, AUTO trigger, requires_target=True.

Base stats: E2 max, trust 100 (generated/erato.py).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import AttackType, BuffAxis, BuffStack, Profession, RoleArchetype, SPGainMode, SkillTrigger, StatusKind
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent, register_pre_attack_hook
from data.characters.generated.erato import make_erato as _base_stats


# --- Talent: Song of Dreams — 50% DEF ignore on sleeping targets, don't wake ---
_TALENT_TAG = "erato_song_of_dreams"
_DEF_IGNORE_RATIO = 0.50


def _song_pre_attack(world, attacker: UnitState, target) -> None:
    sleep_statuses = [s for s in target.statuses if s.kind == StatusKind.SLEEP]
    attacker._erato_sleep_snapshot = sleep_statuses  # empty list = not sleeping


def _song_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    saved = getattr(attacker, "_erato_sleep_snapshot", [])
    if not saved:
        return
    # 50% DEF ignore as bonus true damage
    bonus = int(target.effective_def * _DEF_IGNORE_RATIO)
    if bonus > 0:
        extra = target.take_true(bonus)
        world.global_state.total_damage_dealt += extra
        world.log(f"Erato Song of Dreams DEF-ignore → {target.name} +{extra}")
    # Don't wake: re-apply the SLEEP status (take_physical cleared it)
    if target.alive:
        target.statuses.extend(saved)
        world.log(f"Erato Song of Dreams — {target.name} stays asleep")
    attacker._erato_sleep_snapshot = []


register_pre_attack_hook(_TALENT_TAG, _song_pre_attack)
register_talent(_TALENT_TAG, on_attack_hit=_song_on_attack_hit)

# Standard Besieger Sniper range: 3 forward + flanking tiles
BESIEGER_RANGE_5STAR = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0),
    (1, -1), (1, 1), (2, -1), (2, 1),
))

# --- S2: Killshot ---
_S2_TAG = "erato_s2_killshot"
_S2_ATK_RATIO = 2.00    # ATK +200% → each shot deals 3× base ATK
_S2_AMMO = 3            # 3 heavy rounds
_S2_SOURCE_TAG = "erato_s2_killshot"


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_SOURCE_TAG,
    ))
    world.log(f"Erato S2 Killshot — {_S2_AMMO} rounds, ATK+{_S2_ATK_RATIO:.0%}")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_SOURCE_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


# --- S1: Strafing Fire ---
_S1_TAG = "erato_s1_strafing_fire"
_S1_ATK_RATIO = 1.00     # ATK +100%
_S1_SOURCE_TAG = "erato_s1_strafing_fire"


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_SOURCE_TAG,
    ))
    world.log(f"Erato S1 Strafing Fire — ATK +{_S1_ATK_RATIO:.0%}")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_SOURCE_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_erato(slot: str = "S1") -> UnitState:
    """Erato E2 max. Besieger: targets heaviest enemy; 1.5× ATK to blocked enemies. S1: ATK+100% 20s."""
    op = _base_stats()
    op.name = "Erato"
    op.archetype = RoleArchetype.SNIPER_SIEGE
    op.profession = Profession.SNIPER
    op.range_shape = BESIEGER_RANGE_5STAR
    op.block = 1
    op.cost = 23
    op.talents = [TalentComponent(name="Song of Dreams", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Killshot",
            slot="S2",
            sp_cost=35,
            initial_sp=15,
            duration=0.0,
            ammo_count=_S2_AMMO,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S1":
        op.skill = SkillComponent(
            name="Strafing Fire",
            slot="S1",
            sp_cost=30,
            initial_sp=10,
            duration=20.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S1_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
