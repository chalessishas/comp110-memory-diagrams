"""Ceylon S2 Soothing Waves — ATK+30%, heal_targets 3→4 for 20s."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.ceylon import (
    make_ceylon, _S2_TAG, _S2_ATK_RATIO, _S2_BUFF_TAG, _S2_DURATION,
    _S2_HEAL_TARGETS, _BASE_HEAL_TARGETS,
)


def _world(w=5, h=3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def test_ceylon_s2_config():
    c = make_ceylon(slot="S2")
    sk = c.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Soothing Waves"
    assert sk.sp_cost == 20
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff():
    """S2 applies ATK+30% buff."""
    from core.types import BuffAxis
    w = _world()
    c = make_ceylon(slot="S2")
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)

    c.skill.sp = float(c.skill.sp_cost)
    w.tick()

    buff = next((b for b in c.buffs if b.source_tag == _S2_BUFF_TAG), None)
    assert buff is not None, "S2 ATK buff must be applied"
    assert buff.axis == BuffAxis.ATK
    assert buff.value == _S2_ATK_RATIO


def test_s2_heal_targets_increased():
    """S2 raises heal_targets from 3 to 4."""
    w = _world()
    c = make_ceylon(slot="S2")
    assert c.heal_targets == _BASE_HEAL_TARGETS
    c.deployed = True; c.position = (0.0, 1.0)
    w.add_unit(c)

    c.skill.sp = float(c.skill.sp_cost)
    w.tick()

    assert c.heal_targets == _S2_HEAL_TARGETS


def test_s2_heal_targets_restored_on_end():
    """heal_targets and ATK buff both reset when S2 expires."""
    w = _world()
    c = make_ceylon(slot="S2")
    c.deployed = True; c.position = (0.0, 1.0)
    w.add_unit(c)

    c.skill.sp = float(c.skill.sp_cost)
    w.tick()

    for _ in range(int(TICK_RATE * (_S2_DURATION + 2))):
        w.tick()

    assert c.heal_targets == _BASE_HEAL_TARGETS
    assert not any(b.source_tag == _S2_BUFF_TAG for b in c.buffs)


def test_s3_regression():
    c = make_ceylon(slot="S3")
    assert c.skill is not None and c.skill.slot == "S3"
    assert c.skill.name == "Quiet Recovery"
