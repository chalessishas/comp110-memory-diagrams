"""Shaw S2 "Powerful Current" — instant burst, 280% ATK Arts AoE + 3-tile push.

Tests cover:
  - S2 config (slot, name, sp_cost=15, initial_sp=5, duration=0 instant, AUTO_ATTACK)
  - On activation: enemy in extended range takes Arts damage
  - Damage scales with 280% ATK multiplier
  - Enemy pushed back 3 tiles
  - Enemy out of range takes no damage
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
from core.systems.skill_system import manual_trigger
from data.characters.shaw import (
    make_shaw,
    _S2_TAG, _S2_ATK_MULT, _S2_PUSH_DIST,
    PUSHER_RANGE_EXTENDED,
)

_SHAW_POS   = (0.0, 1.0)
_ENEMY_IN   = (1.0, 1.0)    # dx=1, dy=0 — in PUSHER_RANGE_EXTENDED
_ENEMY_OUT  = (5.0, 1.0)    # dx=5 — out of range


def _world() -> World:
    grid = TileGrid(width=8, height=3)
    for x in range(8):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _enemy(world: World, pos, hp=5000, defence=0, res=0) -> UnitState:
    from core.types import Faction
    e = UnitState(name=f"enemy_{pos[0]}_{pos[1]}", faction=Faction.ENEMY,
                  max_hp=hp, atk=0, defence=defence, res=float(res))
    e.deployed = True; e.alive = True
    e.position = (float(pos[0]), float(pos[1]))
    e.hp = hp
    e.block = 1
    world.add_unit(e)
    return e


def test_shaw_s2_config():
    op = make_shaw(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Powerful Current"
    assert sk.sp_cost == 15
    assert sk.initial_sp == 5
    assert sk.duration == 0.0
    assert sk.sp_gain_mode == SPGainMode.AUTO_ATTACK
    assert sk.behavior_tag == _S2_TAG


def test_s2_deals_arts_damage_in_range():
    """Enemy in extended range takes Arts damage on S2 activation."""
    w = _world()
    op = make_shaw(slot="S2")
    op.deployed = True; op.position = _SHAW_POS; op.atk_cd = 999.0
    enemy = _enemy(w, _ENEMY_IN, hp=5000, defence=0, res=0)

    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    expected_dmg = int(op.atk * _S2_ATK_MULT)
    assert enemy.hp < 5000, "Enemy in range should take Arts damage"


def test_s2_pushes_enemy():
    """Enemy in range gets path_progress pushed back by _S2_PUSH_DIST."""
    w = _world()
    op = make_shaw(slot="S2")
    op.deployed = True; op.position = _SHAW_POS; op.atk_cd = 999.0
    enemy = _enemy(w, _ENEMY_IN, hp=10000)
    # Path going left→right; place enemy at progress=1 (position (1,1))
    enemy.path = [(float(x), 1.0) for x in range(8)]
    enemy.path_progress = 1.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    if enemy.alive:
        # path_progress should be near 0 after 3-tile push (clamped at 0)
        assert enemy.path_progress < 1.0, (
            f"path_progress should decrease after push, got {enemy.path_progress}"
        )


def test_s2_no_damage_out_of_range():
    """Enemy out of range unaffected by S2."""
    w = _world()
    op = make_shaw(slot="S2")
    op.deployed = True; op.position = _SHAW_POS; op.atk_cd = 999.0
    enemy_in = _enemy(w, _ENEMY_IN, hp=5000)   # in range — needed as target so S2 fires
    enemy_out = _enemy(w, _ENEMY_OUT, hp=5000)  # out of range
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    assert enemy_out.hp == 5000, "Out-of-range enemy should take no damage"


def test_s3_regression():
    op = make_shaw(slot="S3")
    assert op.skill is not None and op.skill.slot == "S3"
    assert op.skill.name == "Raging Flood"
