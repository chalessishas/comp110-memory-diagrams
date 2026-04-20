"""Ifrit S3 Flamethrower — range expand + ATK+220% + 60% ATK/s burn aura."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis
from core.systems import register_default_systems
from data.characters.ifrit import (
    make_ifrit,
    _S3_ATK_RATIO, _S3_BUFF_TAG, _S3_BURN_RATIO,
    _S3_DURATION, _S3_RANGE, CORE_CASTER_RANGE,
)


def _world(w=8, h=5) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def _enemy(world: World, x: float, y: float, res: float = 0.0):
    from core.state.unit_state import UnitState
    from core.types import Faction
    e = UnitState(name="Enemy", faction=Faction.ENEMY, max_hp=99999, atk=0,
                  defence=0, res=res)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


_IFRIT_POS = (0.0, 2.0)
# dx=4 is in _S3_RANGE but NOT in CORE_CASTER_RANGE (max dx=2/3)
_ENEMY_EXTENDED = (4.0, 2.0)   # in S3 range only
_ENEMY_NORMAL = (2.0, 2.0)     # in both ranges
_ENEMY_OUT = (5.0, 2.0)        # dx=5, out of S3 range


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def test_ifrit_s3_config():
    i = make_ifrit(slot="S3")
    sk = i.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.name == "Flamethrower"
    assert sk.sp_cost == 50


# ---------------------------------------------------------------------------
# ATK buff applied on activation
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    """S3 applies ATK+220% on activation."""
    w = _world()
    i = make_ifrit(slot="S3")
    i.deployed = True; i.position = _IFRIT_POS; i.atk_cd = 999.0
    _enemy(w, *_ENEMY_NORMAL)
    w.add_unit(i)

    i.skill.sp = float(i.skill.sp_cost)
    w.tick()

    buff = next((b for b in i.buffs if b.source_tag == _S3_BUFF_TAG), None)
    assert buff is not None, "S3 ATK buff must be applied"
    assert buff.axis == BuffAxis.ATK
    assert buff.value == _S3_ATK_RATIO


# ---------------------------------------------------------------------------
# Range expansion
# ---------------------------------------------------------------------------

def test_s3_expands_range():
    """During S3, Ifrit's range_shape is replaced with the expanded zone."""
    w = _world()
    i = make_ifrit(slot="S3")
    i.deployed = True; i.position = _IFRIT_POS; i.atk_cd = 999.0
    _enemy(w, *_ENEMY_NORMAL)
    w.add_unit(i)

    assert set(i.range_shape.tiles) == set(CORE_CASTER_RANGE.tiles), "Pre-S3 range must be base range"
    i.skill.sp = float(i.skill.sp_cost)
    w.tick()

    assert set(i.range_shape.tiles) == set(_S3_RANGE.tiles), "S3 must expand range_shape"


# ---------------------------------------------------------------------------
# Burn aura reaches extended tiles
# ---------------------------------------------------------------------------

def test_s3_burns_extended_range_enemy():
    """An enemy at dx=4 (outside base range) takes burn damage during S3."""
    w = _world()
    i = make_ifrit(slot="S3")
    i.deployed = True; i.position = _IFRIT_POS; i.atk_cd = 999.0
    enemy_ext = _enemy(w, *_ENEMY_EXTENDED)
    w.add_unit(i)

    i.skill.sp = float(i.skill.sp_cost)
    for _ in range(TICK_RATE * 2 + 2):
        w.tick()

    assert enemy_ext.hp < enemy_ext.max_hp, "Enemy in extended range must take burn damage"


def test_s3_no_burn_out_of_range():
    """Enemies beyond dx=4 do NOT take burn damage."""
    w = _world()
    i = make_ifrit(slot="S3")
    i.deployed = True; i.position = _IFRIT_POS; i.atk_cd = 999.0
    enemy_out = _enemy(w, *_ENEMY_OUT)
    w.add_unit(i)

    i.skill.sp = float(i.skill.sp_cost)
    for _ in range(TICK_RATE * 2 + 2):
        w.tick()

    assert enemy_out.hp == enemy_out.max_hp, "Out-of-range enemy must not take burn damage"


# ---------------------------------------------------------------------------
# Range reverts on S3 end
# ---------------------------------------------------------------------------

def test_s3_range_reverts_on_end():
    """range_shape and ATK buff are restored when S3 expires."""
    w = _world()
    i = make_ifrit(slot="S3")
    i.deployed = True; i.position = _IFRIT_POS; i.atk_cd = 999.0
    _enemy(w, *_ENEMY_NORMAL)
    w.add_unit(i)

    i.skill.sp = float(i.skill.sp_cost)
    w.tick()

    for _ in range(int(TICK_RATE * (_S3_DURATION + 2))):
        w.tick()

    assert set(i.range_shape.tiles) == set(CORE_CASTER_RANGE.tiles), "range_shape must revert after S3"
    assert not any(b.source_tag == _S3_BUFF_TAG for b in i.buffs), "ATK buff must clear on S3 end"


# ---------------------------------------------------------------------------
# Regression: S2 still works
# ---------------------------------------------------------------------------

def test_s2_regression():
    i = make_ifrit(slot="S2")
    assert i.skill is not None and i.skill.slot == "S2"
    assert i.skill.name == "Combustion"
