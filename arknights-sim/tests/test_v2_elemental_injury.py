"""Elemental Injury system — Necrosis, Erosion, Combustion.

Three element types fill a 0→1000 bar on hits; at 1000 a proc fires:
  NECROSIS:   Arts damage = max(600, 15% max_hp)
  EROSION:    True damage 800 + permanent DEF -100
  COMBUSTION: Arts damage 1200 + permanent RES -20%

Post-proc: 10s immunity window; bar resets to 0.

Tests use inline operators with AttackType.ELEMENTAL + element_type set.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, RangeShape
from core.types import (
    TileType, TICK_RATE, DT, Faction, AttackType, ElementType, BuffAxis,
    ELEMENTAL_PROC_THRESHOLD, ELEMENTAL_IMMUNITY_DURATION,
)
from core.systems import register_default_systems
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=4, height=1)
    for i in range(4):
        grid.set_tile(TileState(x=i, y=0, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _elemental_op(element: ElementType, atk: int = 500) -> UnitState:
    """Operator that deals elemental damage only."""
    return UnitState(
        name=f"Elemental_{element.value}",
        faction=Faction.ALLY,
        max_hp=1000,
        atk=atk,
        defence=0,
        atk_interval=0.1,   # very fast — fire every 2 ticks
        block=0,
        attack_type=AttackType.ELEMENTAL,
        element_type=element,
        attack_range_melee=False,
        range_shape=RangeShape(tiles=tuple((dx, 0) for dx in range(-3, 4))),
        deployed=True,
        position=(0.0, 0.0),
    )


def _slug(pos=(1, 0), hp=99999, defence=0, res=0.0) -> UnitState:
    px = int(pos[0])
    path = [(px, 0)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = defence; e.res = res
    e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), 0.0)
    return e


# ---------------------------------------------------------------------------
# Test 1: Elemental hits charge the bar (no direct HP damage)
# ---------------------------------------------------------------------------

def test_elemental_charges_bar_no_hp_damage():
    """Each elemental hit increases elemental_bars[element] but does not reduce HP."""
    w = _world()
    op = _elemental_op(ElementType.COMBUSTION, atk=100)
    op.atk_cd = 0.0
    w.add_unit(op)

    slug = _slug(hp=9999)
    w.add_unit(slug)

    hp_before = slug.hp
    w.tick()

    assert slug.hp == hp_before, "Elemental hit must not directly reduce HP"
    assert slug.elemental_bars.get("combustion", 0.0) == 100.0, (
        f"Bar should be 100 after one hit; got {slug.elemental_bars}"
    )


# ---------------------------------------------------------------------------
# Test 2: Bar accumulates across multiple hits
# ---------------------------------------------------------------------------

def test_elemental_bar_accumulates():
    """After N hits totalling < 1000, bar holds the running sum."""
    w = _world()
    op = _elemental_op(ElementType.NECROSIS, atk=200)
    op.atk_cd = 0.0
    w.add_unit(op)

    slug = _slug(hp=99999)
    w.add_unit(slug)

    # 4 hits × 200 = 800 (still below 1000)
    for _ in range(4):
        op.atk_cd = 0.0
        w.tick()

    bar = slug.elemental_bars.get("necrosis", 0.0)
    assert abs(bar - 800.0) < 1.0, f"Bar should be ~800 after 4×200 hits; got {bar}"
    assert slug.alive, "Slug should still be alive (no proc yet)"


# ---------------------------------------------------------------------------
# Test 3: COMBUSTION proc — Arts damage + permanent RES debuff
# ---------------------------------------------------------------------------

def test_combustion_proc_arts_damage_and_res_debuff():
    """After bar reaches 1000, Combustion deals 1200 Arts and applies RES -20."""
    w = _world()
    # 2 hits × 500 = 1000 → proc on second hit
    op = _elemental_op(ElementType.COMBUSTION, atk=500)
    op.atk_cd = 0.0
    w.add_unit(op)

    slug = _slug(hp=99999, res=0.0)
    w.add_unit(slug)

    hp_before = slug.hp

    # Two hits
    op.atk_cd = 0.0
    w.tick()
    op.atk_cd = 0.0
    w.tick()

    # Bar should be reset (proc fired)
    bar = slug.elemental_bars.get("combustion", 0.0)
    assert bar == 0.0, f"Bar must reset after proc; got {bar}"

    # Arts damage dealt (1200 Arts on a 0 RES target = 1200 damage)
    assert slug.hp < hp_before, "COMBUSTION proc must deal Arts damage"
    from core.systems.combat_system import _COMBUSTION_PROC_ARTS
    expected_dmg = int(_COMBUSTION_PROC_ARTS * (1 - slug.res / 100))
    assert hp_before - slug.hp >= expected_dmg * 0.9, (
        f"Expected ≥{expected_dmg * 0.9:.0f} Combustion proc damage; got {hp_before - slug.hp}"
    )

    # Permanent RES debuff applied
    res_buffs = [b for b in slug.buffs if b.axis == BuffAxis.RES and b.value < 0]
    assert len(res_buffs) >= 1, "COMBUSTION must apply RES debuff"
    assert any(abs(b.value - (-20.0)) < 0.1 for b in res_buffs), (
        f"RES debuff should be -20; got {[b.value for b in res_buffs]}"
    )


# ---------------------------------------------------------------------------
# Test 4: EROSION proc — True damage + permanent DEF debuff
# ---------------------------------------------------------------------------

def test_erosion_proc_true_damage_and_def_debuff():
    """After bar reaches 1000, Erosion deals 800 true damage and DEF -100."""
    w = _world()
    op = _elemental_op(ElementType.EROSION, atk=500)
    op.atk_cd = 0.0
    w.add_unit(op)

    slug = _slug(hp=99999, defence=500)
    w.add_unit(slug)

    hp_before = slug.hp

    op.atk_cd = 0.0
    w.tick()
    op.atk_cd = 0.0
    w.tick()

    assert slug.elemental_bars.get("erosion", 0.0) == 0.0, "Bar must reset"

    from core.systems.combat_system import _EROSION_PROC_PHYS
    assert hp_before - slug.hp >= int(_EROSION_PROC_PHYS * 0.9), (
        f"EROSION must deal ≥{_EROSION_PROC_PHYS * 0.9:.0f} true damage"
    )

    def_buffs = [b for b in slug.buffs if b.axis == BuffAxis.DEF and b.value < 0]
    assert len(def_buffs) >= 1, "EROSION must apply DEF debuff"
    from core.systems.combat_system import _EROSION_DEF_DEBUFF
    assert any(abs(b.value - (-_EROSION_DEF_DEBUFF)) < 0.1 for b in def_buffs), (
        f"DEF debuff should be -{_EROSION_DEF_DEBUFF}"
    )


# ---------------------------------------------------------------------------
# Test 5: NECROSIS proc — Arts damage = max(600, 15% max HP)
# ---------------------------------------------------------------------------

def test_necrosis_proc_arts_damage():
    """Necrosis proc deals max(600, 15% max_hp) Arts damage."""
    w = _world()
    op = _elemental_op(ElementType.NECROSIS, atk=500)
    op.atk_cd = 0.0
    w.add_unit(op)

    slug = _slug(hp=10000, res=0.0)
    w.add_unit(slug)

    hp_before = slug.hp

    op.atk_cd = 0.0
    w.tick()
    op.atk_cd = 0.0
    w.tick()

    from core.systems.combat_system import _NECROSIS_PROC_HP_RATIO, _NECROSIS_PROC_MIN
    expected_dmg = max(_NECROSIS_PROC_MIN, int(slug.max_hp * _NECROSIS_PROC_HP_RATIO))
    assert hp_before - slug.hp >= int(expected_dmg * 0.9), (
        f"NECROSIS proc damage wrong: expected ≥{expected_dmg * 0.9:.0f}, "
        f"got {hp_before - slug.hp}"
    )


# ---------------------------------------------------------------------------
# Test 6: Immunity window — no bar accumulation for 10s after proc
# ---------------------------------------------------------------------------

def test_immunity_window_after_proc():
    """After a proc, further elemental hits do NOT charge the bar for 10s."""
    w = _world()
    op = _elemental_op(ElementType.COMBUSTION, atk=500)
    op.atk_cd = 0.0
    w.add_unit(op)

    slug = _slug(hp=99999)
    w.add_unit(slug)

    # Trigger proc (2 hits × 500 = 1000)
    op.atk_cd = 0.0
    w.tick()
    op.atk_cd = 0.0
    w.tick()
    assert slug.elemental_bars.get("combustion", 0.0) == 0.0, "Proc must reset bar"

    hp_after_proc = slug.hp

    # Hit again immediately — should be immune
    op.atk_cd = 0.0
    w.tick()

    bar_after_immune_hit = slug.elemental_bars.get("combustion", 0.0)
    assert bar_after_immune_hit == 0.0, (
        f"Bar must stay 0 during immunity; got {bar_after_immune_hit}"
    )
    # No second proc damage either
    assert slug.hp == hp_after_proc or slug.hp > hp_after_proc - 10, (
        "No additional proc damage during immunity window"
    )


# ---------------------------------------------------------------------------
# Test 7: Immunity expires — bar charges again after 10s
# ---------------------------------------------------------------------------

def test_immunity_expires_after_duration():
    """After 10s immunity expires, bar can be charged again."""
    w = _world()
    op = _elemental_op(ElementType.NECROSIS, atk=500)
    op.atk_cd = 999.0  # freeze attacks
    w.add_unit(op)

    slug = _slug(hp=99999)
    w.add_unit(slug)

    # Manually set immunity as if proc just fired
    slug.elemental_immune_until["necrosis"] = w.global_state.elapsed + ELEMENTAL_IMMUNITY_DURATION

    # Advance past immunity window
    for _ in range(int(TICK_RATE * (ELEMENTAL_IMMUNITY_DURATION + 1))):
        w.tick()

    # Allow an attack
    op.atk_cd = 0.0
    w.tick()

    bar = slug.elemental_bars.get("necrosis", 0.0)
    assert bar > 0.0, f"After immunity expires, bar must charge; got {bar}"


# ---------------------------------------------------------------------------
# Test 8: COMBUSTION RES debuff reduces future Arts damage taken
# ---------------------------------------------------------------------------

def test_combustion_res_debuff_reduces_arts_damage():
    """After COMBUSTION proc, target's effective_res drops, so future Arts damage increases."""
    w = _world()
    op = _elemental_op(ElementType.COMBUSTION, atk=500)
    op.atk_cd = 0.0
    w.add_unit(op)

    # Target with 30 base RES
    slug = _slug(hp=99999, res=30.0)
    w.add_unit(slug)

    res_before = slug.res

    # Trigger proc
    op.atk_cd = 0.0
    w.tick()
    op.atk_cd = 0.0
    w.tick()

    from core.systems.combat_system import _COMBUSTION_RES_DEBUFF
    res_after = slug.effective_stat(BuffAxis.RES, base=slug.res)
    expected_res = res_before - _COMBUSTION_RES_DEBUFF
    assert abs(res_after - expected_res) < 0.1, (
        f"Post-Combustion RES should be {expected_res}, got {res_after}"
    )
