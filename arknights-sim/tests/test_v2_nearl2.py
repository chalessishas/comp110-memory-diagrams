"""Nearl2 (耀骑士临光 Penance) — blocking-count ATK talent + S3 Purgatorio block=3."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, RoleArchetype
from core.systems import register_default_systems
from data.characters.nearl2 import (
    make_penance as make_nearl2,
    _TALENT_ATK_PER_STACK, _TALENT_MAX_STACKS,
    _S3_ATK_RATIO, _S3_BLOCK, _S3_DURATION,
)
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


def _blocked_slug(world: World, penance: UnitState, pos=(0, 1)) -> UnitState:
    """Spawn a slug at penance's tile so targeting_system blocks it."""
    e = _slug(pos=pos)
    world.add_unit(e)
    return e


# ---------------------------------------------------------------------------
# Test 1: Config
# ---------------------------------------------------------------------------

def test_nearl2_config():
    p = make_nearl2()
    assert p.archetype == RoleArchetype.GUARD_CENTURION
    assert p.block == 1
    assert len(p.talents) == 1
    assert p.talents[0].name == "Penitence, Absolution"
    sk = p.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.sp_cost == 60


# ---------------------------------------------------------------------------
# Test 2: No ATK buff when blocking 0 enemies
# ---------------------------------------------------------------------------

def test_talent_no_buff_when_idle():
    """Talent must not apply when Penance is blocking 0 enemies."""
    w = _world()
    p = make_nearl2()
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    w.add_unit(p)

    base_atk = p.atk
    w.tick()

    assert p.effective_atk == base_atk, (
        f"ATK must stay at {base_atk} with 0 blocked; got {p.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: +30% ATK with 1 blocked enemy
# ---------------------------------------------------------------------------

def test_talent_one_stack():
    """Talent grants +30% ATK when blocking 1 enemy."""
    w = _world()
    p = make_nearl2()
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    w.add_unit(p)

    # Enemy on same tile → targeting system blocks it
    slug = _slug(pos=(0, 1))
    w.add_unit(slug)

    base_atk = p.atk
    w.tick()  # targeting assigns block, talent fires

    expected = int(base_atk * (1.0 + _TALENT_ATK_PER_STACK))
    assert p.effective_atk == expected, (
        f"1 blocked → ATK should be {expected}; got {p.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 4: +90% ATK with 3 blocked enemies (max stacks)
# ---------------------------------------------------------------------------

def test_talent_max_stacks():
    """Blocking 3 enemies gives the maximum +90% ATK (stacked with S3 ATK+20%)."""
    w = _world()
    p = make_nearl2("S3")
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    # Fire S3 to get block=3
    p.skill.sp = float(p.skill.sp_cost)
    w.add_unit(p)

    # 3 enemies at same tile
    for _ in range(3):
        w.add_unit(_slug(pos=(0, 1)))

    base_atk = p.atk
    w.tick()  # tick 1: targeting runs (block=1 still), S3 fires → block=3
    w.tick()  # tick 2: targeting runs with block=3 → 3 enemies blocked → talent fires 3 stacks

    # effective_atk = int(base_atk * (1 + S3_ratio + 3 × talent_ratio))
    total_ratio = _S3_ATK_RATIO + _TALENT_MAX_STACKS * _TALENT_ATK_PER_STACK
    expected = int(base_atk * (1.0 + total_ratio))
    assert p.effective_atk == expected, (
        f"3 blocked (S3 active) → ATK must be {expected}; got {p.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 5: Talent buff updates when blocking count changes
# ---------------------------------------------------------------------------

def test_talent_buff_updates_on_unblock():
    """When a blocked enemy dies, talent buff should decrease on next tick."""
    w = _world()
    p = make_nearl2()
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    w.add_unit(p)

    slug = _slug(pos=(0, 1))
    w.add_unit(slug)

    w.tick()  # blocking → buff = +30% ATK
    base_atk = p.atk
    expected_buffed = int(base_atk * (1.0 + _TALENT_ATK_PER_STACK))
    assert p.effective_atk == expected_buffed, "ATK buffed while blocking"

    slug.alive = False  # kill slug

    w.tick()  # now 0 blocked → talent removes buff

    assert p.effective_atk == base_atk, (
        f"ATK must revert to {base_atk} when unblocked; got {p.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 6: S3 sets block=3 and ATK+20%
# ---------------------------------------------------------------------------

def test_s3_activates():
    """Purgatorio must set block=3 and grant ATK +20%."""
    w = _world()
    p = make_nearl2("S3")
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    w.add_unit(p)

    base_atk = p.atk  # use base atk (no blocking buff yet)
    p.skill.sp = float(p.skill.sp_cost)
    w.tick()

    assert p.block == _S3_BLOCK, f"S3 must set block={_S3_BLOCK}; got {p.block}"
    expected_atk = int(base_atk * (1.0 + _S3_ATK_RATIO))
    assert p.effective_atk == expected_atk, (
        f"S3 ATK must be {expected_atk}; got {p.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 7: S3 reverts on end
# ---------------------------------------------------------------------------

def test_s3_reverts_on_end():
    """After S3 expires, block reverts to 1 and ATK buff is removed."""
    w = _world()
    p = make_nearl2("S3")
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    w.add_unit(p)

    base_atk = p.atk
    p.skill.sp = float(p.skill.sp_cost)
    w.tick()
    assert p.block == _S3_BLOCK

    for _ in range(int(TICK_RATE * (_S3_DURATION + 1))):
        w.tick()

    assert p.block == 1, f"Block must revert to 1 after S3; got {p.block}"
    assert p.effective_atk == base_atk, (
        f"ATK must revert to {base_atk}; got {p.effective_atk}"
    )
