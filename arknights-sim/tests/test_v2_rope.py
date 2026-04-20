"""Rope — SPEC_HOOKMASTER pull mechanic (push_distance=1) + S2 Binding Arts."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, StatusKind, TICK_RATE
from core.systems import register_default_systems
from data.characters.rope import make_rope, _BASE_PULL, _S2_PULL_DIST, _S2_BIND_DURATION, _S2_ATK_MULT
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=10, height=3)
    for x in range(10):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _slug(progress=5.0, hp=99999, atk=0):
    path = [(x, 1) for x in range(10)]
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = atk; e.move_speed = 0.0
    e.deployed = True
    e.path_progress = progress
    tx, ty = path[int(progress)]
    e.position = (float(tx), float(ty))
    return e


# ---------------------------------------------------------------------------
# Test 1: Archetype and push_distance
# ---------------------------------------------------------------------------

def test_rope_archetype_and_pull():
    from core.types import RoleArchetype
    r = make_rope()
    assert r.archetype == RoleArchetype.SPEC_HOOKMASTER
    assert r.push_distance == _BASE_PULL  # 1 tile pull per attack


# ---------------------------------------------------------------------------
# Test 2: Normal attack pulls enemy 1 tile backward
# ---------------------------------------------------------------------------

def test_basic_attack_pulls_one_tile():
    """Rope's basic attack decreases target path_progress by 1."""
    w = _world()
    r = make_rope()
    r.deployed = True; r.position = (0.0, 1.0); r.atk_cd = 0.0
    w.add_unit(r)

    slug = _slug(progress=3.0)
    w.add_unit(slug)

    progress_before = slug.path_progress
    w.tick()

    assert slug.path_progress == progress_before - _BASE_PULL, (
        f"Expected path_progress={progress_before - _BASE_PULL}, got {slug.path_progress}"
    )


# ---------------------------------------------------------------------------
# Test 3: Pull clamps at 0
# ---------------------------------------------------------------------------

def test_pull_clamps_at_zero():
    """Enemy at path_progress=0 cannot be pulled further."""
    w = _world()
    r = make_rope()
    r.deployed = True; r.position = (0.0, 1.0); r.atk_cd = 0.0
    r.push_distance = 5
    w.add_unit(r)

    slug = _slug(progress=1.0)
    w.add_unit(slug)

    w.tick()

    assert slug.path_progress >= 0.0
    assert slug.path_progress == 0.0


# ---------------------------------------------------------------------------
# Test 4: S2 applies BIND status to target
# ---------------------------------------------------------------------------

def test_s2_applies_bind():
    """S2 Binding Arts: target receives BIND status."""
    w = _world()
    r = make_rope(slot="S2")
    r.deployed = True; r.position = (0.0, 1.0); r.atk_cd = 999.0
    w.add_unit(r)

    slug = _slug(progress=3.0)
    w.add_unit(slug)

    r.skill.sp = r.skill.sp_cost
    w.tick()

    assert slug.has_status(StatusKind.BIND), "S2 must apply BIND to target"


# ---------------------------------------------------------------------------
# Test 5: S2 pulls target 3 tiles backward
# ---------------------------------------------------------------------------

def test_s2_pulls_three_tiles():
    """S2 Binding Arts: target pulled 3 tiles backward."""
    w = _world()
    r = make_rope(slot="S2")
    r.deployed = True; r.position = (0.0, 1.0); r.atk_cd = 999.0
    w.add_unit(r)

    slug = _slug(progress=3.0)   # tile (3,1) — max range of Hookmaster (dx=3)
    w.add_unit(slug)

    progress_before = slug.path_progress
    r.skill.sp = r.skill.sp_cost
    w.tick()

    expected = max(0.0, progress_before - _S2_PULL_DIST)
    assert slug.path_progress == expected, (
        f"S2 must pull {_S2_PULL_DIST} tiles; expected {expected}, got {slug.path_progress}"
    )


# ---------------------------------------------------------------------------
# Test 6: BIND expires after _S2_BIND_DURATION
# ---------------------------------------------------------------------------

def test_s2_bind_expires():
    """BIND applied by S2 expires after _S2_BIND_DURATION."""
    w = _world()
    r = make_rope(slot="S2")
    r.deployed = True; r.position = (0.0, 1.0); r.atk_cd = 999.0
    w.add_unit(r)

    slug = _slug(progress=3.0, hp=9999999)   # within Hookmaster range (dx=3)
    w.add_unit(slug)

    r.skill.sp = r.skill.sp_cost
    w.tick()
    assert slug.has_status(StatusKind.BIND), "BIND must be active after S2"

    for _ in range(int(TICK_RATE * (_S2_BIND_DURATION + 0.5))):
        w.tick()

    assert not slug.has_status(StatusKind.BIND), "BIND must expire after duration"
    assert slug.can_act(), "Enemy must be able to act after BIND expires"
