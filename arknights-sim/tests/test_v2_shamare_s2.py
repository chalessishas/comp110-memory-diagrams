"""Shamare S2 "Puppetmaster" — instant AUTO, applies FRAGILE +65% for 20s to all in-range enemies.

Tests cover:
  - S2 config (slot, name, sp_cost=25, initial_sp=10, duration=0 instant, AUTO_TIME)
  - FRAGILE status applied to in-range enemy on activation
  - FRAGILE amount is +65%
  - FRAGILE expires after 20s
  - Out-of-range enemy receives no FRAGILE
  - S3 regression (slot/name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, SPGainMode, TICK_RATE
from core.systems import register_default_systems
from data.characters.shamare import (
    make_shamare,
    _S2_TAG, _S2_FRAGILE_AMOUNT, _S2_FRAGILE_DURATION, _S2_FRAGILE_TAG,
    SUP_HEXER_RANGE,
)

_SHAMARE_POS = (0.0, 1.0)
# SUP_HEXER_RANGE: dx in [-1,3], dy in [-1,1]
_ENEMY_IN    = (1.0, 1.0)   # dx=1, dy=0 — in range
_ENEMY_OUT   = (5.0, 1.0)   # dx=5 — out of range


def _world() -> World:
    grid = TileGrid(width=8, height=3)
    for x in range(8):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _enemy(world: World, pos, hp=3000) -> UnitState:
    from core.types import Faction
    e = UnitState(name=f"enemy_{pos[0]}_{pos[1]}", faction=Faction.ENEMY,
                  max_hp=hp, atk=0, defence=0, res=0.0)
    e.deployed = True; e.alive = True
    e.position = (float(pos[0]), float(pos[1]))
    e.hp = hp
    e.block = 1
    world.add_unit(e)
    return e


def test_shamare_s2_config():
    op = make_shamare(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Puppetmaster"
    assert sk.sp_cost == 25
    assert sk.initial_sp == 10
    assert sk.duration == 0.0
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.behavior_tag == _S2_TAG


def test_s2_fragile_applied_in_range():
    """FRAGILE applied to in-range enemy on S2 activation."""
    w = _world()
    op = make_shamare(slot="S2")
    op.deployed = True; op.position = _SHAMARE_POS
    enemy = _enemy(w, _ENEMY_IN)
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    fragile = next((s for s in enemy.statuses if s.source_tag == _S2_FRAGILE_TAG), None)
    assert fragile is not None, "FRAGILE should be applied to in-range enemy"
    assert abs(fragile.params["amount"] - _S2_FRAGILE_AMOUNT) < 1e-6


def test_s2_fragile_expires():
    """FRAGILE expires after 20s (enemy must stay alive for status expiry to be checked)."""
    w = _world()
    op = make_shamare(slot="S2")
    op.deployed = True; op.position = _SHAMARE_POS; op.atk_cd = 999.0
    enemy = _enemy(w, _ENEMY_IN, hp=999999)  # huge HP so enemy survives the duration
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    fragile_before = next((s for s in enemy.statuses if s.source_tag == _S2_FRAGILE_TAG), None)
    assert fragile_before is not None

    for _ in range(int(TICK_RATE * (_S2_FRAGILE_DURATION + 2.0))):
        w.tick()

    assert enemy.alive, "Enemy should be alive"
    fragile_after = next((s for s in enemy.statuses if s.source_tag == _S2_FRAGILE_TAG), None)
    assert fragile_after is None, "FRAGILE should have expired"


def test_s2_no_fragile_out_of_range():
    """Enemy outside range receives no FRAGILE."""
    w = _world()
    op = make_shamare(slot="S2")
    op.deployed = True; op.position = _SHAMARE_POS
    enemy = _enemy(w, _ENEMY_OUT)
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    fragile = next((s for s in enemy.statuses if s.source_tag == _S2_FRAGILE_TAG), None)
    assert fragile is None, "Out-of-range enemy should not receive FRAGILE"


def test_s3_regression():
    op = make_shamare(slot="S3")
    assert op.skill is not None and op.skill.slot == "S3"
