"""Ling S2 Dragon's Majesty — ATK+100% self + +40 flat ATK aura to allies in range."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, Faction
from core.state.unit_state import UnitState, RangeShape
from core.systems import register_default_systems
from data.characters.ling import (
    make_ling, _S2_TAG, _S2_ATK_RATIO, _S2_AURA_BONUS,
    _S2_BUFF_TAG, _S2_AURA_TAG, _S2_DURATION,
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


def _ally(pos, atk=500):
    """Minimal ally unit for aura testing."""
    a = UnitState(
        name="Ally", faction=Faction.ALLY,
        max_hp=1000, hp=1000, atk=atk, defence=100, res=0.0,
        atk_interval=1.0, block=1, cost=0,
        deployed=True, position=(float(pos[0]), float(pos[1])),
    )
    return a


def test_ling_s2_config():
    l = make_ling(slot="S2")
    sk = l.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Dragon's Majesty"
    assert sk.sp_cost == 35
    assert sk.behavior_tag == _S2_TAG


def test_s2_self_atk_buff():
    """S2 applies ATK+100% to Ling herself."""
    w = _world()
    l = make_ling(slot="S2")
    base_atk = l.effective_atk
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    w.add_unit(l)

    l.skill.sp = float(l.skill.sp_cost)
    w.tick()

    expected = int(base_atk * (1 + _S2_ATK_RATIO))
    assert l.effective_atk == expected, f"Self ATK: expected {expected}, got {l.effective_atk}"


def test_s2_ally_aura_in_range():
    """S2 grants +40 flat ATK to allies in range."""
    w = _world()
    l = make_ling(slot="S2")
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    w.add_unit(l)

    a = _ally(pos=(1, 1), atk=500)
    w.add_unit(a)
    base_ally_atk = a.effective_atk

    l.skill.sp = float(l.skill.sp_cost)
    w.tick()

    assert a.effective_atk == base_ally_atk + _S2_AURA_BONUS


def test_s2_no_aura_out_of_range():
    """Allies outside summoner range do NOT receive the aura."""
    w = _world()
    l = make_ling(slot="S2")
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    w.add_unit(l)

    far = _ally(pos=(5, 1), atk=500)
    w.add_unit(far)
    base_far_atk = far.effective_atk

    l.skill.sp = float(l.skill.sp_cost)
    w.tick()

    assert far.effective_atk == base_far_atk, "Out-of-range ally must not receive aura"


def test_s2_buffs_removed_on_end():
    """Self ATK buff and ally aura cleared when S2 expires."""
    w = _world()
    l = make_ling(slot="S2")
    base_atk = l.effective_atk
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    l.skill.sp = float(l.skill.sp_cost)
    w.add_unit(l)

    a = _ally(pos=(1, 1), atk=500)
    w.add_unit(a)
    base_ally_atk = a.effective_atk

    for _ in range(int(TICK_RATE * (_S2_DURATION + 2))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in l.buffs)
    assert l.effective_atk == base_atk
    assert not any(b.source_tag == _S2_AURA_TAG for b in a.buffs)
    assert a.effective_atk == base_ally_atk


def test_s3_regression():
    l = make_ling(slot="S3")
    assert l.skill is not None and l.skill.slot == "S3"
    assert l.skill.name == "Draconic Inspiration"
