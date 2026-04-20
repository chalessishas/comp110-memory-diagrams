"""Vigil — Pack Leader's Resolve talent: self-REGEN 80 HP/s while S3 inactive."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, StatusKind, RoleArchetype
from core.systems import register_default_systems
from data.characters.vigil import (
    make_vigil,
    _TALENT_TAG, _REGEN_SOURCE_TAG, _REGEN_HPS,
)


def _world(w=6, h=3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


# ---------------------------------------------------------------------------
# Test 1: Config
# ---------------------------------------------------------------------------

def test_vigil_config():
    v = make_vigil()
    assert v.archetype == RoleArchetype.VAN_TACTICIAN
    assert v.block == 1
    assert len(v.talents) == 1
    assert v.talents[0].name == "Pack Leader's Resolve"
    assert v.talents[0].behavior_tag == _TALENT_TAG
    sk = v.skill
    assert sk is not None and sk.slot == "S3"


# ---------------------------------------------------------------------------
# Test 2: REGEN status applied when S3 not active
# ---------------------------------------------------------------------------

def test_talent_regen_while_idle():
    """After one tick with S3 inactive, Vigil must have REGEN status."""
    w = _world()
    v = make_vigil()
    v.deployed = True; v.position = (0.0, 1.0); v.atk_cd = 999.0
    w.add_unit(v)

    w.tick()

    assert v.has_status(StatusKind.REGEN), (
        "Vigil must have REGEN status while S3 is inactive"
    )


# ---------------------------------------------------------------------------
# Test 3: REGEN carries correct source_tag and HPS param
# ---------------------------------------------------------------------------

def test_talent_regen_params():
    """REGEN status must have correct source_tag and hps param."""
    w = _world()
    v = make_vigil()
    v.deployed = True; v.position = (0.0, 1.0); v.atk_cd = 999.0
    w.add_unit(v)

    w.tick()

    regen = next((s for s in v.statuses if s.kind == StatusKind.REGEN and s.source_tag == _REGEN_SOURCE_TAG), None)
    assert regen is not None, f"REGEN with source_tag {_REGEN_SOURCE_TAG} must be present"
    assert regen.params.get("hps") == _REGEN_HPS, (
        f"REGEN hps must be {_REGEN_HPS}; got {regen.params.get('hps')}"
    )


# ---------------------------------------------------------------------------
# Test 4: REGEN actually heals HP each tick
# ---------------------------------------------------------------------------

def test_talent_regen_heals_hp():
    """REGEN must increase Vigil's HP each tick when he is injured."""
    w = _world()
    v = make_vigil()
    v.deployed = True; v.position = (0.0, 1.0); v.atk_cd = 999.0
    w.add_unit(v)

    # Injure Vigil
    v.hp = v.max_hp - 500
    hp_before = v.hp

    w.tick()  # tick 1: talent applies REGEN (status_system already ran, but REGEN was not present)
    w.tick()  # tick 2: status_system applies REGEN heal with REGEN present from tick 1

    assert v.hp > hp_before, (
        f"Vigil HP must increase from REGEN; was {hp_before}, now {v.hp}"
    )


# ---------------------------------------------------------------------------
# Test 5: REGEN removed when S3 fires
# ---------------------------------------------------------------------------

def test_talent_regen_removed_on_s3():
    """When S3 fires, REGEN must be removed by end of that tick."""
    w = _world()
    v = make_vigil("S3")
    v.deployed = True; v.position = (0.0, 1.0); v.atk_cd = 999.0
    w.add_unit(v)

    w.tick()  # REGEN applied (S3 not yet active)
    assert v.has_status(StatusKind.REGEN), "REGEN must be present before S3"

    v.skill.sp = float(v.skill.sp_cost)
    w.tick()  # S3 fires → talent removes REGEN

    assert not v.has_status(StatusKind.REGEN), (
        "REGEN must be removed once S3 is active"
    )


# ---------------------------------------------------------------------------
# Test 6: REGEN reapplies after S3 ends
# ---------------------------------------------------------------------------

def test_talent_regen_reapplies_after_s3():
    """After S3 expires, REGEN must reapply."""
    from data.characters.vigil import _S3_TAG
    w = _world()
    v = make_vigil("S3")
    v.deployed = True; v.position = (0.0, 1.0); v.atk_cd = 999.0
    w.add_unit(v)

    v.skill.sp = float(v.skill.sp_cost)
    w.tick()  # S3 fires, REGEN removed
    assert not v.has_status(StatusKind.REGEN)

    # Advance past S3 duration (15s)
    for _ in range(int(TICK_RATE * 16)):
        w.tick()

    assert v.has_status(StatusKind.REGEN), (
        "Vigil must regain REGEN after S3 ends"
    )
