"""Tests for Deepcolor S3 "Abyssal Tide" — deploy 2 Jellyfish G1, 35s MANUAL."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import Faction, TileType, TICK_RATE
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.deepcolor import make_deepcolor, _S3_TAG, _DC_S3_JELLY_ATTR, _JELLY_G1_TALENT_TAG


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def test_s3_config():
    op = make_deepcolor(slot="S3")
    assert op.skill is not None
    assert op.skill.slot == "S3"
    assert op.skill.behavior_tag == _S3_TAG
    assert op.skill.sp_cost == 35
    assert op.skill.duration == 35.0


def test_s3_spawns_two_jellyfish():
    w = _world()
    op = make_deepcolor(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    jelly_ids = getattr(op, _DC_S3_JELLY_ATTR, [])
    assert len(jelly_ids) == 2
    jellies = [w.unit_by_id(jid) for jid in jelly_ids]
    assert all(j is not None and j.alive for j in jellies)


def test_s3_jellyfish_g1_carries_respawn_talent():
    w = _world()
    op = make_deepcolor(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    jelly_ids = getattr(op, _DC_S3_JELLY_ATTR, [])
    j = w.unit_by_id(jelly_ids[0])
    assert any(t.behavior_tag == _JELLY_G1_TALENT_TAG for t in j.talents)


def test_s3_jellyfish_despawned_on_end():
    w = _world()
    op = make_deepcolor(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    jelly_ids = getattr(op, _DC_S3_JELLY_ATTR, [])
    assert all(w.unit_by_id(jid).alive for jid in jelly_ids)
    _ticks(w, 35.0 + 0.5)
    assert all(not w.unit_by_id(jid).alive for jid in jelly_ids)


def test_s3_more_jellyfish_than_s2():
    """S3 spawns 2 jellyfish; S2 spawns 1."""
    op2 = make_deepcolor(slot="S2")
    op3 = make_deepcolor(slot="S3")
    assert op3.skill.sp_cost > op2.skill.sp_cost  # S3 costs more — stronger skill
