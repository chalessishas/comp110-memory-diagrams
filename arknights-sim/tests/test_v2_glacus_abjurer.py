"""Glacius — SUP_ABJURER: passive RES aura to allies + COLD/FREEZE on hit.

SUP_ABJURER trait:
  - Allies within range gain +_AURA_RES_BONUS flat RES while Glacius is deployed
  - Aura maintained via on_tick (refreshed with short expires_at each tick)

Talent "Frost Guard":
  - Each attack applies COLD (3s) to primary target
  - If target already has COLD, upgrade to FREEZE (2s)

S2 "Arctic Barrier": 20s duration
  - ATK +40%
  - All attacks apply FREEZE directly (skip COLD step)
  - Both revert on skill end

Tests cover:
  - Archetype is SUP_ABJURER, attack_type=ARTS, block=1
  - ARTS damage reduced by RES (not DEF)
  - Talent applies COLD on first hit
  - Talent upgrades COLD to FREEZE on second hit
  - COLD expires after duration
  - Ally in range receives RES aura buff
  - Out-of-range ally does NOT receive RES aura
  - S2 applies ATK+40% buff
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, RangeShape
from core.types import (
    TileType, TICK_RATE, DT, Faction, AttackType, RoleArchetype, StatusKind,
)
from core.systems import register_default_systems
from data.characters.glacus import (
    make_glacus,
    _AURA_RES_BONUS, _COLD_DURATION, _FREEZE_DURATION,
    _S2_ATK_RATIO, _S2_DURATION, _AURA_RES_BUFF_TAG,
)
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=8, height=5)
    for x in range(8):
        for y in range(5):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _slug(pos=(2, 2), hp=99999, defence=0, res=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = defence; e.res = float(res)
    e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


def _ally(pos=(1, 2), res=0.0) -> UnitState:
    return UnitState(
        name="Ally",
        faction=Faction.ALLY,
        max_hp=2000, hp=2000, atk=0,
        defence=0, res=res,
        atk_interval=999.0, block=1,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=False,
        range_shape=RangeShape(tiles=()),
        deployed=True, position=(float(pos[0]), float(pos[1])),
    )


# ---------------------------------------------------------------------------
# Test 1: Archetype and base stats
# ---------------------------------------------------------------------------

def test_glacus_archetype():
    g = make_glacus()
    assert g.archetype == RoleArchetype.SUP_ABJURER
    assert g.attack_type == AttackType.ARTS
    assert g.block == 1


# ---------------------------------------------------------------------------
# Test 2: ARTS damage reduced by RES
# ---------------------------------------------------------------------------

def test_arts_damage_reduced_by_res():
    """ARTS attacks are mitigated by enemy RES."""
    w1 = _world()
    g1 = make_glacus()
    g1.deployed = True; g1.position = (0.0, 2.0); g1.atk_cd = 0.0
    w1.add_unit(g1)
    e_no = _slug(pos=(2, 2), res=0)
    w1.add_unit(e_no)
    w1.tick()
    dmg_no_res = 99999 - e_no.hp

    w2 = _world()
    g2 = make_glacus()
    g2.deployed = True; g2.position = (0.0, 2.0); g2.atk_cd = 0.0
    w2.add_unit(g2)
    e_hi = _slug(pos=(2, 2), res=60)
    w2.add_unit(e_hi)
    w2.tick()
    dmg_hi_res = 99999 - e_hi.hp

    assert dmg_no_res > 0, "Must deal damage"
    assert dmg_no_res > dmg_hi_res, (
        f"ARTS damage must be reduced by RES; RES=0:{dmg_no_res}, RES=60:{dmg_hi_res}"
    )


# ---------------------------------------------------------------------------
# Test 3: Talent applies COLD on first hit
# ---------------------------------------------------------------------------

def test_talent_applies_cold_on_hit():
    """First attack applies COLD status to primary target."""
    w = _world()
    g = make_glacus()
    g.deployed = True; g.position = (0.0, 2.0); g.atk_cd = 0.0
    w.add_unit(g)

    enemy = _slug(pos=(2, 2))
    w.add_unit(enemy)

    w.tick()

    assert enemy.has_status(StatusKind.COLD), (
        f"First hit must apply COLD; statuses={[s.kind for s in enemy.statuses]}"
    )
    assert not enemy.has_status(StatusKind.FREEZE), "Should not be FREEZE yet (only 1 hit)"


# ---------------------------------------------------------------------------
# Test 4: Talent upgrades COLD to FREEZE on second hit
# ---------------------------------------------------------------------------

def test_talent_cold_upgrades_to_freeze():
    """Second hit while target is already COLD upgrades to FREEZE."""
    w = _world()
    g = make_glacus()
    g.deployed = True; g.position = (0.0, 2.0); g.atk_cd = 0.0
    w.add_unit(g)

    enemy = _slug(pos=(2, 2))
    w.add_unit(enemy)

    w.tick()
    assert enemy.has_status(StatusKind.COLD)

    g.atk_cd = 0.0  # reset to fire again immediately
    w.tick()

    assert enemy.has_status(StatusKind.FREEZE), (
        "Second hit while COLD must upgrade to FREEZE"
    )


# ---------------------------------------------------------------------------
# Test 5: COLD expires after duration
# ---------------------------------------------------------------------------

def test_cold_expires():
    """COLD status must expire after _COLD_DURATION seconds."""
    w = _world()
    g = make_glacus()
    g.deployed = True; g.position = (0.0, 2.0); g.atk_cd = 0.0
    w.add_unit(g)

    enemy = _slug(pos=(2, 2))
    w.add_unit(enemy)

    w.tick()
    assert enemy.has_status(StatusKind.COLD)

    g.atk_cd = 999.0  # prevent re-application
    for _ in range(int(TICK_RATE * (_COLD_DURATION + 1))):
        w.tick()

    assert not enemy.has_status(StatusKind.COLD), (
        f"COLD must expire after {_COLD_DURATION}s"
    )


# ---------------------------------------------------------------------------
# Test 6: Ally in range receives RES aura buff
# ---------------------------------------------------------------------------

def test_aura_buffs_ally_in_range():
    """Ally within Glacius's range gets +_AURA_RES_BONUS RES from the aura."""
    w = _world()
    g = make_glacus()
    g.deployed = True; g.position = (0.0, 2.0); g.atk_cd = 999.0
    w.add_unit(g)

    ally = _ally(pos=(1, 2), res=0.0)
    w.add_unit(ally)

    base_res = ally.effective_stat(
        __import__('core.types', fromlist=['BuffAxis']).BuffAxis.RES,
        base=ally.res
    )
    w.tick()

    res_buffed = ally.effective_stat(
        __import__('core.types', fromlist=['BuffAxis']).BuffAxis.RES,
        base=ally.res
    )
    assert res_buffed > base_res, (
        f"Ally in range must get RES buff; base={base_res}, buffed={res_buffed}"
    )
    aura_buffs = [b for b in ally.buffs if b.source_tag == _AURA_RES_BUFF_TAG]
    assert len(aura_buffs) == 1, "Must have exactly 1 aura buff"
    assert abs(aura_buffs[0].value - _AURA_RES_BONUS) < 0.1


# ---------------------------------------------------------------------------
# Test 7: Out-of-range ally does NOT receive RES aura
# ---------------------------------------------------------------------------

def test_aura_does_not_buff_out_of_range():
    """Ally far from Glacius must not receive the RES aura buff."""
    w = _world()
    g = make_glacus()
    g.deployed = True; g.position = (0.0, 2.0); g.atk_cd = 999.0
    w.add_unit(g)

    far_ally = _ally(pos=(7, 2), res=0.0)  # 7 tiles away — outside range (max 3)
    w.add_unit(far_ally)

    for _ in range(3):
        w.tick()

    aura_buffs = [b for b in far_ally.buffs if b.source_tag == _AURA_RES_BUFF_TAG]
    assert len(aura_buffs) == 0, (
        f"Out-of-range ally must NOT receive aura; buffs={aura_buffs}"
    )


# ---------------------------------------------------------------------------
# Test 8: S2 applies ATK+40%
# ---------------------------------------------------------------------------

def test_s2_atk_buff():
    """During S2, effective_atk must be base × 1.4."""
    w = _world()
    g = make_glacus()
    g.deployed = True; g.position = (0.0, 2.0)
    w.add_unit(g)

    e = _slug(pos=(2, 2))
    w.add_unit(e)

    base_atk = g.effective_atk
    g.skill.sp = float(g.skill.sp_cost)
    w.tick()

    assert g.skill.active_remaining > 0.0, "S2 must be active"
    expected = int(base_atk * (1 + _S2_ATK_RATIO))
    assert abs(g.effective_atk - expected) <= 2, (
        f"S2 ATK must be base×{1 + _S2_ATK_RATIO}; base={base_atk}, "
        f"expected={expected}, got={g.effective_atk}"
    )
