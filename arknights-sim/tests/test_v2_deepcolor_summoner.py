"""Deepcolor — Jellyfish summon + generational re-spawn mechanic.

Tests cover:
  - S2 activation deploys Jellyfish G1 at Deepcolor's position
  - G1 has correct stats (HP, ATK, block)
  - G2 has correct stats (HP, ATK, block)
  - G1 combat death → G2 spawns at same position, alive
  - G2 combat death → no G3 spawned (generation guard)
  - S2 expiry → G1 silently despawned (no re-spawn triggered)
  - Deepcolor retreats → G1 silently despawned
  - G1 death during S2 → G2 registered on Deepcolor, despawned on S2 end
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.deepcolor import (
    make_deepcolor,
    _make_jellyfish,
    _JELLY_G1_HP, _JELLY_G1_ATK,
    _JELLY_G2_HP, _JELLY_G2_ATK,
)


def _world() -> World:
    grid = TileGrid(width=8, height=5)
    for x in range(8):
        for y in range(5):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


# ---------------------------------------------------------------------------
# Test 1: S2 activation deploys G1 jellyfish
# ---------------------------------------------------------------------------

def test_s2_deploys_jellyfish_g1():
    """S2 activation must deploy a Jellyfish G1 at Deepcolor's position."""
    w = _world()
    dc = make_deepcolor(slot="S2")
    dc.deployed = True; dc.position = (2.0, 2.0); dc.atk_cd = 999.0
    dc.skill.sp = float(dc.skill.sp_cost)
    w.add_unit(dc)

    w.tick()  # S2 activates

    assert dc.skill.active_remaining > 0.0, "S2 must be active"
    g1_id = getattr(dc, "_dc_jelly_id", None)
    assert g1_id is not None, "Deepcolor must track G1 jellyfish ID"
    g1 = w.unit_by_id(g1_id)
    assert g1 is not None and g1.alive, "G1 jellyfish must be alive"
    assert g1.deployed, "G1 jellyfish must be deployed"
    assert g1.name == "Jellyfish-G1", "G1 must be named Jellyfish-G1"


# ---------------------------------------------------------------------------
# Test 2: G1 jellyfish stats
# ---------------------------------------------------------------------------

def test_jellyfish_g1_stats():
    """G1 jellyfish must have correct HP, ATK, and block."""
    g1 = _make_jellyfish((0.0, 0.0), generation=1)
    assert g1.max_hp == _JELLY_G1_HP, f"G1 HP={g1.max_hp} expected {_JELLY_G1_HP}"
    assert g1.atk == _JELLY_G1_ATK, f"G1 ATK={g1.atk} expected {_JELLY_G1_ATK}"
    assert g1.block == 0, f"G1 block={g1.block} expected 0"


# ---------------------------------------------------------------------------
# Test 3: G2 jellyfish stats
# ---------------------------------------------------------------------------

def test_jellyfish_g2_stats():
    """G2 jellyfish must have correct HP, ATK, and block."""
    g2 = _make_jellyfish((0.0, 0.0), generation=2)
    assert g2.max_hp == _JELLY_G2_HP, f"G2 HP={g2.max_hp} expected {_JELLY_G2_HP}"
    assert g2.atk == _JELLY_G2_ATK, f"G2 ATK={g2.atk} expected {_JELLY_G2_ATK}"
    assert g2.block == 0, f"G2 block={g2.block} expected 0"


# ---------------------------------------------------------------------------
# Test 4: G1 combat death → G2 spawns at same position
# ---------------------------------------------------------------------------

def test_g1_death_spawns_g2():
    """When G1 Jellyfish dies in combat, a G2 Jellyfish must spawn at same position."""
    w = _world()
    dc = make_deepcolor(slot="S2")
    dc.deployed = True; dc.position = (2.0, 2.0); dc.atk_cd = 999.0
    dc.skill.sp = float(dc.skill.sp_cost)
    w.add_unit(dc)

    w.tick()  # S2 activates, G1 deployed at (2,2)

    g1_id = getattr(dc, "_dc_jelly_id", None)
    g1 = w.unit_by_id(g1_id)
    assert g1 is not None, "G1 must exist"

    # Move G1 and kill it in combat (set _just_died to trigger on_death)
    g1.position = (3.0, 2.0)
    g1.hp = 0
    g1.alive = False
    g1._just_died = True

    w.tick()  # cleanup fires on_death → G2 spawned

    # G2 should now be alive in world
    g2_id = getattr(dc, "_dc_jelly_g2_id", None)
    assert g2_id is not None, "Deepcolor must track G2 jellyfish ID after G1 death"
    g2 = w.unit_by_id(g2_id)
    assert g2 is not None and g2.alive, "G2 jellyfish must be alive after G1 dies"
    assert g2.name == "Jellyfish-G2", "Spawned unit must be Jellyfish-G2"
    # G2 position must match G1's death position
    assert g2.position == (3.0, 2.0), f"G2 must spawn at G1's position; got {g2.position}"


# ---------------------------------------------------------------------------
# Test 5: G2 combat death → no G3 spawned
# ---------------------------------------------------------------------------

def test_g2_death_no_g3():
    """G2 Jellyfish death must NOT spawn a G3 (generation guard)."""
    w = _world()
    dc = make_deepcolor(slot="S2")
    dc.deployed = True; dc.position = (2.0, 2.0); dc.atk_cd = 999.0
    dc.skill.sp = float(dc.skill.sp_cost)
    w.add_unit(dc)

    w.tick()  # S2 activates

    g1_id = getattr(dc, "_dc_jelly_id", None)
    g1 = w.unit_by_id(g1_id)
    g1.position = (2.0, 2.0)

    # Kill G1 in combat → G2 spawns
    g1.hp = 0; g1.alive = False; g1._just_died = True
    w.tick()  # G2 spawned

    g2_id = getattr(dc, "_dc_jelly_g2_id", None)
    assert g2_id is not None, "G2 must have been spawned"
    g2 = w.unit_by_id(g2_id)
    assert g2 is not None and g2.alive, "G2 must be alive"

    jellies_before = {u.unit_id for u in w.units if "Jellyfish" in u.name and u.alive}

    # Kill G2 in combat
    g2.hp = 0; g2.alive = False; g2._just_died = True
    w.tick()  # cleanup fires on_death for G2 — must NOT spawn G3

    new_jellies = [u for u in w.units
                   if "Jellyfish" in u.name and u.alive and u.unit_id not in jellies_before]
    assert len(new_jellies) == 0, f"G2 death must NOT spawn G3; found: {new_jellies}"


# ---------------------------------------------------------------------------
# Test 6: S2 expiry → G1 silently despawned (no re-spawn)
# ---------------------------------------------------------------------------

def test_s2_expiry_despawns_g1_silently():
    """When S2 duration expires, G1 must be despawned without triggering re-spawn."""
    w = _world()
    dc = make_deepcolor(slot="S2")
    dc.deployed = True; dc.position = (2.0, 2.0); dc.atk_cd = 999.0
    dc.skill.sp = float(dc.skill.sp_cost)
    w.add_unit(dc)

    w.tick()  # S2 activates

    g1_id = getattr(dc, "_dc_jelly_id", None)
    g1 = w.unit_by_id(g1_id)
    assert g1 is not None and g1.alive

    # Advance past S2 duration (30s)
    for _ in range(int(TICK_RATE * 31.0)):
        w.tick()

    assert dc.skill.active_remaining == 0.0, "S2 must have ended"
    assert not g1.alive, "G1 must be despawned after S2 ends"
    # No G2 should have been spawned (silent despawn)
    g2_id = getattr(dc, "_dc_jelly_g2_id", None)
    if g2_id is not None:
        g2 = w.unit_by_id(g2_id)
        assert g2 is None or not g2.alive, "G2 must not be alive after S2 silent despawn"


# ---------------------------------------------------------------------------
# Test 7: Deepcolor retreats → G1 silently despawned
# ---------------------------------------------------------------------------

def test_deepcolor_retreat_despawns_g1():
    """When Deepcolor retreats, G1 must be silently despawned (no re-spawn)."""
    w = _world()
    dc = make_deepcolor(slot="S2")
    dc.deployed = True; dc.position = (2.0, 2.0); dc.atk_cd = 999.0
    dc.skill.sp = float(dc.skill.sp_cost)
    w.add_unit(dc)

    w.tick()  # S2 activates

    g1_id = getattr(dc, "_dc_jelly_id", None)
    g1 = w.unit_by_id(g1_id)
    assert g1 is not None and g1.alive, "G1 must be alive before retreat"

    w.retreat(dc)  # fires on_retreat → _despawn_jellies

    assert not g1.alive, "G1 must be despawned after Deepcolor retreats"
    # No G2 should have been spawned by retreat
    g2_id = getattr(dc, "_dc_jelly_g2_id", None)
    if g2_id is not None:
        g2 = w.unit_by_id(g2_id)
        assert g2 is None or not g2.alive, "No G2 after retreat silent despawn"


# ---------------------------------------------------------------------------
# Test 8: G1 dies mid-S2 → G2 registered → S2 end despawns G2
# ---------------------------------------------------------------------------

def test_g2_despawned_on_s2_end():
    """If G1 dies mid-S2 (G2 spawns), S2 expiry must also despawn G2."""
    w = _world()
    dc = make_deepcolor(slot="S2")
    dc.deployed = True; dc.position = (2.0, 2.0); dc.atk_cd = 999.0
    dc.skill.sp = float(dc.skill.sp_cost)
    w.add_unit(dc)

    w.tick()  # S2 activates

    g1_id = getattr(dc, "_dc_jelly_id", None)
    g1 = w.unit_by_id(g1_id)

    # Kill G1 in combat mid-S2
    g1.hp = 0; g1.alive = False; g1._just_died = True
    w.tick()  # G2 spawns

    g2_id = getattr(dc, "_dc_jelly_g2_id", None)
    assert g2_id is not None, "G2 must be registered on Deepcolor after G1 dies"
    g2 = w.unit_by_id(g2_id)
    assert g2 is not None and g2.alive, "G2 must be alive"

    # Advance past S2 duration
    for _ in range(int(TICK_RATE * 31.0)):
        w.tick()

    assert not g2.alive, "G2 must be despawned when S2 ends"
