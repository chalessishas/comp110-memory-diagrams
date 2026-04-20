"""怒潮凛冬 (Mudrock/Wild Mane character, 6* Guard — 撼地者).

Curated layer wrapping generated/headb2.py base stats + her 撼地者 特性:
attacks deal 50% ATK splash damage within 1.0 tile radius of primary target.

Talent 1 "Shockwave": On deployment, splash_radius increases to 1.5 tiles.
Talent 2 "Ward of the Fertile Soil": Every 9s gains 1 Shield (max 3);
  each shield absorbs 1 complete hit. When a shield breaks: restore 25% max HP
  and gain 2 SP.

S3 "Storm Strike": 5 consecutive hits each dealing 200% ATK physical damage,
  scheduled via EventQueue at 0.3s intervals from activation.
  sp_cost=45, initial_sp=20, duration=5.0s, MANUAL trigger, AUTO_TIME SP gain.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, TalentComponent, StatusEffect
from core.types import BuffAxis, BuffStack, RoleArchetype, SPGainMode, SkillTrigger, StatusKind
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.headb2 import make_headb2 as _base_stats


# --- Talent 1: Shockwave — splash radius 1.0 → 1.5 at E2 ---
_TALENT_TAG = "headb2_shockwave"
_BASE_SPLASH_RADIUS = 1.0
_TALENT_SPLASH_RADIUS = 1.5


def _shockwave_on_battle_start(world, carrier: UnitState) -> None:
    carrier.splash_radius = _TALENT_SPLASH_RADIUS
    world.log(f"headb2 Shockwave — splash_radius → {_TALENT_SPLASH_RADIUS}")


register_talent(_TALENT_TAG, on_battle_start=_shockwave_on_battle_start)


# --- Talent 2: Ward of the Fertile Soil ---
_WARD_TAG = "headb2_ward_fertile_soil"
_WARD_SHIELD_INTERVAL = 9.0    # seconds between shield gains
_WARD_MAX_SHIELDS = 3          # max simultaneous shields
_WARD_SHIELD_AMOUNT = 999999   # sentinel: each shield absorbs 1 complete hit
_WARD_HEAL_RATIO = 0.25        # 25% max HP restored on shield break
_WARD_SP_GRANT = 2             # SP gained per shield break


def _ward_count(unit) -> int:
    return sum(1 for s in unit.statuses if s.kind == StatusKind.SHIELD and s.source_tag == _WARD_TAG)


def _ward_on_tick(world, carrier, dt: float) -> None:
    for tc in carrier.talents:
        if tc.behavior_tag != _WARD_TAG:
            continue
        tc.params.setdefault("_acc", 0.0)
        tc.params["_acc"] += dt
        while tc.params["_acc"] >= _WARD_SHIELD_INTERVAL:
            tc.params["_acc"] -= _WARD_SHIELD_INTERVAL
            curr = _ward_count(carrier)
            if curr < _WARD_MAX_SHIELDS:
                carrier.statuses.append(StatusEffect(
                    kind=StatusKind.SHIELD,
                    source_tag=_WARD_TAG,
                    params={"amount": float(_WARD_SHIELD_AMOUNT)},
                ))
                world.log(f"headb2 Ward +1 Shield ({curr+1}/{_WARD_MAX_SHIELDS})")
        # Sync baseline for break detection in on_hit_received
        tc.params["_prev_shields"] = float(_ward_count(carrier))
        break


def _ward_on_hit_received(world, defender, attacker, damage: int) -> None:
    for tc in defender.talents:
        if tc.behavior_tag != _WARD_TAG:
            continue
        prev = int(tc.params.get("_prev_shields", 0))
        # Force-break any Ward shield that absorbed damage this hit (one-hit-block behavior)
        defender.statuses = [
            s for s in defender.statuses
            if not (s.kind == StatusKind.SHIELD
                    and s.source_tag == _WARD_TAG
                    and s.params.get("amount", _WARD_SHIELD_AMOUNT) < _WARD_SHIELD_AMOUNT)
        ]
        curr = _ward_count(defender)
        broken = prev - curr
        if broken > 0:
            heal = int(defender.max_hp * _WARD_HEAL_RATIO)
            defender.hp = min(defender.max_hp, defender.hp + heal)
            if defender.skill is not None:
                sp_gain = float(_WARD_SP_GRANT * broken)
                defender.skill.sp = min(defender.skill.sp + sp_gain, float(defender.skill.sp_cost))
            world.log(f"headb2 Ward {broken} shield(s) broke — heal {heal}, SP+{_WARD_SP_GRANT * broken}")
        tc.params["_prev_shields"] = float(curr)
        break


register_talent(_WARD_TAG, on_tick=_ward_on_tick, on_hit_received=_ward_on_hit_received)


# --- S2: Shockwave Burst ---
_S2_TAG = "headb2_s2_shockwave_burst"
_S2_ATK_RATIO = 0.80
_S2_BUFF_TAG = "headb2_s2_atk"
_S2_DURATION = 15.0

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


def _s2_on_start(world, carrier) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    world.log(f"headb2 S2 Shockwave Burst — ATK+{_S2_ATK_RATIO:.0%}/{_S2_DURATION}s")


def _s2_on_end(world, carrier) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


register_skill(_S3_TAG, on_start=_s3_on_start)


def make_headb2(slot: str | None = None) -> UnitState:
    """怒潮凛冬 E2 max. 撼地者 特性: 50% ATK splash. Shockwave talent: splash_radius 1→1.5."""
    op = _base_stats()
    op.archetype = RoleArchetype.GUARD_CRUSHER
    op.splash_radius = _BASE_SPLASH_RADIUS
    op.splash_atk_multiplier = 0.5
    op.talents = [
        TalentComponent(name="Shockwave", behavior_tag=_TALENT_TAG),
        TalentComponent(name="Ward of the Fertile Soil", behavior_tag=_WARD_TAG),
    ]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Shockwave Burst",
            slot="S2",
            sp_cost=25,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
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
