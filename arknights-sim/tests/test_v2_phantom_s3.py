"""Phantom S3 The Spring — Shadow clone deploy + Arts death burst.

Tests cover:
  - Shadow clone deployed on S3 activation
  - Clone death triggers Arts damage burst to enemies in Chebyshev-1
  - Enemies outside burst radius unaffected
  - AoE hits multiple enemies simultaneously
  - S3 expiry triggers the burst (same as combat death)
  - Clone has correct stats
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction
from core.systems import register_default_systems
from data.characters.phantom import (
    make_phantom, _make_shadow_clone,
    _CLONE_HP, _CLONE_ATK, _BURST_ARTS_DAMAGE, _CLONE_DURATION,
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


def _slug(pos=(3, 2), hp=99999) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 20)
    e.max_hp = hp; e.hp = hp
    e.defence = 0; e.res = 0.0; e.atk = 0
    e.move_speed = 0.0
    return e


# ---------------------------------------------------------------------------
# Test 1: Shadow deployed on S3 activation
# ---------------------------------------------------------------------------

def test_shadow_deployed_on_s3():
    """S3 activation must deploy a Shadow clone at Phantom's position."""
    w = _world()
    ph = make_phantom(slot="S3")
    ph.deployed = True; ph.position = (1.0, 2.0); ph.atk_cd = 999.0
    ph.skill.sp = float(ph.skill.sp_cost)
    w.add_unit(ph)

    e = _slug(pos=(3, 2))
    w.add_unit(e)

    w.tick()  # S3 activates

    assert ph.skill.active_remaining > 0.0, "S3 must be active"
    clone_id = getattr(ph, "_phantom_clone_id", None)
    assert clone_id is not None, "Phantom must track clone ID"
    clone = w.unit_by_id(clone_id)
    assert clone is not None and clone.alive, "Shadow clone must be alive"
    assert clone.faction == Faction.ALLY, "Clone is an ally"
    assert clone.name == "Shadow", "Clone must be named Shadow"


# ---------------------------------------------------------------------------
# Test 2: Clone stats
# ---------------------------------------------------------------------------

def test_shadow_clone_stats():
    """Shadow clone must have expected HP, ATK, and block."""
    clone = _make_shadow_clone((0.0, 0.0))
    assert clone.max_hp == _CLONE_HP, f"Clone HP={clone.max_hp} expected {_CLONE_HP}"
    assert clone.atk == _CLONE_ATK, f"Clone ATK={clone.atk} expected {_CLONE_ATK}"
    assert clone.block == 2, f"Clone block={clone.block} expected 2"


# ---------------------------------------------------------------------------
# Test 3: Clone death triggers Arts damage burst
# ---------------------------------------------------------------------------

def test_shadow_death_burst_arts_damage():
    """When the Shadow dies, enemies within Chebyshev-1 take Arts damage."""
    w = _world()
    ph = make_phantom(slot="S3")
    ph.deployed = True; ph.position = (2.0, 2.0); ph.atk_cd = 999.0
    ph.skill.sp = float(ph.skill.sp_cost)
    w.add_unit(ph)

    e = _slug(pos=(2, 2), hp=99999)  # same tile as phantom (Chebyshev dist 0 from clone)
    e.res = 0.0
    w.add_unit(e)

    w.tick()  # S3 activates, clone deployed at (2,2)

    clone_id = getattr(ph, "_phantom_clone_id", None)
    clone = w.unit_by_id(clone_id)
    clone.position = (2.0, 2.0)  # ensure co-located with slug

    hp_before = e.hp
    # Kill the clone
    clone.hp = 0; clone.alive = False; clone._just_died = True

    w.tick()  # cleanup fires on_death → arts burst

    # Arts damage with RES=0 → full _BURST_ARTS_DAMAGE dealt
    damage_dealt = hp_before - e.hp
    assert damage_dealt == _BURST_ARTS_DAMAGE, (
        f"Arts burst must deal {_BURST_ARTS_DAMAGE}; dealt {damage_dealt}"
    )


# ---------------------------------------------------------------------------
# Test 4: Enemies outside radius unaffected
# ---------------------------------------------------------------------------

def test_shadow_burst_radius():
    """Enemies at Chebyshev distance > 1 must not be affected by the burst."""
    w = _world()
    ph = make_phantom(slot="S3")
    ph.deployed = True; ph.position = (3.0, 2.0); ph.atk_cd = 999.0
    ph.skill.sp = float(ph.skill.sp_cost)
    w.add_unit(ph)

    e_close = _slug(pos=(3, 1), hp=99999)  # dist=1 from (3,2) → hit
    e_far = _slug(pos=(3, 4), hp=99999)    # dist=2 → not hit
    w.add_unit(e_close); w.add_unit(e_far)

    w.tick()  # S3 activates

    clone_id = getattr(ph, "_phantom_clone_id", None)
    clone = w.unit_by_id(clone_id)
    clone.position = (3.0, 2.0)

    clone.hp = 0; clone.alive = False; clone._just_died = True
    w.tick()

    assert e_close.hp < e_close.max_hp, "Enemy at dist=1 must be hit"
    assert e_far.hp == e_far.max_hp, "Enemy at dist=2 must NOT be hit"


# ---------------------------------------------------------------------------
# Test 5: Burst hits multiple enemies (AoE)
# ---------------------------------------------------------------------------

def test_shadow_burst_hits_multiple():
    """Shadow death burst hits all enemies within Chebyshev-1 simultaneously."""
    w = _world()
    ph = make_phantom(slot="S3")
    ph.deployed = True; ph.position = (3.0, 2.0); ph.atk_cd = 999.0
    ph.skill.sp = float(ph.skill.sp_cost)
    w.add_unit(ph)

    e1 = _slug(pos=(2, 2), hp=99999)  # dist=1
    e2 = _slug(pos=(3, 1), hp=99999)  # dist=1
    e3 = _slug(pos=(4, 3), hp=99999)  # dist=1 (Chebyshev: max(1,1)=1)
    for e in [e1, e2, e3]:
        w.add_unit(e)

    w.tick()

    clone_id = getattr(ph, "_phantom_clone_id", None)
    clone = w.unit_by_id(clone_id)
    clone.position = (3.0, 2.0)
    clone.hp = 0; clone.alive = False; clone._just_died = True
    w.tick()

    assert e1.hp < e1.max_hp, "Enemy at (2,2) must be hit"
    assert e2.hp < e2.max_hp, "Enemy at (3,1) must be hit"
    assert e3.hp < e3.max_hp, "Enemy at (4,3) must be hit"


# ---------------------------------------------------------------------------
# Test 6: S3 expiry triggers clone burst (same as combat death)
# ---------------------------------------------------------------------------

def test_s3_expiry_triggers_burst():
    """When S3 duration expires, the clone detonates (same burst as combat death)."""
    w = _world()
    ph = make_phantom(slot="S3")
    ph.deployed = True; ph.position = (2.0, 2.0); ph.atk_cd = 999.0
    ph.skill.sp = float(ph.skill.sp_cost)
    w.add_unit(ph)

    e = _slug(pos=(2, 2), hp=99999)
    e.res = 0.0
    w.add_unit(e)

    w.tick()  # S3 activates

    hp_before = e.hp
    # Advance past skill duration
    for _ in range(int(TICK_RATE * (_CLONE_DURATION + 1.0))):
        w.tick()

    assert ph.skill.active_remaining == 0.0, "S3 must have ended"
    # Burst must have fired during S3 end (or shortly after)
    assert e.hp < hp_before, (
        f"S3 expiry must trigger clone burst; hp_before={hp_before}, now={e.hp}"
    )
