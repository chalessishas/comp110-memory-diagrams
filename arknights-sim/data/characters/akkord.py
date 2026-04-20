"""Akkord (协律) — 4* Caster (Blast Caster archetype).

Archetype trait: Attacks pierce through all enemies along the attack ray,
  dealing full Arts damage to each (CASTER_BLAST blast_pierce=True).

Talent "律脉同构" (Resonant Structure): When ≥1 other ally is deployed in
  Akkord's attack range, ATK +17%. Updated every tick via on_tick hook.

S2 "协律轰鸣" (Harmonic Blast): Instant. Fires a concentrated blast along
  the attack ray, dealing 150% ATK Arts damage to all enemies pierced.
  Applies SLOW (2.0s) to each hit enemy.
  sp_cost=25, initial_sp=10, AUTO_ATTACK, requires_target=True.

Base stats: E2 max, trust 100 (char_4051_akkord).
  HP=1528, ATK=740, DEF=110, RES=20%, atk_interval=2.9s, block=1, cost=32.
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
from core.systems.combat_system import _apply_blast_pierce
from data.characters.generated.akkord import make_akkord as _base_stats


BLAST_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 5) for dy in range(-1, 2)
))

_TALENT_TAG = "akkord_resonant_structure"
_TALENT_ATK_RATIO = 0.17
_TALENT_BUFF_TAG = "akkord_resonant_atk"

_S2_TAG = "akkord_s2_harmonic_blast"
_S2_ATK_MULT = 1.50
_S2_SLOW_DURATION = 2.0
_S2_SLOW_TAG = "akkord_s2_slow"


def _unit_in_range(op: UnitState, other: UnitState) -> bool:
    """Check if other is within op's range_shape tiles."""
    if op.position is None or other.position is None:
        return False
    ox, oy = op.position
    dx = round(other.position[0]) - round(ox)
    dy = round(other.position[1]) - round(oy)
    return (dx, dy) in set(op.range_shape.tiles)


def _talent_on_tick(world, unit: UnitState, dt: float) -> None:
    has_ally = any(
        a is not unit and a.alive and a.deployed and _unit_in_range(unit, a)
        for a in world.allies()
    )
    has_buff = any(b.source_tag == _TALENT_BUFF_TAG for b in unit.buffs)
    if has_ally and not has_buff:
        unit.buffs.append(Buff(
            axis=BuffAxis.ATK, stack=BuffStack.RATIO,
            value=_TALENT_ATK_RATIO, source_tag=_TALENT_BUFF_TAG,
        ))
    elif not has_ally and has_buff:
        unit.buffs = [b for b in unit.buffs if b.source_tag != _TALENT_BUFF_TAG]


register_talent(_TALENT_TAG, on_tick=_talent_on_tick)


def _s2_on_start(world, unit: UnitState) -> None:
    target = getattr(unit, "__target__", None)
    if target is None or not target.alive or unit.position is None:
        return
    raw = unit.effective_atk
    # Primary target at 150% ATK
    blast_raw = int(raw * _S2_ATK_MULT)
    dealt = target.take_arts(blast_raw)
    world.global_state.total_damage_dealt += dealt
    world.log(f"Akkord S2 → {target.name}  dmg={dealt}  ({target.hp}/{target.max_hp})")
    _apply_slow(world, target)

    # Pierce all enemies along the ray at 150% ATK
    _apply_blast_pierce(world, unit, target, raw, atk_multiplier=_S2_ATK_MULT)

    # SLOW all pierced enemies (already applied to primary above)
    _apply_pierce_slow(world, unit, target)


def _apply_slow(world, target: UnitState) -> None:
    elapsed = world.global_state.elapsed
    target.statuses = [s for s in target.statuses if s.source_tag != _S2_SLOW_TAG]
    target.statuses.append(StatusEffect(
        kind=StatusKind.SLOW,
        source_tag=_S2_SLOW_TAG,
        expires_at=elapsed + _S2_SLOW_DURATION,
    ))


def _apply_pierce_slow(world, attacker: UnitState, primary_target: UnitState) -> None:
    """Apply SLOW to all enemies on the blast ray (excluding primary already done)."""
    if primary_target.position is None or attacker.position is None:
        return
    ox, oy = attacker.position
    tx, ty = primary_target.position
    dx, dy = tx - ox, ty - oy
    len_sq = dx * dx + dy * dy
    if len_sq < 1e-6:
        return
    for e in world.enemies():
        if e is primary_target or not e.alive or e.position is None:
            continue
        ex, ey = e.position
        vx, vy = ex - ox, ey - oy
        proj = vx * dx + vy * dy
        if proj <= 0:
            continue
        perp_sq = (vx * vx + vy * vy) - proj * proj / len_sq
        if perp_sq <= 0.25:
            _apply_slow(world, e)


register_skill(_S2_TAG, on_start=_s2_on_start)


def make_akkord(slot: str = "S2") -> UnitState:
    """Akkord E2 max. CASTER_BLAST: pierce all enemies in attack ray. Talent: ATK+17% with ally in range."""
    op = _base_stats()
    op.name = "Akkord"
    op.archetype = RoleArchetype.CASTER_BLAST
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = BLAST_RANGE
    op.attack_range_melee = False
    op.block = 1
    op.cost = 32
    op.blast_pierce = True

    op.talents = [TalentComponent(name="Resonant Structure", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Harmonic Blast",
            slot="S2",
            sp_cost=25,
            initial_sp=10,
            duration=0.0,
            sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    return op
