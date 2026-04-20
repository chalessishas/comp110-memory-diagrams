"""Cross-operator COLD chain: Kroos2 + Gnosis cooperative FREEZE.

Scenario: Kroos2 applies COLD on first hit (source=kroos2_cold).
          Gnosis then hits the same enemy → sees has_status(COLD) = True
          → upgrades to FREEZE (source=gnosis_freeze).

This validates the cross-operator status stacking contract:
  has_status() checks by KIND, not by source_tag.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, StatusKind
from core.systems import register_default_systems
from data.characters.kroos2 import make_kroos2
from data.characters.gnosis import make_gnosis
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


def _slug(pos=(1, 1), hp=999999) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp
    e.atk = 0; e.move_speed = 0.0; e.defence = 0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Kroos2 first hit applies COLD (sanity check in multi-op world)
# ---------------------------------------------------------------------------

def test_kroos2_applies_cold_in_multi_op_world():
    """Kroos2 hit applies COLD even when Gnosis is also deployed."""
    w = _world()

    k = make_kroos2(slot=None)
    k.deployed = True; k.position = (0.0, 1.0); k.atk_cd = 0.0
    w.add_unit(k)

    g = make_gnosis(slot=None)
    g.deployed = True; g.position = (0.0, 0.0); g.atk_cd = 999.0
    w.add_unit(g)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    w.tick()  # Kroos2 attacks (Gnosis is locked out due to high atk_cd)

    assert slug.has_status(StatusKind.COLD), (
        "Kroos2 must apply COLD on first hit"
    )
    assert not slug.has_status(StatusKind.FREEZE), (
        "FREEZE must NOT appear on first hit"
    )


# ---------------------------------------------------------------------------
# Test 2: Gnosis second hit upgrades Kroos2's COLD to FREEZE
# ---------------------------------------------------------------------------

def test_gnosis_upgrades_kroos2_cold_to_freeze():
    """Gnosis hit on a Kroos2-COLD-ed target upgrades to FREEZE (cross-op chain)."""
    w = _world()

    # Kroos2 attacks first
    k = make_kroos2(slot=None)
    k.deployed = True; k.position = (0.0, 1.0); k.atk_cd = 0.0
    w.add_unit(k)

    # Gnosis will attack after Kroos2 (higher atk_cd, fires second)
    g = make_gnosis(slot=None)
    g.deployed = True; g.position = (0.0, 0.0); g.atk_cd = 0.5
    w.add_unit(g)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    # Tick until Kroos2 has fired at least once
    w.tick()  # Kroos2 fires → COLD applied
    assert slug.has_status(StatusKind.COLD), "COLD must be present after Kroos2 hit"

    # Advance until Gnosis fires (atk_cd=0.5, so 5 ticks at DT=0.1)
    for _ in range(int(0.5 * TICK_RATE) + 2):
        w.tick()

    assert slug.has_status(StatusKind.FREEZE), (
        "FREEZE must be applied when Gnosis hits a COLD target (cross-op upgrade)"
    )
    assert not slug.has_status(StatusKind.COLD), (
        "COLD must be cleared when FREEZE is applied"
    )


# ---------------------------------------------------------------------------
# Test 3: FREEZE from cross-op chain blocks action
# ---------------------------------------------------------------------------

def test_cross_op_freeze_blocks_action():
    """Enemy FROZEn by Gnosis (after Kroos2 COLD) cannot act."""
    w = _world()

    k = make_kroos2(slot=None)
    k.deployed = True; k.position = (0.0, 1.0); k.atk_cd = 0.0
    w.add_unit(k)

    g = make_gnosis(slot=None)
    g.deployed = True; g.position = (0.0, 0.0); g.atk_cd = 0.5
    w.add_unit(g)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    w.tick()  # Kroos2 → COLD

    for _ in range(int(0.5 * TICK_RATE) + 2):
        w.tick()  # Gnosis → FREEZE

    assert slug.has_status(StatusKind.FREEZE)
    assert not slug.can_act(), "FROZEN enemy must not be able to act"


# ---------------------------------------------------------------------------
# Test 4: Kroos2-COLD + Gnosis-FREEZE chain coexists with Gnosis RES_DOWN
# ---------------------------------------------------------------------------

def test_cross_op_freeze_coexists_with_res_down():
    """When Gnosis upgrades to FREEZE, RES_DOWN is also applied in the same hit."""
    w = _world()

    k = make_kroos2(slot=None)
    k.deployed = True; k.position = (0.0, 1.0); k.atk_cd = 0.0
    w.add_unit(k)

    g = make_gnosis(slot=None)
    g.deployed = True; g.position = (0.0, 0.0); g.atk_cd = 0.5
    w.add_unit(g)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    w.tick()  # Kroos2 → COLD

    for _ in range(int(0.5 * TICK_RATE) + 2):
        w.tick()  # Gnosis → FREEZE + RES_DOWN

    assert slug.has_status(StatusKind.FREEZE), "FREEZE must be applied"
    assert slug.has_status(StatusKind.RES_DOWN), (
        "RES_DOWN must also be applied by Gnosis's hit (same talent callback)"
    )


# ---------------------------------------------------------------------------
# Test 5: Reverse order — Gnosis COLD first, Kroos2 upgrades to FREEZE
# ---------------------------------------------------------------------------

def test_gnosis_cold_first_kroos2_upgrades_to_freeze():
    """If Gnosis hits first (COLD), Kroos2 second hit upgrades to FREEZE."""
    w = _world()

    # Gnosis fires first
    g = make_gnosis(slot=None)
    g.deployed = True; g.position = (0.0, 0.0); g.atk_cd = 0.0
    w.add_unit(g)

    # Kroos2 fires second
    k = make_kroos2(slot=None)
    k.deployed = True; k.position = (0.0, 1.0); k.atk_cd = 0.5
    w.add_unit(k)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    w.tick()  # Gnosis → COLD + RES_DOWN
    assert slug.has_status(StatusKind.COLD), "Gnosis must apply COLD on first hit"

    for _ in range(int(0.5 * TICK_RATE) + 2):
        w.tick()  # Kroos2 → detects COLD → upgrades to FREEZE

    assert slug.has_status(StatusKind.FREEZE), (
        "Kroos2 must upgrade Gnosis's COLD to FREEZE (cross-op, reverse order)"
    )
