"""Mudrock S2 Rockfall — ATK+80% + DEF+30% for 20s."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.mudrock import (
    make_mudrock, _S2_TAG, _S2_ATK_RATIO, _S2_DEF_RATIO, _S2_BUFF_TAG, _S2_DURATION,
)


def _world(w=4, h=3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def test_mudrock_s2_config():
    m = make_mudrock(slot="S2")
    sk = m.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Rockfall"
    assert sk.sp_cost == 30
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff():
    """S2 applies ATK+80% buff."""
    w = _world()
    m = make_mudrock(slot="S2")
    base_atk = m.effective_atk
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()

    expected_atk = int(base_atk * (1 + _S2_ATK_RATIO))
    assert m.effective_atk == expected_atk, f"ATK: expected {expected_atk}, got {m.effective_atk}"


def test_s2_def_buff():
    """S2 applies a DEF+30% RATIO buff — verify buff is present."""
    from core.types import BuffAxis, BuffStack
    w = _world()
    m = make_mudrock(slot="S2")
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()

    def_buff = next((b for b in m.buffs if b.source_tag == _S2_BUFF_TAG and b.axis == BuffAxis.DEF), None)
    assert def_buff is not None, "S2 DEF buff must be applied"
    assert def_buff.stack == BuffStack.RATIO
    assert def_buff.value == _S2_DEF_RATIO


def test_s2_buffs_removed_on_end():
    """Both buffs must be removed when S2 expires."""
    m = make_mudrock(slot="S2")
    base_atk = m.effective_atk
    m.skill.sp = float(m.skill.sp_cost)

    w = _world()
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)

    for _ in range(int(TICK_RATE * (_S2_DURATION + 2))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in m.buffs)
    assert m.effective_atk == base_atk


def test_s3_regression():
    m = make_mudrock(slot="S3")
    assert m.skill is not None and m.skill.slot == "S3"
