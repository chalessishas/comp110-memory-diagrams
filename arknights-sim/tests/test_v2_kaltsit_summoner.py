"""Kal'tsit — SUP_SUMMONER: spawns Mon3tr tank on deploy.

Talent "Non-Damaging Restructuring" (on Mon3tr):
  When Mon3tr dies, deal True damage (30% Mon3tr max HP) + 3s Stun to
  all enemies within Chebyshev distance 1 of Mon3tr's position.

Lifecycle:
  - Kal'tsit spawns Mon3tr on battle_start.
  - Kal'tsit dies/retreats → Mon3tr despawns.
  - Mon3tr dies → AoE burst to nearby enemies.

Tests cover:
  - Archetype SUP_SUMMONER
  - Mon3tr spawned on deploy
  - Mon3tr has correct stats (HP, ATK, DEF)
  - Mon3tr is faction=ALLY, melee, block=3
  - Mon3tr on_death: True damage to adjacent enemies
  - Mon3tr on_death: STUN applied to adjacent enemies for 3s
  - Mon3tr on_death: out-of-range enemies NOT affected
  - Kal'tsit on_death: Mon3tr despawns
  - Kal'tsit on_retreat: Mon3tr despawns
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, RoleArchetype, StatusKind
from core.systems import register_default_systems
from data.characters.kaltsit import (
    make_kaltsit,
    _KALTSIT_TALENT_TAG, _MONSTR_TALENT_TAG,
    _BURST_DAMAGE_RATIO, _BURST_STUN_DURATION, _BURST_STUN_TAG,
    _KALTSIT_MONSTR_ATTR,
    _MONSTR_HP, _MONSTR_ATK, _MONSTR_DEF,
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
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = 0; e.res = 0.0; e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Archetype SUP_SUMMONER
# ---------------------------------------------------------------------------

def test_kaltsit_archetype():
    k = make_kaltsit()
    assert k.archetype == RoleArchetype.SUP_SUMMONER
    assert k.block == 1
    assert len(k.talents) == 1
    assert k.talents[0].behavior_tag == _KALTSIT_TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: Mon3tr spawned on deploy
# ---------------------------------------------------------------------------

def test_monstr_spawned_on_deploy():
    """Kal'tsit's talent must spawn Mon3tr when added to the world."""
    w = _world()
    k = make_kaltsit()
    k.deployed = True; k.position = (0.0, 2.0)

    allies_before = len(w.allies())
    w.add_unit(k)

    allies_after = len(w.allies())
    assert allies_after == allies_before + 2, (
        f"Must have Kal'tsit + Mon3tr; allies={allies_after}"
    )
    monstr = next((u for u in w.allies() if u.name == "Mon3tr"), None)
    assert monstr is not None, "Mon3tr must be in allies"


# ---------------------------------------------------------------------------
# Test 3: Mon3tr has correct stats
# ---------------------------------------------------------------------------

def test_monstr_stats():
    """Mon3tr must have correct HP, ATK, DEF values."""
    w = _world()
    k = make_kaltsit()
    k.deployed = True; k.position = (0.0, 2.0)
    w.add_unit(k)

    monstr = next(u for u in w.allies() if u.name == "Mon3tr")
    assert monstr.max_hp == _MONSTR_HP, f"HP must be {_MONSTR_HP}; got {monstr.max_hp}"
    assert monstr.atk == _MONSTR_ATK, f"ATK must be {_MONSTR_ATK}; got {monstr.atk}"
    assert monstr.defence == _MONSTR_DEF, f"DEF must be {_MONSTR_DEF}; got {monstr.defence}"


# ---------------------------------------------------------------------------
# Test 4: Mon3tr is faction=ALLY, melee, block=3
# ---------------------------------------------------------------------------

def test_monstr_is_allied_tank():
    """Mon3tr must be faction=ALLY, melee, block=3."""
    w = _world()
    k = make_kaltsit()
    k.deployed = True; k.position = (0.0, 2.0)
    w.add_unit(k)

    monstr = next(u for u in w.allies() if u.name == "Mon3tr")
    assert monstr.faction == Faction.ALLY
    assert monstr.attack_range_melee is True, "Mon3tr must be melee"
    assert monstr.block == 3, f"Mon3tr block must be 3; got {monstr.block}"
    assert len(monstr.talents) == 1
    assert monstr.talents[0].behavior_tag == _MONSTR_TALENT_TAG


# ---------------------------------------------------------------------------
# Test 5: Mon3tr on_death — True damage to adjacent enemy
# ---------------------------------------------------------------------------

def test_monstr_death_burst_deals_true_damage():
    """When Mon3tr dies, adjacent enemies take True damage = 30% Mon3tr max HP."""
    w = _world()
    k = make_kaltsit(slot=None)
    k.deployed = True; k.position = (0.0, 2.0)
    w.add_unit(k)

    monstr = next(u for u in w.units if u.name == "Mon3tr")
    monstr.position = (3.0, 2.0)  # place Mon3tr explicitly

    # Enemy adjacent to Mon3tr at (4, 2) → Chebyshev dist = 1
    e_adj = _slug(pos=(4, 2))
    w.add_unit(e_adj)

    hp_before = e_adj.hp
    expected_true_dmg = int(_MONSTR_HP * _BURST_DAMAGE_RATIO)

    # Kill Mon3tr → _just_died set
    monstr.take_damage(monstr.max_hp + 1)
    assert not monstr.alive

    # Tick so cleanup_system fires on_death
    w.tick()

    damage_dealt = hp_before - e_adj.hp
    assert damage_dealt == expected_true_dmg, (
        f"Mon3tr burst True damage must be {expected_true_dmg}; dealt={damage_dealt}"
    )


# ---------------------------------------------------------------------------
# Test 6: Mon3tr on_death — STUN applied to adjacent enemy
# ---------------------------------------------------------------------------

def test_monstr_death_burst_stuns_adjacent_enemy():
    """Adjacent enemies must be stunned for 3s after Mon3tr dies."""
    w = _world()
    k = make_kaltsit(slot=None)
    k.deployed = True; k.position = (0.0, 2.0)
    w.add_unit(k)

    monstr = next(u for u in w.units if u.name == "Mon3tr")
    monstr.position = (3.0, 2.0)

    e_adj = _slug(pos=(4, 2))
    w.add_unit(e_adj)

    monstr.take_damage(monstr.max_hp + 1)
    w.tick()

    stun_effects = [s for s in e_adj.statuses if s.kind == StatusKind.STUN]
    assert len(stun_effects) == 1, (
        f"Adjacent enemy must have 1 STUN status; found {len(stun_effects)}"
    )
    assert stun_effects[0].source_tag == _BURST_STUN_TAG
    stun_remaining = stun_effects[0].expires_at - w.global_state.elapsed
    assert stun_remaining >= _BURST_STUN_DURATION - 0.1, (
        f"STUN must last ~{_BURST_STUN_DURATION}s; remaining={stun_remaining:.2f}"
    )


# ---------------------------------------------------------------------------
# Test 7: Mon3tr on_death — out-of-range enemies NOT affected
# ---------------------------------------------------------------------------

def test_monstr_death_burst_does_not_hit_distant_enemy():
    """Enemies beyond Chebyshev distance 1 must NOT be affected by the burst."""
    w = _world()
    k = make_kaltsit(slot=None)
    k.deployed = True; k.position = (0.0, 2.0)
    w.add_unit(k)

    monstr = next(u for u in w.units if u.name == "Mon3tr")
    monstr.position = (3.0, 2.0)

    # Enemy at Chebyshev dist = 2 from Mon3tr
    e_far = _slug(pos=(5, 2))
    w.add_unit(e_far)

    hp_before = e_far.hp
    monstr.take_damage(monstr.max_hp + 1)
    w.tick()

    assert e_far.hp == hp_before, (
        f"Far enemy must NOT take burst damage; hp={e_far.hp}"
    )
    assert not any(s.source_tag == _BURST_STUN_TAG for s in e_far.statuses), (
        "Far enemy must NOT be stunned by burst"
    )


# ---------------------------------------------------------------------------
# Test 8: Mon3tr on_death — diagonal adjacent enemy IS affected
# ---------------------------------------------------------------------------

def test_monstr_death_burst_hits_diagonal_adjacent():
    """Diagonally adjacent enemies (Chebyshev dist=1) must be hit by the burst."""
    w = _world()
    k = make_kaltsit(slot=None)
    k.deployed = True; k.position = (0.0, 2.0)
    w.add_unit(k)

    monstr = next(u for u in w.units if u.name == "Mon3tr")
    monstr.position = (3.0, 2.0)

    # Diagonal: (4, 3) → Chebyshev dist = max(|4-3|, |3-2|) = 1
    e_diag = _slug(pos=(4, 3))
    w.add_unit(e_diag)

    hp_before = e_diag.hp
    monstr.take_damage(monstr.max_hp + 1)
    w.tick()

    assert e_diag.hp < hp_before, "Diagonally adjacent enemy must take burst damage"
    assert any(s.kind == StatusKind.STUN for s in e_diag.statuses), (
        "Diagonally adjacent enemy must be stunned"
    )


# ---------------------------------------------------------------------------
# Test 9: Kal'tsit on_death — Mon3tr despawns
# ---------------------------------------------------------------------------

def test_monstr_despawns_when_kaltsit_dies():
    """When Kal'tsit is killed, Mon3tr must be despawned."""
    w = _world()
    k = make_kaltsit(slot=None)
    k.deployed = True; k.position = (0.0, 2.0)
    w.add_unit(k)

    monstr = next(u for u in w.units if u.name == "Mon3tr")
    assert monstr.alive, "Mon3tr must be alive before Kal'tsit's death"

    k.take_damage(k.max_hp + 1000)
    assert not k.alive

    w.tick()  # cleanup_system dispatches on_death

    assert not monstr.alive or not monstr.deployed, (
        f"Mon3tr must despawn when Kal'tsit dies; alive={monstr.alive}, deployed={monstr.deployed}"
    )


# ---------------------------------------------------------------------------
# Test 10: Kal'tsit on_retreat — Mon3tr despawns
# ---------------------------------------------------------------------------

def test_monstr_despawns_when_kaltsit_retreats():
    """When Kal'tsit is retreated, Mon3tr must be despawned."""
    w = _world()
    k = make_kaltsit(slot=None)
    k.deployed = True; k.position = (0.0, 2.0)
    w.add_unit(k)

    monstr = next(u for u in w.units if u.name == "Mon3tr")
    assert monstr.alive, "Mon3tr must be alive before retreat"

    w.retreat(k)

    assert not k.deployed, "Kal'tsit must no longer be deployed"
    assert not monstr.alive or not monstr.deployed, (
        f"Mon3tr must despawn when Kal'tsit retreats; alive={monstr.alive}, deployed={monstr.deployed}"
    )


# ---------------------------------------------------------------------------
# Test 11: No Mon3tr burst when Kal'tsit retreats (Mon3tr silently despawned)
# ---------------------------------------------------------------------------

def test_no_burst_when_monstr_despawned_by_retreat():
    """When Mon3tr is despawned via Kal'tsit retreat (not killed by enemies),
    no True damage burst should occur."""
    w = _world()
    k = make_kaltsit(slot=None)
    k.deployed = True; k.position = (0.0, 2.0)
    w.add_unit(k)

    monstr = next(u for u in w.units if u.name == "Mon3tr")
    monstr.position = (3.0, 2.0)

    e_adj = _slug(pos=(4, 2))
    w.add_unit(e_adj)

    hp_before = e_adj.hp

    # Retreat Kal'tsit → Mon3tr despawned directly (alive=False, not via take_damage)
    w.retreat(k)

    # Tick — no _just_died was set on Mon3tr, so no burst fires
    w.tick()

    assert e_adj.hp == hp_before, (
        "No True damage burst must fire when Mon3tr is silently despawned via retreat"
    )
