"""Pallas S3 War Ode — ATK+200% Arts + block+2."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis, AttackType
from core.systems import register_default_systems
from data.characters.pallas import (
    make_pallas,
    _S3_ATK_RATIO, _S3_ATK_BUFF_TAG, _S3_BLOCK_BONUS, _S3_DURATION,
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


def _slug(world: World, x: float = 1.0, y: float = 1.0):
    from core.state.unit_state import UnitState
    from core.types import Faction
    e = UnitState(name="Slug", faction=Faction.ENEMY, max_hp=9999, atk=0, defence=0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def test_pallas_s3_config():
    p = make_pallas(slot="S3")
    sk = p.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.name == "War Ode"
    assert sk.sp_cost == 50


# ---------------------------------------------------------------------------
# S3 activation effects
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    """S3 applies ATK+200% on activation."""
    w = _world()
    p = make_pallas(slot="S3")
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    _slug(w)
    w.add_unit(p)

    p.skill.sp = float(p.skill.sp_cost)
    w.tick()

    buff = next((b for b in p.buffs if b.source_tag == _S3_ATK_BUFF_TAG), None)
    assert buff is not None, "S3 ATK buff must be applied"
    assert buff.axis == BuffAxis.ATK
    assert buff.value == _S3_ATK_RATIO


def test_s3_attack_type_becomes_arts():
    """S3 converts Pallas's attacks to Arts damage."""
    w = _world()
    p = make_pallas(slot="S3")
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    _slug(w)
    w.add_unit(p)

    assert p.attack_type == AttackType.PHYSICAL
    p.skill.sp = float(p.skill.sp_cost)
    w.tick()

    assert p.attack_type == AttackType.ARTS, "Attack type must be Arts while S3 active"


def test_s3_block_increases():
    """S3 increases block by _S3_BLOCK_BONUS (2 → 4)."""
    w = _world()
    p = make_pallas(slot="S3")
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    _slug(w)
    w.add_unit(p)

    base_block = p.block
    p.skill.sp = float(p.skill.sp_cost)
    w.tick()

    assert p.block == base_block + _S3_BLOCK_BONUS, "Block must increase by 2 during S3"


# ---------------------------------------------------------------------------
# S3 expiry — all mutations restored
# ---------------------------------------------------------------------------

def test_s3_reverts_on_end():
    """ATK buff, attack type, and block all revert when S3 expires."""
    w = _world()
    p = make_pallas(slot="S3")
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    _slug(w)
    w.add_unit(p)

    p.skill.sp = float(p.skill.sp_cost)
    w.tick()

    for _ in range(int(TICK_RATE * (_S3_DURATION + 2))):
        w.tick()

    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in p.buffs), "ATK buff must be removed"
    assert p.attack_type == AttackType.PHYSICAL, "Attack type must revert to Physical"
    assert p.block == 2, "Block must revert to 2"


# ---------------------------------------------------------------------------
# Regression: S2 still works
# ---------------------------------------------------------------------------

def test_s2_regression():
    p = make_pallas(slot="S2")
    assert p.skill is not None and p.skill.slot == "S2"
    assert p.skill.name == "Blessing of the Muses"
