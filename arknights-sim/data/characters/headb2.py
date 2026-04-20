"""怒潮凛冬 (Mudrock/Wild Mane character, 6* Guard — 撼地者).

Curated layer wrapping generated/headb2.py base stats + her 撼地者 特性:
attacks deal 50% ATK splash damage within 1.0 tile radius of primary target.

Talent "Shockwave": On deployment, splash_radius increases to 1.5 tiles.

S3 "Storm Strike": 5 consecutive hits each dealing 200% ATK physical damage,
  scheduled via EventQueue at 0.3s intervals from activation.
  sp_cost=45, initial_sp=20, duration=5.0s, MANUAL trigger, AUTO_TIME SP gain.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, TalentComponent
from core.types import RoleArchetype, SPGainMode, SkillTrigger
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.headb2 import make_headb2 as _base_stats


# --- Talent: Shockwave — splash radius 1.0 → 1.5 at E2 ---
_TALENT_TAG = "headb2_shockwave"
_BASE_SPLASH_RADIUS = 1.0
_TALENT_SPLASH_RADIUS = 1.5


def _shockwave_on_battle_start(world, carrier: UnitState) -> None:
    carrier.splash_radius = _TALENT_SPLASH_RADIUS
    world.log(f"headb2 Shockwave — splash_radius → {_TALENT_SPLASH_RADIUS}")


register_talent(_TALENT_TAG, on_battle_start=_shockwave_on_battle_start)


_S3_TAG = "headb2_s3_storm_strike"
_S3_EVENT_KIND = "headb2_smash_hit"
_S3_HIT_COUNT = 5
_S3_ATK_RATIO = 2.0
_S3_HIT_INTERVAL = 0.3
_S3_DURATION = 5.0


def _smash_hit_handler(world, event) -> None:
    attacker = world.unit_by_id(event.payload["attacker_id"])
    target = world.unit_by_id(event.payload["target_id"])
    if attacker is None or not attacker.alive:
        return
    if target is None or not target.alive:
        return
    dmg = int(attacker.effective_atk * event.payload["atk_ratio"])
    actual = target.take_physical(dmg)
    world.global_state.total_damage_dealt += actual


def _s3_on_start(world, carrier) -> None:
    if _S3_EVENT_KIND not in world.event_queue._handlers:
        world.event_queue.register(_S3_EVENT_KIND, _smash_hit_handler)
    target = getattr(carrier, "__target__", None)
    if target is None:
        return
    now = world.global_state.elapsed
    world.event_queue.schedule_repeating(
        first_at=now,
        interval=_S3_HIT_INTERVAL,
        count=_S3_HIT_COUNT,
        kind=_S3_EVENT_KIND,
        attacker_id=carrier.unit_id,
        target_id=target.unit_id,
        atk_ratio=_S3_ATK_RATIO,
    )


register_skill(_S3_TAG, on_start=_s3_on_start)


def make_headb2(slot: str | None = None) -> UnitState:
    """怒潮凛冬 E2 max. 撼地者 特性: 50% ATK splash. Shockwave talent: splash_radius 1→1.5."""
    op = _base_stats()
    op.archetype = RoleArchetype.GUARD_CRUSHER
    op.splash_radius = _BASE_SPLASH_RADIUS
    op.splash_atk_multiplier = 0.5
    op.talents = [TalentComponent(name="Shockwave", behavior_tag=_TALENT_TAG)]

    if slot == "S3":
        op.skill = SkillComponent(
            name="Storm Strike",
            slot="S3",
            sp_cost=45,
            initial_sp=20,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=True,
            behavior_tag=_S3_TAG,
        )

    return op
