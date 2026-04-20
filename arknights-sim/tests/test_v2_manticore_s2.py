"""Manticore S2 Predator's Claws — ATK+100% + BIND on enemies in range."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, StatusKind
from core.systems import register_default_systems
from data.characters.manticore import (
    make_manticore,
    _S2_TAG, _S2_ATK_RATIO, _S2_BIND_DURATION, _S2_BIND_TAG, _S2_BUFF_TAG,
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


def _slug(pos=(1, 1), hp=999999):
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 20)
    e.deployed = True
    e.position = (float(px), float(py))
    e.max_hp = hp; e.hp = hp; e.atk = 0; e.move_speed = 0.0
    return e


# ---------------------------------------------------------------------------
# Test 1: Config
# ---------------------------------------------------------------------------

def test_manticore_s2_config():
    m = make_manticore(slot="S2")
    sk = m.skill
    assert sk is not None
    assert sk.slot == "S2"
    assert sk.name == "Predator's Claws"
    assert sk.sp_cost == 20
    assert sk.behavior_tag == _S2_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK buff applied on S2 activation
# ---------------------------------------------------------------------------

def test_s2_atk_buff():
    """S2 must apply ATK +100% while active."""
    w = _world()
    m = make_manticore(slot="S2")
    base_atk = m.effective_atk
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)

    slug = _slug(pos=(0, 1))  # same tile, in range (0,0) offset
    w.add_unit(slug)

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()  # skill fires

    assert m.skill.active_remaining > 0, "S2 should be active"
    expected_atk = int(base_atk * (1 + _S2_ATK_RATIO))
    assert m.effective_atk == expected_atk, (
        f"S2 ATK buff: expected {expected_atk}, got {m.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: BIND applied to enemy in melee range
# ---------------------------------------------------------------------------

def test_s2_binds_enemies_in_range():
    """S2 on_start must BIND enemies within Manticore's range tiles."""
    w = _world()
    m = make_manticore(slot="S2")
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)

    slug = _slug(pos=(1, 1))  # offset (1,0) — in EXECUTOR_RANGE
    w.add_unit(slug)

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()

    assert slug.has_status(StatusKind.BIND), "S2 must BIND enemy in melee range"


# ---------------------------------------------------------------------------
# Test 4: BIND source_tag and duration correct
# ---------------------------------------------------------------------------

def test_s2_bind_params():
    """BIND status must carry correct source_tag."""
    w = _world()
    m = make_manticore(slot="S2")
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()

    bind = next((s for s in slug.statuses if s.kind == StatusKind.BIND and s.source_tag == _S2_BIND_TAG), None)
    assert bind is not None, f"BIND with source_tag {_S2_BIND_TAG} must be present"


# ---------------------------------------------------------------------------
# Test 5: Enemy out of range NOT bound
# ---------------------------------------------------------------------------

def test_s2_no_bind_out_of_range():
    """Enemy outside EXECUTOR_RANGE must NOT be bound."""
    w = _world()
    m = make_manticore(slot="S2")
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)

    slug_in = _slug(pos=(1, 1))   # in range (1,0)
    slug_out = _slug(pos=(3, 1))  # out of range (3,0)
    w.add_unit(slug_in)
    w.add_unit(slug_out)

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()

    assert slug_in.has_status(StatusKind.BIND), "In-range enemy must be BOUND"
    assert not slug_out.has_status(StatusKind.BIND), "Out-of-range enemy must NOT be BOUND"


# ---------------------------------------------------------------------------
# Test 6: ATK buff removed on S2 end
# ---------------------------------------------------------------------------

def test_s2_atk_buff_removed_on_end():
    """ATK buff must be cleaned up when S2 expires."""
    m = make_manticore(slot="S2")
    base_atk = m.effective_atk
    m.skill.sp = float(m.skill.sp_cost)

    w = _world()
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)

    slug = _slug(pos=(0, 1))  # in same-tile range to trigger S2
    w.add_unit(slug)

    from core.types import TICK_RATE
    for _ in range(int(TICK_RATE * 17)):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in m.buffs), (
        "ATK buff must be removed after S2 ends"
    )
    assert m.effective_atk == base_atk, (
        f"ATK must return to base {base_atk} after S2; got {m.effective_atk}"
    )
