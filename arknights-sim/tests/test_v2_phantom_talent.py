"""Phantom — Infiltration talent: CAMOUFLAGE while S3 inactive, removed when S3 fires."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, StatusKind, RoleArchetype
from core.systems import register_default_systems
from data.characters.phantom import (
    make_phantom,
    _INFILTRATION_TAG, _INFILTRATION_CAMO_TAG, _INFILTRATION_CAMO_TTL,
)
from data.characters.mountain import make_mountain
from data.enemies import make_originium_slug


def _world(w=6, h=3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def _slug(pos=(0, 1), hp=9999) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 20)
    e.deployed = True
    e.position = (float(px), float(py))
    e.max_hp = hp; e.hp = hp
    e.atk = 0; e.move_speed = 0.0
    return e


# ---------------------------------------------------------------------------
# Test 1: Config
# ---------------------------------------------------------------------------

def test_phantom_config():
    p = make_phantom()
    assert p.archetype == RoleArchetype.SPEC_EXECUTOR
    assert p.block == 1
    assert len(p.talents) == 1
    assert p.talents[0].name == "Infiltration"
    assert p.talents[0].behavior_tag == _INFILTRATION_TAG
    sk = p.skill
    assert sk is not None and sk.slot == "S3"


# ---------------------------------------------------------------------------
# Test 2: CAMOUFLAGE active when S3 not running
# ---------------------------------------------------------------------------

def test_infiltration_camo_while_idle():
    """After one tick with S3 not active, Phantom must have CAMOUFLAGE."""
    w = _world()
    p = make_phantom()
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    w.add_unit(p)

    w.tick()

    assert p.has_status(StatusKind.CAMOUFLAGE), (
        "Phantom must have CAMOUFLAGE while S3 is inactive"
    )


# ---------------------------------------------------------------------------
# Test 3: CAMOUFLAGE uses correct source_tag
# ---------------------------------------------------------------------------

def test_infiltration_camo_source_tag():
    """CAMOUFLAGE status must carry the infiltration source_tag."""
    w = _world()
    p = make_phantom()
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    w.add_unit(p)

    w.tick()

    camo = next((s for s in p.statuses if s.kind == StatusKind.CAMOUFLAGE), None)
    assert camo is not None
    assert camo.source_tag == _INFILTRATION_CAMO_TAG, (
        f"source_tag must be {_INFILTRATION_CAMO_TAG}; got {camo.source_tag}"
    )


# ---------------------------------------------------------------------------
# Test 4: CAMOUFLAGE removed when S3 fires
# ---------------------------------------------------------------------------

def test_infiltration_camo_removed_on_s3():
    """When S3 fires, CAMOUFLAGE must be absent by end of that tick."""
    w = _world()
    p = make_phantom("S3")
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    w.add_unit(p)

    w.tick()  # tick 1: CAMOUFLAGE applied (S3 not yet active)
    assert p.has_status(StatusKind.CAMOUFLAGE), "CAMOUFLAGE must be present before S3"

    p.skill.sp = float(p.skill.sp_cost)
    w.tick()  # tick 2: S3 fires (skill_system) → infiltration removes CAMOUFLAGE

    assert not p.has_status(StatusKind.CAMOUFLAGE), (
        "CAMOUFLAGE must be removed once S3 is active"
    )


# ---------------------------------------------------------------------------
# Test 5: CAMOUFLAGE absent for full S3 duration
# ---------------------------------------------------------------------------

def test_infiltration_camo_absent_during_s3():
    """CAMOUFLAGE must stay absent for the entire S3 active window."""
    w = _world()
    p = make_phantom("S3")
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    w.add_unit(p)

    p.skill.sp = float(p.skill.sp_cost)
    w.tick()  # S3 fires

    # Advance halfway through S3 and verify CAMOUFLAGE is absent each tick
    for _ in range(int(TICK_RATE * 10)):
        w.tick()
        assert not p.has_status(StatusKind.CAMOUFLAGE), (
            "CAMOUFLAGE must not be present while S3 is active"
        )


# ---------------------------------------------------------------------------
# Test 6: CAMOUFLAGE reapplies after S3 ends
# ---------------------------------------------------------------------------

def test_infiltration_camo_reapplies_after_s3():
    """After S3 expires, Phantom must regain CAMOUFLAGE."""
    from data.characters.phantom import _CLONE_DURATION
    w = _world()
    p = make_phantom("S3")
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    w.add_unit(p)

    p.skill.sp = float(p.skill.sp_cost)
    w.tick()  # S3 fires
    assert not p.has_status(StatusKind.CAMOUFLAGE)

    # Advance past S3 duration
    for _ in range(int(TICK_RATE * (_CLONE_DURATION + 1))):
        w.tick()

    assert p.has_status(StatusKind.CAMOUFLAGE), (
        "Phantom must regain CAMOUFLAGE after S3 ends"
    )


# ---------------------------------------------------------------------------
# Test 7: Enemy deprioritizes Phantom for block when CAMOUFLAGE active
# ---------------------------------------------------------------------------

def test_infiltration_camo_block_depriority():
    """With CAMOUFLAGE, Mountain (visible) must get block priority over Phantom."""
    w = _world()

    # Phantom on tile (1, 1) — will have CAMOUFLAGE after 1st tick
    p = make_phantom()
    p.deployed = True; p.position = (1.0, 1.0); p.atk_cd = 999.0
    w.add_unit(p)

    # Mountain on same tile — no CAMOUFLAGE
    mountain = make_mountain()
    mountain.deployed = True; mountain.position = (1.0, 1.0); mountain.atk_cd = 999.0
    w.add_unit(mountain)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    w.tick()  # tick 1: CAMOUFLAGE applied to Phantom
    w.tick()  # tick 2: targeting uses CAMOUFLAGE sort → Mountain wins block priority

    assert mountain.unit_id in slug.blocked_by_unit_ids, (
        "Mountain (visible) must block the enemy; Phantom (CAMOUFLAGE) must be deprioritized"
    )
    assert p.unit_id not in slug.blocked_by_unit_ids, (
        "Phantom (CAMOUFLAGE) must NOT win block priority when Mountain is available"
    )
