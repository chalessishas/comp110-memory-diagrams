"""Kal'tsit + Mon3tr — SUP companion + death burst mechanics.

Tests cover:
  - Mon3tr auto-deployed on Kal'tsit battle start
  - Mon3tr has expected stats (HP, ATK, DEF, block)
  - Mon3tr death burst deals True damage to enemies in Chebyshev-1 radius
  - Mon3tr death burst applies Stun for _MON3TR_STUN_DURATION seconds
  - Enemies outside burst radius are unaffected
  - Mon3tr death burst hits multiple enemies simultaneously (AoE)
  - Kal'tsit dies → Mon3tr despawned
  - Kal'tsit retreats → Mon3tr despawned
  - Mon3tr death burst hits diagonally adjacent enemies (Chebyshev dist=1)
  - No burst when Mon3tr silently despawned via Kal'tsit retreat
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, StatusKind, Faction
from core.systems import register_default_systems
from data.characters.kal_tsit import (
    make_kal_tsit,
    _make_mon3tr,
    _MON3TR_HP, _MON3TR_ATK, _MON3TR_DEF,
    _MON3TR_TRUE_DAMAGE, _MON3TR_STUN_DURATION,
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
# Test 1: Mon3tr auto-deployed on battle start
# ---------------------------------------------------------------------------

def test_mon3tr_deployed_on_battle_start():
    """Kal'tsit's talent deploys Mon3tr automatically on battle start."""
    w = _world()
    kal = make_kal_tsit()
    kal.deployed = True; kal.position = (0.0, 2.0)
    w.add_unit(kal)

    w.tick()  # battle_start fires, Mon3tr is deployed

    mon3tr_id = getattr(kal, "_kal_tsit_mon3tr_id", None)
    assert mon3tr_id is not None, "Kal'tsit must track Mon3tr's unit_id"
    mon3tr = w.unit_by_id(mon3tr_id)
    assert mon3tr is not None, "Mon3tr must exist in world"
    assert mon3tr.alive, "Mon3tr must be alive"
    assert mon3tr.deployed, "Mon3tr must be deployed"
    assert mon3tr.faction == Faction.ALLY, "Mon3tr must be an ally"


# ---------------------------------------------------------------------------
# Test 2: Mon3tr has correct stats
# ---------------------------------------------------------------------------

def test_mon3tr_stats():
    """Mon3tr must have correct HP, ATK, DEF, and block."""
    mon3tr = _make_mon3tr((1.0, 2.0))
    assert mon3tr.max_hp == _MON3TR_HP, f"HP={mon3tr.max_hp} expected {_MON3TR_HP}"
    assert mon3tr.atk == _MON3TR_ATK, f"ATK={mon3tr.atk} expected {_MON3TR_ATK}"
    assert mon3tr.defence == _MON3TR_DEF, f"DEF={mon3tr.defence} expected {_MON3TR_DEF}"
    assert mon3tr.block == 2, f"block={mon3tr.block} expected 2"


# ---------------------------------------------------------------------------
# Test 3: Mon3tr death burst deals True damage to adjacent enemy
# ---------------------------------------------------------------------------

def test_mon3tr_death_burst_true_damage():
    """Mon3tr's death fires a True damage burst to enemies within Chebyshev-1."""
    w = _world()
    kal = make_kal_tsit()
    kal.deployed = True; kal.position = (0.0, 2.0)
    w.add_unit(kal)

    e = _slug(pos=(2, 2), hp=99999)  # adjacent to Mon3tr at (0,2): dist=2
    w.add_unit(e)

    w.tick()  # Mon3tr deployed

    mon3tr_id = getattr(kal, "_kal_tsit_mon3tr_id", None)
    mon3tr = w.unit_by_id(mon3tr_id)
    assert mon3tr is not None

    # Move Mon3tr next to the slug and kill it
    mon3tr.position = (2.0, 2.0)
    hp_before = e.hp
    # Directly kill Mon3tr to trigger on_death
    mon3tr.hp = 0
    mon3tr.alive = False
    mon3tr._just_died = True

    # CLEANUP phase fires on_death
    w.tick()

    # True damage bypasses DEF; slug has DEF=0 so dmg == _MON3TR_TRUE_DAMAGE
    assert e.hp < hp_before, "Mon3tr death burst must deal damage"
    assert hp_before - e.hp == _MON3TR_TRUE_DAMAGE, (
        f"True damage should be exactly {_MON3TR_TRUE_DAMAGE}; "
        f"dealt {hp_before - e.hp}"
    )


# ---------------------------------------------------------------------------
# Test 4: Mon3tr death burst applies Stun
# ---------------------------------------------------------------------------

def test_mon3tr_death_burst_stun():
    """Mon3tr death burst must apply STUN for _MON3TR_STUN_DURATION seconds."""
    w = _world()
    kal = make_kal_tsit()
    kal.deployed = True; kal.position = (0.0, 2.0)
    w.add_unit(kal)

    e = _slug(pos=(1, 2), hp=99999)
    w.add_unit(e)

    w.tick()  # Mon3tr deployed

    mon3tr_id = getattr(kal, "_kal_tsit_mon3tr_id", None)
    mon3tr = w.unit_by_id(mon3tr_id)
    mon3tr.position = (1.0, 2.0)  # same tile as slug

    mon3tr.hp = 0
    mon3tr.alive = False
    mon3tr._just_died = True

    w.tick()  # cleanup fires death burst

    stun_statuses = [s for s in e.statuses if s.kind == StatusKind.STUN]
    assert len(stun_statuses) >= 1, "Enemy must be stunned after Mon3tr death"
    elapsed_now = w.global_state.elapsed
    assert stun_statuses[0].expires_at >= elapsed_now + _MON3TR_STUN_DURATION - 0.2, (
        f"Stun must last {_MON3TR_STUN_DURATION}s; expires_at={stun_statuses[0].expires_at}"
    )


# ---------------------------------------------------------------------------
# Test 5: Enemies outside Chebyshev-1 are not hit
# ---------------------------------------------------------------------------

def test_mon3tr_burst_radius():
    """Enemies at Chebyshev distance > 1 from Mon3tr must not be affected."""
    w = _world()
    kal = make_kal_tsit()
    kal.deployed = True; kal.position = (0.0, 2.0)
    w.add_unit(kal)

    # Close enemy: Chebyshev dist = 1 (should be hit)
    e_close = _slug(pos=(1, 2), hp=99999)
    w.add_unit(e_close)

    # Far enemy: Chebyshev dist = 2 (should NOT be hit)
    e_far = _slug(pos=(2, 2), hp=99999)
    w.add_unit(e_far)

    w.tick()  # Mon3tr deployed at (0,2)

    mon3tr_id = getattr(kal, "_kal_tsit_mon3tr_id", None)
    mon3tr = w.unit_by_id(mon3tr_id)
    mon3tr.position = (0.0, 2.0)  # keep at kal's pos, dist to e_close=1, e_far=2

    mon3tr.hp = 0
    mon3tr.alive = False
    mon3tr._just_died = True

    w.tick()  # death burst fires

    assert e_close.hp < e_close.max_hp, "Enemy at dist=1 must be hit"
    assert e_far.hp == e_far.max_hp, "Enemy at dist=2 must NOT be hit"


# ---------------------------------------------------------------------------
# Test 6: Death burst hits multiple enemies (AoE)
# ---------------------------------------------------------------------------

def test_mon3tr_burst_hits_multiple_enemies():
    """Mon3tr death burst is AoE — all enemies within Chebyshev-1 take damage."""
    w = _world()
    kal = make_kal_tsit()
    kal.deployed = True; kal.position = (2.0, 2.0)
    w.add_unit(kal)

    # Three enemies in 8-tile radius of (2,2)
    e1 = _slug(pos=(1, 2), hp=99999)
    e2 = _slug(pos=(2, 1), hp=99999)
    e3 = _slug(pos=(3, 3), hp=99999)
    w.add_unit(e1); w.add_unit(e2); w.add_unit(e3)

    w.tick()  # Mon3tr deployed

    mon3tr_id = getattr(kal, "_kal_tsit_mon3tr_id", None)
    mon3tr = w.unit_by_id(mon3tr_id)
    mon3tr.position = (2.0, 2.0)

    mon3tr.hp = 0; mon3tr.alive = False; mon3tr._just_died = True
    w.tick()

    assert e1.hp < e1.max_hp, "Enemy at (1,2) must be hit (dist=1 from (2,2))"
    assert e2.hp < e2.max_hp, "Enemy at (2,1) must be hit (dist=1 from (2,2))"
    assert e3.hp < e3.max_hp, "Enemy at (3,3) must be hit (dist=1 from (2,2))"


# ---------------------------------------------------------------------------
# Test 7: Kal'tsit dies → Mon3tr despawned
# ---------------------------------------------------------------------------

def test_kal_tsit_death_despawns_mon3tr():
    """When Kal'tsit dies, Mon3tr must be removed from the field."""
    w = _world()
    kal = make_kal_tsit()
    kal.deployed = True; kal.position = (0.0, 2.0)
    w.add_unit(kal)

    w.tick()  # Mon3tr deployed

    mon3tr_id = getattr(kal, "_kal_tsit_mon3tr_id", None)
    mon3tr = w.unit_by_id(mon3tr_id)
    assert mon3tr.alive, "Mon3tr alive before Kal'tsit death"

    # Kill Kal'tsit
    kal.hp = 0; kal.alive = False; kal._just_died = True

    w.tick()  # cleanup fires on_death for Kal'tsit → despawns Mon3tr

    assert not mon3tr.alive, "Mon3tr must be despawned after Kal'tsit dies"
    assert not mon3tr.deployed, "Mon3tr must be undeployed after Kal'tsit dies"


# ---------------------------------------------------------------------------
# Test 8: Kal'tsit retreats → Mon3tr despawned
# ---------------------------------------------------------------------------

def test_kal_tsit_retreat_despawns_mon3tr():
    """When Kal'tsit retreats, Mon3tr must be removed from the field."""
    w = _world()
    kal = make_kal_tsit()
    kal.deployed = True; kal.position = (0.0, 2.0)
    w.add_unit(kal)

    w.tick()  # Mon3tr deployed

    mon3tr_id = getattr(kal, "_kal_tsit_mon3tr_id", None)
    mon3tr = w.unit_by_id(mon3tr_id)
    assert mon3tr.alive, "Mon3tr alive before retreat"

    w.retreat(kal)  # fires on_retreat → despawns Mon3tr

    assert not mon3tr.alive, "Mon3tr must be despawned after Kal'tsit retreats"


# ---------------------------------------------------------------------------
# Test 9: Diagonal adjacent enemy IS hit by death burst
# ---------------------------------------------------------------------------

def test_mon3tr_death_burst_hits_diagonal_adjacent():
    """Mon3tr death burst hits diagonally adjacent enemies (Chebyshev dist=1)."""
    w = _world()
    kal = make_kal_tsit()
    kal.deployed = True; kal.position = (2.0, 2.0)
    w.add_unit(kal)

    w.tick()  # Mon3tr deployed

    mon3tr_id = getattr(kal, "_kal_tsit_mon3tr_id", None)
    mon3tr = w.unit_by_id(mon3tr_id)
    mon3tr.position = (3.0, 2.0)

    # Diagonal: (4, 3) → Chebyshev dist = max(|4-3|, |3-2|) = 1
    e_diag = _slug(pos=(4, 3), hp=99999)
    e_diag.deployed = True; e_diag.position = (4.0, 3.0)
    w.add_unit(e_diag)

    hp_before = e_diag.hp
    mon3tr.hp = 0; mon3tr.alive = False; mon3tr._just_died = True
    w.tick()

    assert e_diag.hp < hp_before, "Diagonally adjacent enemy must take burst damage"
    stun_statuses = [s for s in e_diag.statuses if s.kind == StatusKind.STUN]
    assert len(stun_statuses) >= 1, "Diagonally adjacent enemy must be stunned"


# ---------------------------------------------------------------------------
# Test 10: No burst when Mon3tr is silently despawned via Kal'tsit retreat
# ---------------------------------------------------------------------------

def test_no_burst_when_mon3tr_despawned_by_retreat():
    """Mon3tr despawned via Kal'tsit retreat must NOT fire its death burst."""
    w = _world()
    kal = make_kal_tsit()
    kal.deployed = True; kal.position = (0.0, 2.0)
    w.add_unit(kal)

    w.tick()  # Mon3tr deployed

    mon3tr_id = getattr(kal, "_kal_tsit_mon3tr_id", None)
    mon3tr = w.unit_by_id(mon3tr_id)
    mon3tr.position = (1.0, 2.0)

    e = _slug(pos=(2, 2), hp=99999)
    e.deployed = True; e.position = (2.0, 2.0)
    w.add_unit(e)

    hp_before = e.hp
    w.retreat(kal)   # _despawn_mon3tr sets alive=False without setting _just_died
    w.tick()         # cleanup fires, but _just_died was NOT set → no burst

    assert e.hp == hp_before, (
        "No True damage burst must fire when Mon3tr is silently despawned via retreat"
    )
