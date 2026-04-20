"""Irene S2 Swift Judgement — ATK+50%, ASPD+20 for 20s."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.irene import (
    make_irene, _S2_TAG, _S2_ATK_RATIO, _S2_ASPD_FLAT, _S2_BUFF_TAG, _S2_DURATION,
)
from data.enemies import make_originium_slug


def _world(w=4, h=3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def _slug(pos=(0, 1)):
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 20)
    e.deployed = True; e.position = (float(px), float(py))
    e.atk = 0; e.move_speed = 0.0
    return e


def test_irene_s2_config():
    ir = make_irene(slot="S2")
    sk = ir.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Swift Judgement"
    assert sk.sp_cost == 25
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff():
    """S2 applies ATK+50% buff."""
    from core.types import BuffAxis, BuffStack
    w = _world()
    ir = make_irene(slot="S2")
    ir.deployed = True; ir.position = (0.0, 1.0); ir.atk_cd = 999.0
    w.add_unit(ir)

    slug = _slug(pos=(0, 1))
    w.add_unit(slug)

    ir.skill.sp = float(ir.skill.sp_cost)
    w.tick()

    buff = next((b for b in ir.buffs if b.source_tag == _S2_BUFF_TAG and b.axis == BuffAxis.ATK), None)
    assert buff is not None, "S2 ATK buff must be applied"
    assert buff.value == _S2_ATK_RATIO


def test_s2_aspd_buff():
    """S2 applies ASPD+20 buff."""
    from core.types import BuffAxis
    w = _world()
    ir = make_irene(slot="S2")
    ir.deployed = True; ir.position = (0.0, 1.0); ir.atk_cd = 999.0
    w.add_unit(ir)

    slug = _slug(pos=(0, 1))
    w.add_unit(slug)

    ir.skill.sp = float(ir.skill.sp_cost)
    w.tick()

    buff = next((b for b in ir.buffs if b.source_tag == _S2_BUFF_TAG and b.axis == BuffAxis.ASPD), None)
    assert buff is not None, "S2 ASPD buff must be applied"
    assert buff.value == _S2_ASPD_FLAT


def test_s2_buffs_removed_on_end():
    """Both buffs cleared when S2 expires."""
    w = _world()
    ir = make_irene(slot="S2")
    ir.deployed = True; ir.position = (0.0, 1.0); ir.atk_cd = 999.0
    ir.skill.sp = float(ir.skill.sp_cost)
    w.add_unit(ir)

    slug = _slug(pos=(0, 1))
    w.add_unit(slug)

    for _ in range(int(TICK_RATE * (_S2_DURATION + 2))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in ir.buffs)


def test_s3_regression():
    ir = make_irene(slot="S3")
    assert ir.skill is not None and ir.skill.slot == "S3"
    assert ir.skill.name == "Sword of Vengeance"
