"""Manticore — passive CAMOUFLAGE talent + S1 self-REGEN via StatusEffect.

Two new mechanics validated here:
  1. CAMOUFLAGE on an operator: enemies deprioritize her for block assignment.
  2. StatusKind.REGEN as a StatusEffect processed by status_decay_system —
     the first practical test of the REGEN path added alongside DOT.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, StatusEffect
from core.types import TileType, TICK_RATE, StatusKind
from core.systems import register_default_systems
from data.characters.manticore import (
    make_manticore, _TALENT_TAG, _CAMO_TAG,
    _S1_REGEN_HPS, _S1_REGEN_DURATION,
)
from data.characters.fang import make_fang
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _slug(pos=(1, 1), hp=9999, defence=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp
    e.atk = 200; e.move_speed = 0.0; e.defence = defence
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Talent registered
# ---------------------------------------------------------------------------

def test_manticore_talent_registered():
    m = make_manticore()
    assert len(m.talents) == 1
    assert m.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: CAMOUFLAGE applied to Manticore each tick while deployed
# ---------------------------------------------------------------------------

def test_camouflage_applied_while_deployed():
    w = _world()
    m = make_manticore(slot=None)
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)

    w.tick()

    assert m.has_status(StatusKind.CAMOUFLAGE), "Manticore must have CAMOUFLAGE while deployed"


# ---------------------------------------------------------------------------
# Test 3: CAMOUFLAGE uses the correct source_tag
# ---------------------------------------------------------------------------

def test_camouflage_source_tag():
    w = _world()
    m = make_manticore(slot=None)
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    w.tick()

    camo = next((s for s in m.statuses if s.kind == StatusKind.CAMOUFLAGE), None)
    assert camo is not None and camo.source_tag == _CAMO_TAG


# ---------------------------------------------------------------------------
# Test 4: CAMOUFLAGE lapses after Manticore is undeployed
# ---------------------------------------------------------------------------

def test_camouflage_lapses_when_undeployed():
    w = _world()
    m = make_manticore(slot=None)
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    w.tick()
    assert m.has_status(StatusKind.CAMOUFLAGE)

    m.deployed = False

    # Tick past the aura expiry (3 ticks is enough)
    for _ in range(3):
        w.tick()

    assert not m.has_status(StatusKind.CAMOUFLAGE), "CAMOUFLAGE must lapse when undeployed"


# ---------------------------------------------------------------------------
# Test 5: CAMOUFLAGE deprioritizes Manticore for block assignment
#         Enemy on same tile as Manticore (CAMOUFLAGE) + Fang (normal):
#         enemy should be blocked by Fang, not Manticore.
# ---------------------------------------------------------------------------

def test_camouflage_block_deprioritized():
    """A CAMOUFLAGE operator is assigned block only after visible operators."""
    w = _world()

    # Give Manticore block=1 for this structural test
    m = make_manticore(slot=None)
    m.deployed = True; m.position = (1.0, 1.0); m.block = 1
    w.add_unit(m)

    guard = make_fang()
    guard.deployed = True; guard.position = (1.0, 1.0); guard.block = 1
    w.add_unit(guard)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    # Tick 1: talent fires → CAMOUFLAGE applied to Manticore.
    # Tick 2: _update_block_assignments re-runs with CAMOUFLAGE already present
    #         → non-CAMOUFLAGE Fang wins block priority.
    w.tick()  # CAMOUFLAGE applied this tick
    w.tick()  # block re-assigned using CAMOUFLAGE sort

    # Fang (no CAMOUFLAGE) should win the block assignment
    assert guard.unit_id in slug.blocked_by_unit_ids, (
        "Guard (no CAMOUFLAGE) must block the enemy, not Manticore"
    )
    assert m.unit_id not in slug.blocked_by_unit_ids, (
        "Manticore (CAMOUFLAGE) must NOT get block priority when another op is available"
    )


# ---------------------------------------------------------------------------
# Test 6: When Manticore is the only blocker, she still gets assigned
# ---------------------------------------------------------------------------

def test_camouflage_only_blocker_still_blocks():
    """If no visible operator is available, CAMOUFLAGE operator takes the block."""
    w = _world()

    m = make_manticore(slot=None)
    m.deployed = True; m.position = (1.0, 1.0); m.block = 1
    w.add_unit(m)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    w.tick()

    assert m.unit_id in slug.blocked_by_unit_ids, (
        "CAMOUFLAGE Manticore must still block when she is the only option"
    )


# ---------------------------------------------------------------------------
# Test 7: S1 applies REGEN StatusEffect to Manticore
# ---------------------------------------------------------------------------

def test_s1_applies_regen():
    w = _world()
    m = make_manticore()
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)

    m.skill.sp = m.skill.sp_cost
    w.tick()

    assert m.skill.active_remaining > 0.0, "S1 must be active"
    assert m.has_status(StatusKind.REGEN), "Manticore must have REGEN while S1 is active"


# ---------------------------------------------------------------------------
# Test 8: REGEN StatusEffect carries correct hps param
# ---------------------------------------------------------------------------

def test_s1_regen_hps_param():
    w = _world()
    m = make_manticore()
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)

    m.skill.sp = m.skill.sp_cost
    w.tick()

    regen = next(s for s in m.statuses if s.kind == StatusKind.REGEN)
    assert regen.params.get("hps") == _S1_REGEN_HPS


# ---------------------------------------------------------------------------
# Test 9: REGEN actually heals Manticore each tick
# ---------------------------------------------------------------------------

def test_s1_regen_heals_each_tick():
    """status_decay_system must process REGEN: Manticore gains HP each tick."""
    w = _world()
    m = make_manticore()
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    # Injure Manticore so there's room to heal
    m.hp = max(1, m.max_hp // 2)
    w.add_unit(m)

    m.skill.sp = m.skill.sp_cost
    w.tick()  # S1 activates → REGEN applied
    assert m.has_status(StatusKind.REGEN)

    hp_after_s1 = m.hp
    w.tick()  # REGEN tick

    expected_heal = max(1, int(_S1_REGEN_HPS * 0.1))   # DT = 0.1
    assert m.hp - hp_after_s1 == expected_heal, (
        f"Expected REGEN tick heal {expected_heal}, got {m.hp - hp_after_s1}"
    )


# ---------------------------------------------------------------------------
# Test 10: REGEN removed when S1 expires
# ---------------------------------------------------------------------------

def test_s1_regen_removed_on_expiry():
    w = _world()
    m = make_manticore()
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)

    m.skill.sp = m.skill.sp_cost
    w.tick()
    assert m.has_status(StatusKind.REGEN)

    for _ in range(int(TICK_RATE * (_S1_REGEN_DURATION + 1))):
        w.tick()

    assert m.skill.active_remaining == 0.0, "S1 must have expired"
    assert not m.has_status(StatusKind.REGEN), "REGEN must be removed after S1 ends"
