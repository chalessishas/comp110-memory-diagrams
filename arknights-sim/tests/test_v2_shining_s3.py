"""Shining S3 Creed Field — ATK+50% to self + DEF+30 aura to in-range allies."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis
from core.systems import register_default_systems
from data.characters.shining import (
    make_shining,
    _S3_ATK_RATIO, _S3_ATK_BUFF_TAG,
    _S3_DEF_FLAT, _S3_DEF_BUFF_TAG, _S3_DURATION,
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


def _ally(world: World, x: float, y: float):
    from core.state.unit_state import UnitState
    from core.types import Faction
    a = UnitState(name="Ally", faction=Faction.ALLY, max_hp=1000, atk=0, defence=100, res=0.0)
    a.alive = True; a.deployed = True; a.position = (x, y)
    world.add_unit(a)
    return a


# Shining at (0,1), range (1,0) is tile (1,1) in world coords
_SH_POS = (0.0, 1.0)
_ALLY_IN_RANGE = (1.0, 1.0)    # dx=+1, dy=0 → in range
_ALLY_OUT_RANGE = (4.0, 1.0)   # dx=+4, dy=0 → out of range (max dx=3)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def test_shining_s3_config():
    s = make_shining(slot="S3")
    sk = s.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.name == "Creed Field"
    assert sk.sp_cost == 50


# ---------------------------------------------------------------------------
# ATK buff applied to Shining on activation
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    """S3 applies ATK+50% to Shining on activation."""
    w = _world()
    s = make_shining(slot="S3")
    s.deployed = True; s.position = _SH_POS; s.atk_cd = 999.0
    s.deploy_time = w.global_state.elapsed
    w.add_unit(s)

    s.skill.sp = float(s.skill.sp_cost)
    w.tick()

    buff = next((b for b in s.buffs if b.source_tag == _S3_ATK_BUFF_TAG), None)
    assert buff is not None, "S3 ATK buff must be applied to Shining"
    assert buff.axis == BuffAxis.ATK
    assert buff.value == _S3_ATK_RATIO


# ---------------------------------------------------------------------------
# DEF aura applied to in-range allies
# ---------------------------------------------------------------------------

def test_s3_def_aura_in_range():
    """Allies within Shining's heal range receive +30 DEF aura during S3."""
    w = _world()
    s = make_shining(slot="S3")
    s.deployed = True; s.position = _SH_POS; s.atk_cd = 999.0
    s.deploy_time = w.global_state.elapsed
    ally = _ally(w, *_ALLY_IN_RANGE)
    w.add_unit(s)

    s.skill.sp = float(s.skill.sp_cost)
    w.tick()

    aura = next((b for b in ally.buffs if b.source_tag == _S3_DEF_BUFF_TAG), None)
    assert aura is not None, "In-range ally must receive DEF aura"
    assert aura.axis == BuffAxis.DEF
    assert aura.value == _S3_DEF_FLAT


def test_s3_def_aura_out_of_range():
    """Allies outside heal range do NOT receive the DEF aura."""
    w = _world()
    s = make_shining(slot="S3")
    s.deployed = True; s.position = _SH_POS; s.atk_cd = 999.0
    s.deploy_time = w.global_state.elapsed
    ally_out = _ally(w, *_ALLY_OUT_RANGE)
    w.add_unit(s)

    s.skill.sp = float(s.skill.sp_cost)
    w.tick()

    aura = next((b for b in ally_out.buffs if b.source_tag == _S3_DEF_BUFF_TAG), None)
    assert aura is None, "Out-of-range ally must NOT receive DEF aura"


def test_s3_def_aura_refreshed_each_tick():
    """DEF aura TTL is refreshed each tick so it persists throughout S3."""
    w = _world()
    s = make_shining(slot="S3")
    s.deployed = True; s.position = _SH_POS; s.atk_cd = 999.0
    s.deploy_time = w.global_state.elapsed
    ally = _ally(w, *_ALLY_IN_RANGE)
    w.add_unit(s)

    s.skill.sp = float(s.skill.sp_cost)
    for _ in range(int(TICK_RATE * 5)):  # 5 seconds into S3
        w.tick()

    aura = next((b for b in ally.buffs if b.source_tag == _S3_DEF_BUFF_TAG), None)
    assert aura is not None, "DEF aura must still be active 5 seconds into S3"


# ---------------------------------------------------------------------------
# S3 expiry — all buffs cleared
# ---------------------------------------------------------------------------

def test_s3_reverts_on_end():
    """ATK buff and ally DEF aura are removed when S3 expires."""
    w = _world()
    s = make_shining(slot="S3")
    s.deployed = True; s.position = _SH_POS; s.atk_cd = 999.0
    s.deploy_time = w.global_state.elapsed
    ally = _ally(w, *_ALLY_IN_RANGE)
    w.add_unit(s)

    s.skill.sp = float(s.skill.sp_cost)
    w.tick()

    for _ in range(int(TICK_RATE * (_S3_DURATION + 2))):
        w.tick()

    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in s.buffs), "Shining ATK buff must clear on S3 end"
    # Allow for TTL expiry or explicit sweep — either is correct
    aura = next((b for b in ally.buffs if b.source_tag == _S3_DEF_BUFF_TAG), None)
    assert aura is None, "Ally DEF aura must be gone after S3 expires"


# ---------------------------------------------------------------------------
# Regression: S2 still works
# ---------------------------------------------------------------------------

def test_s2_regression():
    s = make_shining(slot="S2")
    assert s.skill is not None and s.skill.slot == "S2"
    assert s.skill.name == "Faith"
