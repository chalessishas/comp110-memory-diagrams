"""Totter (铅踝) — 4★ Sniper (Besieger archetype).

Besieger trait: 1.5× ATK vs blocked enemies (handled by combat_system).

Talent "Illuminating Eyes" (洞察眼) (E2):
  When CAMOUFLAGE enemies are in attack range, ATK +17%.
  Implemented as a short-lived buff refreshed each tick while condition holds.

S1 "Sunpiercer" (日刺) (M3): AUTO, sp_cost=3, initial_sp=0, instant (duration=0), AUTO_ATTACK.
  Deals 220% ATK physical damage to current target.

S2 "Prism Break" (棱镜破碎) (M3): MANUAL, sp_cost=40, initial_sp=25, duration=30s, AUTO_TIME.
  ATK +125%, ASPD +50; each attack also hits 2 additional random enemies.

Base stats from ArknightsGameData (E2 max, trust 100, char_4062_totter).
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape, TalentComponent,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode, StatusKind,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.totter import make_totter as _base_stats


BESIEGER_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0),
    (1, -1), (1, 1), (2, -1), (2, 1),
))

# --- Talent: Illuminating Eyes ---
_TALENT_TAG = "totter_illuminating_eyes"
_TALENT_ATK_RATIO = 0.17
_TALENT_BUFF_TAG = "totter_illuminating_eyes_buff"
_BUFF_WINDOW = 0.2  # refreshed each tick while CAMOUFLAGE enemy in range


def _enemy_in_range(op: UnitState, enemy: UnitState) -> bool:
    if op.position is None or enemy.position is None:
        return False
    ox, oy = op.position
    ex, ey = enemy.position
    dx = round(ex) - round(ox)
    dy = round(ey) - round(oy)
    return (dx, dy) in set(op.range_shape.tiles)


def _talent_on_tick(world, carrier: UnitState, dt: float) -> None:
    if not carrier.deployed:
        return
    camo_in_range = any(
        e.alive and e.has_status(StatusKind.CAMOUFLAGE) and _enemy_in_range(carrier, e)
        for e in world.enemies()
    )
    now = world.global_state.elapsed
    if camo_in_range:
        carrier.buffs = [b for b in carrier.buffs if b.source_tag != _TALENT_BUFF_TAG]
        carrier.buffs.append(Buff(
            axis=BuffAxis.ATK, stack=BuffStack.RATIO,
            value=_TALENT_ATK_RATIO, source_tag=_TALENT_BUFF_TAG,
            expires_at=now + _BUFF_WINDOW,
        ))
    else:
        carrier.buffs = [b for b in carrier.buffs if b.source_tag != _TALENT_BUFF_TAG]


def _talent_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    if not getattr(attacker, "_totter_s2_active", False):
        return
    enemies = [e for e in world.enemies() if e.alive]
    for _ in range(2):
        if not enemies:
            break
        extra_target = world.rng.choice(enemies)
        dealt = extra_target.take_physical(attacker.effective_atk)
        world.global_state.total_damage_dealt += dealt
        enemies = [e for e in enemies if e.alive]


register_talent(_TALENT_TAG, on_tick=_talent_on_tick, on_attack_hit=_talent_on_attack_hit)


# --- S1: Sunpiercer ---
_S1_TAG = "totter_s1_sunpiercer"
_S1_ATK_RATIO = 2.20


def _s1_on_start(world, carrier: UnitState) -> None:
    target = getattr(carrier, "__target__", None)
    if target is None or not target.alive:
        world.log("Totter S1 Sunpiercer — no target")
        return
    raw = int(carrier.effective_atk * _S1_ATK_RATIO)
    dealt = target.take_physical(raw)
    world.global_state.total_damage_dealt += dealt
    world.log(f"Totter S1 Sunpiercer — {_S1_ATK_RATIO:.0%} ATK → {target.name}: {dealt}")


register_skill(_S1_TAG, on_start=_s1_on_start)


# --- S2: Prism Break ---
_S2_TAG = "totter_s2_prism_break"
_S2_ATK_RATIO = 1.25
_S2_ASPD = 50.0
_S2_BUFF_TAG = "totter_s2_buff"
_S2_DURATION = 30.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
        value=_S2_ASPD, source_tag=_S2_BUFF_TAG,
    ))
    carrier._totter_s2_active = True
    world.log(f"Totter S2 Prism Break — ATK+{_S2_ATK_RATIO:.0%}, ASPD+{_S2_ASPD:.0f}, +2 hits/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]
    carrier._totter_s2_active = False


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_totter(slot: str = "S2") -> UnitState:
    """Totter E2 max. Talent: ATK+17% when CAMOUFLAGE enemies in range. S1: 220% ATK. S2: ATK+125%/ASPD+50/+2 hits/30s."""
    op = _base_stats()
    op.name = "Totter"
    op.archetype = RoleArchetype.SNIPER_SIEGE
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = BESIEGER_RANGE
    op.talents = [TalentComponent(name="Illuminating Eyes", behavior_tag=_TALENT_TAG)]

    if slot == "S1":
        op.skill = SkillComponent(
            name="Sunpiercer",
            slot="S1",
            sp_cost=3,
            initial_sp=0,
            duration=0.0,
            sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S1_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Prism Break",
            slot="S2",
            sp_cost=40,
            initial_sp=25,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
