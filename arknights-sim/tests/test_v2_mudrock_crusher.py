"""怒潮凛冬 撼地者 特性: 50% ATK 溅射 1.0 半径, 不伤主目标."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.state.global_state import GlobalState
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.systems import register_default_systems
from core.systems.spawn_system import register_spawn_handler
from core.types import Faction, TileType, AttackType, Mobility
from core.world import World
from data.characters.registry import get_operator


def _grid_8x3() -> TileGrid:
    g = TileGrid(width=8, height=3)
    for x in range(8):
        for y in range(3):
            g.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    return g


def _stationary_enemy(name: str, hp: int, pos: tuple[int, int]) -> UnitState:
    return UnitState(
        name=name,
        faction=Faction.ENEMY,
        max_hp=hp, atk=0, defence=0, res=0,
        atk_interval=99.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=[pos, (pos[0] + 10, pos[1])],
        move_speed=0.0,
        deployed=True,
    )


def test_headb2_splash_hits_co_located_enemy():
    """Primary + co-located enemy both hit. Co-located takes 50% of primary dmg."""
    w = World(tile_grid=_grid_8x3(),
              global_state=GlobalState(max_lives=99, lives=99))
    register_default_systems(w)
    register_spawn_handler(w)

    headb2 = get_operator("headb2")
    headb2.deployed = True
    headb2.position = (2.0, 1.0)
    w.add_unit(headb2)

    primary = _stationary_enemy("A", 9999, (3, 1))   # melee-range adjacent forward
    splash = _stationary_enemy("B", 9999, (3, 1))    # same tile as primary
    primary.position = (3.0, 1.0)
    splash.position = (3.0, 1.0)
    w.add_unit(primary)
    w.add_unit(splash)

    # Run 3 seconds (interval 1.8s → 1-2 hits)
    for _ in range(30):
        w.tick()

    assert headb2.splash_radius == 1.0
    assert headb2.splash_atk_multiplier == 0.5
    assert primary.hp < primary.max_hp, "primary must take damage"
    assert splash.hp < splash.max_hp, "co-located enemy must receive splash"
    # Splash damage = 50% of primary damage (since same DEF=0)
    primary_lost = primary.max_hp - primary.hp
    splash_lost = splash.max_hp - splash.hp
    # Splash should be roughly half; both primary and splash take integer-floored damage
    assert splash_lost == primary_lost // 2, \
        f"splash should be ~50%: primary lost {primary_lost}, splash lost {splash_lost}"


def test_non_crusher_unchanged():
    """SilverAsh is Guard/Lord not Crusher — splash_radius=0 (single target)."""
    silverash = get_operator("silverash")
    assert silverash.splash_radius == 0.0


def test_splash_multiplier_default_is_one():
    """Default splash_atk_multiplier = 1.0 for regular AOE casters (Eyjafjalla etc.)."""
    op = UnitState(name="Test", faction=Faction.ALLY,
                   max_hp=100, atk=100, defence=0, res=0, atk_interval=1.0)
    assert op.splash_atk_multiplier == 1.0
