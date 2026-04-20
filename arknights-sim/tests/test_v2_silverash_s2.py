"""SilverAsh S2 Frost Suppression — ATK+100% + ASPD+30 for 20s."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.silverash import (
    make_silverash,
    _S2_TAG, _S2_ATK_RATIO, _S2_ASPD_BONUS, _S2_BUFF_TAG,
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


def _slug(pos=(0, 1), hp=999999):
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 20)
    e.deployed = True; e.position = (float(px), float(py))
    e.max_hp = hp; e.hp = hp; e.atk = 0; e.move_speed = 0.0
    return e


# ---------------------------------------------------------------------------
# Test 1: Config
# ---------------------------------------------------------------------------

def test_silverash_s2_config():
    sa = make_silverash(slot="S2")
    sk = sa.skill
    assert sk is not None
    assert sk.slot == "S2"
    assert sk.name == "Frost Suppression"
    assert sk.sp_cost == 30
    assert sk.behavior_tag == _S2_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK buff applied
# ---------------------------------------------------------------------------

def test_s2_atk_buff():
    """S2 must apply ATK+100% buff while active."""
    w = _world()
    sa = make_silverash(slot="S2")
    base_atk = sa.effective_atk
    sa.deployed = True; sa.position = (0.0, 1.0); sa.atk_cd = 999.0
    w.add_unit(sa)

    slug = _slug(pos=(0, 1))  # same tile, in range (0,0)
    w.add_unit(slug)

    sa.skill.sp = float(sa.skill.sp_cost)
    w.tick()

    expected_atk = int(base_atk * (1 + _S2_ATK_RATIO))
    assert sa.effective_atk == expected_atk, (
        f"S2 ATK: expected {expected_atk}, got {sa.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: ASPD buff applied
# ---------------------------------------------------------------------------

def test_s2_aspd_buff():
    """S2 must apply ASPD+30 buff while active."""
    w = _world()
    sa = make_silverash(slot="S2")
    base_aspd = sa.effective_aspd
    sa.deployed = True; sa.position = (0.0, 1.0); sa.atk_cd = 999.0
    w.add_unit(sa)

    slug = _slug(pos=(0, 1))
    w.add_unit(slug)

    sa.skill.sp = float(sa.skill.sp_cost)
    w.tick()

    expected_aspd = base_aspd + _S2_ASPD_BONUS
    assert sa.effective_aspd == expected_aspd, (
        f"S2 ASPD: expected {expected_aspd}, got {sa.aspd}"
    )


# ---------------------------------------------------------------------------
# Test 4: Both buffs removed on S2 end
# ---------------------------------------------------------------------------

def test_s2_buffs_removed_on_end():
    """Both ATK and ASPD buffs must be stripped when S2 expires."""
    sa = make_silverash(slot="S2")
    base_atk = sa.effective_atk
    base_aspd = sa.effective_aspd
    sa.skill.sp = float(sa.skill.sp_cost)

    w = _world()
    sa.deployed = True; sa.position = (0.0, 1.0); sa.atk_cd = 999.0
    w.add_unit(sa)

    slug = _slug(pos=(0, 1))
    w.add_unit(slug)

    for _ in range(int(TICK_RATE * 22)):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in sa.buffs), "Buffs must be removed"
    assert sa.effective_atk == base_atk
    assert sa.effective_aspd == base_aspd


# ---------------------------------------------------------------------------
# Test 5: S3 regression
# ---------------------------------------------------------------------------

def test_s3_regression():
    """S3 Truesilver Slash must still work after S2 was added."""
    sa = make_silverash(slot="S3")
    assert sa.skill is not None
    assert sa.skill.slot == "S3"
    assert sa.skill.name == "Truesilver Slash"
