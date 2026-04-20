"""Shaw — SPEC_PUSHER push mechanic + S2 Powerful Current AoE burst."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.shaw import make_shaw, _S2_ATK_MULT, _S2_PUSH_DIST
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


def _slug(path=None, hp=99999, atk=0, progress=5.0):
    """Enemy with a long straight path; path_progress set to `progress`."""
    if path is None:
        path = [(x, 1) for x in range(10)]
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = atk; e.move_speed = 0.0
    e.deployed = True
    e.path_progress = progress
    tx, ty = path[int(progress)]
    e.position = (float(tx), float(ty))
    return e


# ---------------------------------------------------------------------------
# Test 1: SPEC_PUSHER archetype and push_distance
# ---------------------------------------------------------------------------

def test_shaw_archetype_and_push():
    from core.types import RoleArchetype
    from core.systems.talent_registry import fire_on_battle_start
    s = make_shaw()
    assert s.archetype == RoleArchetype.SPEC_PUSHER
    # Gale talent fires on_battle_start; construction default is 1
    w = _world()
    w.add_unit(s)
    fire_on_battle_start(w, s)
    assert s.push_distance == 2


# ---------------------------------------------------------------------------
# Test 2: Normal attack pushes enemy back (path_progress decreases)
# ---------------------------------------------------------------------------

def test_attack_pushes_enemy_back():
    """Shaw's basic attack decreases target's path_progress by push_distance."""
    w = _world()
    shaw = make_shaw()
    shaw.deployed = True; shaw.position = (1.0, 1.0); shaw.atk_cd = 0.0
    w.add_unit(shaw)

    slug = _slug(progress=3.0)   # at tile index 3 (position x=3)
    slug.position = (3.0, 1.0)
    w.add_unit(slug)

    progress_before = slug.path_progress
    w.tick()

    assert slug.path_progress < progress_before, (
        f"path_progress must decrease after push; was {progress_before}, now {slug.path_progress}"
    )
    assert slug.path_progress == max(0.0, progress_before - shaw.push_distance), (
        f"Expected path_progress={max(0.0, progress_before - shaw.push_distance)}, "
        f"got {slug.path_progress}"
    )


# ---------------------------------------------------------------------------
# Test 3: Push clamps at 0 (enemy cannot be pushed past spawn point)
# ---------------------------------------------------------------------------

def test_push_clamps_at_zero():
    """Enemy at path_progress=0 cannot be pushed further back."""
    w = _world()
    shaw = make_shaw()
    shaw.deployed = True; shaw.position = (0.0, 1.0); shaw.atk_cd = 0.0
    shaw.push_distance = 5   # large push
    w.add_unit(shaw)

    slug = _slug(progress=1.0)   # close to start
    slug.position = (1.0, 1.0)
    w.add_unit(slug)

    w.tick()

    assert slug.path_progress >= 0.0, "path_progress must never go below 0"
    assert slug.path_progress == 0.0, f"Expected 0.0 after clamp, got {slug.path_progress}"


# ---------------------------------------------------------------------------
# Test 4: Push updates enemy position to new tile
# ---------------------------------------------------------------------------

def test_push_updates_position():
    """After push, enemy.position must reflect new tile on path."""
    w = _world()
    shaw = make_shaw()
    shaw.deployed = True; shaw.position = (3.0, 1.0); shaw.atk_cd = 0.0
    shaw.push_distance = 2
    w.add_unit(shaw)

    path = [(x, 1) for x in range(10)]
    slug = _slug(path=path, progress=5.0)   # starts at (5,1)
    w.add_unit(slug)

    w.tick()

    # After push of 2, path_progress=3.0 → position should be tile[3] = (3,1)
    assert slug.path_progress == 3.0
    assert slug.position == (3.0, 1.0), f"Position must snap to new tile; got {slug.position}"


# ---------------------------------------------------------------------------
# Test 5: S2 deals Arts damage to all enemies in range
# ---------------------------------------------------------------------------

def test_s2_deals_arts_damage_to_all_in_range():
    """S2 Powerful Current: Arts burst hits all enemies in line (tiles 0-3 forward)."""
    w = _world()
    shaw = make_shaw(slot="S2")
    shaw.deployed = True; shaw.position = (0.0, 1.0); shaw.atk_cd = 999.0
    w.add_unit(shaw)

    s1 = _slug(progress=1.0); s1.position = (1.0, 1.0); w.add_unit(s1)
    s2 = _slug(progress=2.0); s2.position = (2.0, 1.0); w.add_unit(s2)
    s3 = _slug(progress=3.0); s3.position = (3.0, 1.0); w.add_unit(s3)
    s_out = _slug(progress=6.0); s_out.position = (6.0, 1.0); w.add_unit(s_out)  # out of range

    hp1, hp2, hp3, hp_out = s1.hp, s2.hp, s3.hp, s_out.hp

    shaw.skill.sp = shaw.skill.sp_cost
    w.tick()

    assert s1.hp < hp1, "S2 must hit enemy at range 1"
    assert s2.hp < hp2, "S2 must hit enemy at range 2"
    assert s3.hp < hp3, "S2 must hit enemy at range 3"
    assert s_out.hp == hp_out, "S2 must NOT hit enemy out of range"


# ---------------------------------------------------------------------------
# Test 6: S2 pushes hit enemies back 3 tiles
# ---------------------------------------------------------------------------

def test_s2_pushes_enemies_back():
    """S2 Powerful Current: each hit enemy is pushed 3 tiles backward."""
    w = _world()
    shaw = make_shaw(slot="S2")
    shaw.deployed = True; shaw.position = (0.0, 1.0); shaw.atk_cd = 999.0
    w.add_unit(shaw)

    # Slug at tile 1 (progress=1.0, position=(1,1)) — consistent path_progress+position
    slug = _slug(progress=1.0)   # _slug sets position = path[1] = (1,1)
    w.add_unit(slug)

    progress_before = slug.path_progress
    shaw.skill.sp = shaw.skill.sp_cost
    w.tick()

    expected = max(0.0, progress_before - _S2_PUSH_DIST)
    assert slug.path_progress == expected, (
        f"S2 must push {_S2_PUSH_DIST} tiles; expected progress={expected}, got {slug.path_progress}"
    )
