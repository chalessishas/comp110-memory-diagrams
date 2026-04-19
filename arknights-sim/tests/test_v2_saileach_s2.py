"""Saileach S2 Flagship Order: 20 DP over 20s + global 35% ATK/s HoT."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.saileach import make_saileach


def _world() -> World:
    grid = TileGrid(width=4, height=3)
    for x in range(4):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp = 0
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _injured_ally(position, max_hp=2000, hp=500):
    from core.state.unit_state import UnitState, RangeShape
    from core.types import AttackType, Faction
    return UnitState(
        name="TestAlly",
        faction=Faction.ALLY,
        max_hp=max_hp,
        hp=hp,
        atk=0,
        atk_interval=9999.0,
        block=0,
        attack_type=AttackType.PHYSICAL,
        range_shape=RangeShape(tiles=()),
        deployed=True,
        position=position,
        alive=True,
    )


def test_saileach_s2_fires_auto():
    """S2 fires automatically without a target."""
    w = _world()
    s = make_saileach("S2")
    s.deployed = True
    s.position = (0.0, 1.0)
    s.skill.sp = float(s.skill.initial_sp)
    w.add_unit(s)

    for _ in range(TICK_RATE * 25):
        w.tick()
        if s.skill.fire_count >= 1:
            break

    assert s.skill.fire_count >= 1, "S2 must fire without a target"


def test_saileach_s2_block_suppressed():
    """Block drops to 0 during S2 and restores to 1 after."""
    w = _world()
    s = make_saileach("S2")
    s.deployed = True
    s.position = (0.0, 1.0)
    s.skill.sp = float(s.skill.initial_sp)
    w.add_unit(s)

    assert s.block == 1

    for _ in range(TICK_RATE * 25):
        w.tick()
        if s.skill.fire_count >= 1 and s.skill.active_remaining > 0:
            break

    assert s.block == 0, "Block must be 0 during S2"

    for _ in range(TICK_RATE * 25):
        w.tick()
        if s.skill.active_remaining <= 0:
            break

    assert s.block == 1, "Block must restore to 1 after S2"


def test_saileach_s2_grants_20_dp():
    """S2 generates approximately 20 DP over its 20s active window."""
    w = _world()
    s = make_saileach("S2")
    s.deployed = True
    s.position = (0.0, 1.0)
    w.add_unit(s)

    for _ in range(TICK_RATE * 70):
        w.tick()
        if s.skill.fire_count >= 1 and s.skill.active_remaining <= 0:
            break

    for _ in range(5):
        w.tick()

    assert 18 <= w.global_state.dp <= 22, (
        f"Expected ~20 DP from S2 drip, got {w.global_state.dp}"
    )


def test_saileach_s2_heals_ally_globally():
    """S2 heals injured allies with no range restriction."""
    w = _world()
    s = make_saileach("S2")
    s.deployed = True
    s.position = (0.0, 1.0)
    s.skill.sp = float(s.skill.initial_sp)
    w.add_unit(s)

    # Ally far away — beyond any range shape
    ally = _injured_ally(position=(3.0, 2.0), max_hp=2000, hp=500)
    w.add_unit(ally)

    hp_before = ally.hp

    for _ in range(TICK_RATE * 30):
        w.tick()
        if s.skill.fire_count >= 1 and s.skill.active_remaining > 0:
            if ally.hp > hp_before:
                break

    assert ally.hp > hp_before, "S2 must heal distant ally (no range restriction)"


def test_saileach_s2_heal_rate():
    """Over 20s, global HoT delivers approximately 35% ATK * 20s total healing."""
    w = _world()
    s = make_saileach("S2")
    s.deployed = True
    s.position = (0.0, 1.0)
    w.add_unit(s)

    ally = _injured_ally(position=(3.0, 2.0), max_hp=999999, hp=1)
    w.add_unit(ally)

    for _ in range(TICK_RATE * 70):
        w.tick()
        if s.skill.fire_count >= 1 and s.skill.active_remaining <= 0:
            break

    for _ in range(5):
        w.tick()

    # Expected: 0.35 * 620 ATK/s * 20s = 4340 HP
    expected = 0.35 * s.effective_atk * 20.0
    healing = ally.hp - 1
    assert abs(healing - expected) / expected < 0.15, (
        f"Expected ~{expected:.0f} HP healing (35% ATK * 20s), got {healing}"
    )


def test_saileach_s1_fires_and_grants_dp():
    """S1 fires auto and grants approximately 14 DP over 8s."""
    w = _world()
    s = make_saileach("S1")
    s.deployed = True
    s.position = (0.0, 1.0)
    w.add_unit(s)

    for _ in range(TICK_RATE * 40):
        w.tick()
        if s.skill.fire_count >= 1 and s.skill.active_remaining <= 0:
            break

    for _ in range(5):
        w.tick()

    assert 12 <= w.global_state.dp <= 16, (
        f"Expected ~14 DP from S1 drip, got {w.global_state.dp}"
    )
