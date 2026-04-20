"""Rope (暗索) — 4* Specialist (Hookmaster archetype).

Hookmaster trait: Can attack from a distance; each attack pulls the target
  1 tile backward along its path (toward spawn).
  Implemented via push_distance=1 — same ECS primitive as SPEC_PUSHER.

S2 "Binding Arts" (M3): Instant ranged Arts 200% ATK to 1 target + BIND (1.5s)
  + pull 3 tiles.
  sp_cost=25, initial_sp=10, AUTO_ATTACK.

Base stats: E2 max, trust 100 (ArknightsGameData char_236_rope).
  HP=1720, ATK=728, DEF=385, RES=0, atk_interval=1.8s, cost=12, block=2.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape, StatusEffect
from core.types import (
    AttackType, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode, StatusKind,
)
from core.systems.skill_system import register_skill
from core.systems.combat_system import _apply_push
from data.characters.generated.rope import make_rope as _base_stats


HOOKMASTER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 4) for dy in range(-1, 2)
))

_S2_TAG = "rope_s2_binding_arts"
_S2_ATK_MULT = 2.00    # 200% ATK
_S2_PULL_DIST = 3      # pull 3 tiles
_S2_BIND_DURATION = 1.5
_S2_BIND_TAG = "rope_s2_bind"
_BASE_PULL = 1


def _s2_on_start(world, unit: UnitState) -> None:
    if unit.position is None:
        return
    ox, oy = unit.position
    tiles = set(HOOKMASTER_RANGE.tiles)
    burst_atk = int(unit.effective_atk * _S2_ATK_MULT)

    # Instant single-target: nearest enemy in range
    candidates = [
        e for e in world.enemies()
        if e.alive and e.position is not None
        and (round(e.position[0]) - round(ox), round(e.position[1]) - round(oy)) in tiles
    ]
    if not candidates:
        return

    target = min(candidates, key=lambda e: (
        (e.position[0] - ox) ** 2 + (e.position[1] - oy) ** 2
    ))

    dealt = target.take_arts(burst_atk)
    world.global_state.total_damage_dealt += dealt
    world.log(f"Rope S2 → {target.name}  dmg={dealt}  ({target.hp}/{target.max_hp})")

    if target.alive:
        # Apply BIND
        elapsed = world.global_state.elapsed
        target.statuses = [s for s in target.statuses if s.source_tag != _S2_BIND_TAG]
        target.statuses.append(StatusEffect(
            kind=StatusKind.BIND,
            source_tag=_S2_BIND_TAG,
            expires_at=elapsed + _S2_BIND_DURATION,
        ))
        # Pull 3 tiles backward
        _apply_push(target, _S2_PULL_DIST)
        world.log(f"Rope S2 binds {target.name} ({_S2_BIND_DURATION}s) + pulls {_S2_PULL_DIST} tiles")


register_skill(_S2_TAG, on_start=_s2_on_start)


def make_rope(slot: str = "S2") -> UnitState:
    """Rope E2 max. Hookmaster: pull 1 tile per attack. S2: instant Arts 200%+BIND+3-tile pull."""
    op = _base_stats()
    op.name = "Rope"
    op.archetype = RoleArchetype.SPEC_HOOKMASTER
    op.profession = Profession.SPECIALIST
    op.range_shape = HOOKMASTER_RANGE
    op.attack_range_melee = False
    op.block = 2
    op.cost = 12
    op.push_distance = _BASE_PULL   # pull 1 tile per normal attack

    if slot == "S2":
        op.skill = SkillComponent(
            name="Binding Arts",
            slot="S2",
            sp_cost=25,
            initial_sp=10,
            duration=0.0,        # instant
            sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    return op
