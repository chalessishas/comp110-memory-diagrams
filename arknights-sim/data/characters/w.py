"""W (W) — 6* Sniper.

Talent "Last Will" (simplified): Each attack levitates the target for 1.5s.
  Levitated enemies cannot move or attack (can_act() = False).
  Refreshes on every subsequent hit.
  Original: kill-stacking explosive chain; simplified to on-hit LEVITATE.

S2 "Extra Supplies": 15s duration, ATK +60%.
  sp_cost=30, initial_sp=10, AUTO_TIME, AUTO trigger, requires_target=True.

S3 "Chaos Edict": Instant activation (duration=0). Places up to _BOMB_MAX=4
  bombs on the highest-HP enemies in range. Each bomb detonates independently
  after _BOMB_DELAY=3.0s at the position captured at throw time, dealing
  _BOMB_ATK_RATIO=3.10 (310%) ATK physical AoE within _BOMB_RADIUS=1.2 tiles.
  Uses EventQueue: 1 handler registered per world at on_battle_start; up to 4
  events scheduled per activation with per-bomb position in payload.
  sp_cost=50, initial_sp=20, AUTO_TIME, AUTO trigger, requires_target=True.

Constants verified against arknights.wiki.gg/wiki/W (M3 values):
  _BOMB_DELAY: 3.0s, _BOMB_ATK_RATIO: 3.10, _BOMB_RADIUS: 1.2 tiles.

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
from data.characters.generated.cqbw import make_cqbw as _base_stats


SNIPER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 5) for dy in range(-1, 2)
))

# --- Talent: Last Will ---
_TALENT_TAG = "w_last_will"
_LEVITATE_DURATION = 1.5
_LEVITATE_TAG = "w_levitate"

# --- S2: Extra Supplies ---
_S2_TAG = "w_s2_extra_supplies"
_S2_ATK_RATIO = 0.60
_S2_BUFF_TAG = "w_s2_atk_buff"
_S2_DURATION = 15.0

# --- S3: Chaos Edict (4 delayed bombs) ---
_S3_TAG = "w_s3_chaos_edict"
_BOMB_DELAY = 3.0          # seconds after throw before detonation (wiki M3)
_BOMB_ATK_RATIO = 3.10     # 310% ATK per bomb (wiki M3)
_BOMB_RADIUS = 1.2         # tile radius of each bomb's AoE (wiki)
_BOMB_MAX = 4              # up to 4 bombs per activation, targeting highest-HP enemies
_BOMB_KIND_PREFIX = "w_bomb_detonate"


def _talent_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    # Refresh LEVITATE: remove stale, apply fresh
    target.statuses = [s for s in target.statuses if s.source_tag != _LEVITATE_TAG]
    target.statuses.append(StatusEffect(
        kind=StatusKind.LEVITATE,
        source_tag=_LEVITATE_TAG,
        expires_at=world.global_state.elapsed + _LEVITATE_DURATION,
    ))
    world.log(
        f"W Last Will → {target.name}  levitate ({_LEVITATE_DURATION}s)"
    )


def _w_on_battle_start(world, carrier: UnitState) -> None:
    kind = f"{_BOMB_KIND_PREFIX}_{carrier.unit_id}"

    def _bomb_handler(w, event) -> None:
        if not carrier.alive or not carrier.deployed:
            return
        bx = event.payload.get("bx", carrier.position[0] if carrier.position else 0.0)
        by = event.payload.get("by", carrier.position[1] if carrier.position else 0.0)
        raw = int(carrier.effective_atk * _BOMB_ATK_RATIO)
        hit_count = 0
        for e in w.enemies():
            if not e.alive or e.position is None:
                continue
            ex, ey = e.position
            if (ex - bx) ** 2 + (ey - by) ** 2 <= _BOMB_RADIUS ** 2:
                dmg = e.take_physical(raw)
                w.global_state.total_damage_dealt += dmg
                hit_count += 1
                w.log(
                    f"W S3 bomb detonates @ ({bx:.0f},{by:.0f}) → {e.name}  "
                    f"dmg={dmg}  ({e.hp}/{e.max_hp})"
                )
        w.log(f"W S3 bomb: {hit_count} enemies hit")

    world.event_queue.register(kind, _bomb_handler)


register_talent(_TALENT_TAG, on_attack_hit=_talent_on_attack_hit, on_battle_start=_w_on_battle_start)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def _s3_on_start(world, carrier: UnitState) -> None:
    # Pick up to _BOMB_MAX enemies in range, prioritised by highest current HP
    if carrier.position is None:
        return
    cx, cy = carrier.position
    in_range = [
        e for e in world.enemies()
        if e.alive and e.position is not None
        and (round(e.position[0]) - round(cx), round(e.position[1]) - round(cy))
           in set(carrier.range_shape.tiles)
    ]
    # Sort by HP descending (highest HP = primary targets)
    targets = sorted(in_range, key=lambda e: -e.hp)[:_BOMB_MAX]

    # Fallback: if nothing in range, use the primary __target__ if available
    if not targets:
        t = getattr(carrier, "__target__", None)
        if t is not None and t.alive and t.position is not None:
            targets = [t]

    kind = f"{_BOMB_KIND_PREFIX}_{carrier.unit_id}"
    fire_at = world.global_state.elapsed + _BOMB_DELAY
    for t in targets:
        bx, by = t.position
        world.event_queue.schedule(fire_at=fire_at, kind=kind, bx=bx, by=by)
    world.log(
        f"W S3: {len(targets)} bomb(s) placed, "
        f"detonate at t={fire_at:.1f}s"
    )


register_skill(_S3_TAG, on_start=_s3_on_start)


def make_w(slot: str = "S2") -> UnitState:
    """W E2 max. Talent: LEVITATE on every hit. S2: ATK burst. S3: delayed bomb (EventQueue)."""
    op = _base_stats()
    op.name = "W"
    op.archetype = RoleArchetype.SNIPER_SIEGE
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNIPER_RANGE
    op.cost = 29

    op.talents = [TalentComponent(name="Last Will", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Extra Supplies",
            slot="S2",
            sp_cost=30,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Chaos Edict",
            slot="S3",
            sp_cost=50,
            initial_sp=20,
            duration=0.0,           # instant activation — bomb is placed, no hold
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
