"""Skill — SP 回复 + 技能触发/持续/结束. 技能行为由 behavior_tag 查注册表."""
from __future__ import annotations
from typing import Callable, Dict, Tuple
from ..types import Faction
from ..state.unit_state import SPGainMode, SkillTrigger

# skill behavior registry: tag → (on_start, on_tick, on_end)
# on_start(world, unit) / on_tick(world, unit, dt) / on_end(world, unit)
_SKILL_REGISTRY: Dict[str, Tuple[Callable, Callable, Callable]] = {}


def register_skill(tag: str, on_start=None, on_tick=None, on_end=None) -> None:
    noop = lambda *_: None
    _SKILL_REGISTRY[tag] = (on_start or noop, on_tick or noop, on_end or noop)


def skill_system(world, dt: float) -> None:
    now = world.global_state.elapsed
    for u in world.units:
        if not u.alive or not u.deployed or u.skill is None:
            continue
        sk = u.skill

        # ---- active duration tick ----
        if sk.active_remaining > 0.0:
            on_start, on_tick, on_end = _SKILL_REGISTRY.get(sk.behavior_tag, (None, None, None))
            if on_tick:
                on_tick(world, u, dt)
            sk.active_remaining -= dt
            if sk.active_remaining <= 0.0:
                sk.active_remaining = 0.0
                sk.sp = 0.0
                if on_end:
                    on_end(world, u)
            continue

        # ---- SP accumulation (time-based) ----
        if sk.sp_gain_mode == SPGainMode.AUTO_TIME and u.can_use_skill():
            sk.sp = min(sk.sp + dt, float(sk.sp_cost))

        # ---- Auto-trigger with lockout ----
        # Wiki: AUTO skills hold at full SP until target exists (lockout).
        # Skills with requires_target=False (pure buffs) fire unconditionally.
        if sk.trigger == SkillTrigger.AUTO and sk.sp >= sk.sp_cost:
            if not sk.requires_target:
                sk.locked_out = False
                _fire_skill(world, u)
            else:
                has_target = getattr(u, "__target__", None) is not None
                if has_target:
                    sk.locked_out = False
                    _fire_skill(world, u)
                else:
                    sk.locked_out = True


def _fire_skill(world, u) -> None:
    sk = u.skill
    sk.fire_count += 1
    on_start, on_tick, on_end = _SKILL_REGISTRY.get(sk.behavior_tag, (None, None, None))
    if on_start:
        on_start(world, u)
    if sk.duration > 0.0:
        sk.active_remaining = sk.duration
    else:
        sk.sp = 0.0


def manual_trigger(world, u) -> None:
    """Call from UI/test to fire a MANUAL skill if SP is ready."""
    if u.skill is None or u.skill.trigger != SkillTrigger.MANUAL:
        return
    if u.skill.sp >= u.skill.sp_cost:
        _fire_skill(world, u)
