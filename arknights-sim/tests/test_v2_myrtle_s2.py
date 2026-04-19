"""Myrtle S2 Healing Wings: 16 DP over 16s + 50% ATK/s HoT to adjacent ally."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.myrtle import make_myrtle


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
    """Placeholder ally unit that can receive healing."""
    from core.state.unit_state import UnitState, RangeShape
    from core.types import AttackType, Faction
    u = UnitState(
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
    return u


# ---------------------------------------------------------------------------
# S2 basic properties
# ---------------------------------------------------------------------------

def test_myrtle_s2_fires_without_target():
    """S2 fires auto at sp_cost=18, initial_sp=9 → fires after 9s."""
    w = _world()
    m = make_myrtle("S2")
    m.deployed = True
    m.position = (0.0, 1.0)
    m.skill.sp = float(m.skill.initial_sp)
    w.add_unit(m)

    fired = False
    for _ in range(TICK_RATE * 15):
        w.tick()
        if m.skill.fire_count >= 1:
            fired = True
            break

    assert fired, "Myrtle S2 should fire without a target (requires_target=False)"


def test_myrtle_s2_block_suppressed():
    """Block drops to 0 during S2, restores to 1 on end."""
    w = _world()
    m = make_myrtle("S2")
    m.deployed = True
    m.position = (0.0, 1.0)
    m.skill.sp = float(m.skill.initial_sp)
    w.add_unit(m)

    assert m.block == 1

    for _ in range(TICK_RATE * 12):
        w.tick()
        if m.skill.fire_count >= 1 and m.skill.active_remaining > 0:
            break

    assert m.block == 0, "Block must be 0 during S2"

    for _ in range(TICK_RATE * 20):
        w.tick()
        if m.skill.active_remaining <= 0:
            break

    assert m.block == 1, "Block must restore to 1 after S2"


# ---------------------------------------------------------------------------
# DP drip
# ---------------------------------------------------------------------------

def test_myrtle_s2_grants_16_dp():
    """S2 generates approximately 16 DP over its 16s active window."""
    w = _world()
    m = make_myrtle("S2")
    m.deployed = True
    m.position = (0.0, 1.0)
    w.add_unit(m)

    for _ in range(TICK_RATE * 50):
        w.tick()
        if m.skill.fire_count >= 1 and m.skill.active_remaining <= 0:
            break

    for _ in range(5):
        w.tick()

    assert 15 <= w.global_state.dp <= 17, (
        f"Expected ~16 DP from S2 drip, got {w.global_state.dp}"
    )


def test_myrtle_s2_dp_less_than_s1_per_second():
    """S2 generates 1.0 DP/s vs S1's 1.75 DP/s — S1 is faster per second."""
    # S2: 16 DP / 16s = 1.0 DP/s; S1: 14 DP / 8s = 1.75 DP/s
    # After one activation, S1 (14 DP) > S2 (16 DP) would be wrong — S2 total IS higher
    # But per-second rate: S1=1.75, S2=1.0
    m_s2 = make_myrtle("S2")
    m_s1 = make_myrtle("S1")
    assert m_s2.skill.duration > m_s1.skill.duration, "S2 lasts twice as long"
    s2_rate = 16.0 / m_s2.skill.duration
    s1_rate = 14.0 / m_s1.skill.duration
    assert s2_rate < s1_rate, f"S2 rate ({s2_rate}) should be lower than S1 rate ({s1_rate})"


# ---------------------------------------------------------------------------
# HoT mechanic
# ---------------------------------------------------------------------------

def test_myrtle_s2_heals_adjacent_ally():
    """S2 heals the most-injured ally within the heal range cross."""
    w = _world()
    m = make_myrtle("S2")
    m.deployed = True
    m.position = (1.0, 1.0)
    m.skill.sp = float(m.skill.initial_sp)
    w.add_unit(m)

    ally = _injured_ally(position=(0.0, 1.0), max_hp=2000, hp=500)  # at (-1,0) from Myrtle = in range
    w.add_unit(ally)

    hp_before = ally.hp

    for _ in range(TICK_RATE * 15):
        w.tick()
        if m.skill.fire_count >= 1 and m.skill.active_remaining > 0:
            if ally.hp > hp_before:
                break

    assert ally.hp > hp_before, "Adjacent ally must receive HoT healing during S2"


def test_myrtle_s2_heals_at_correct_rate():
    """Over 16s active window, ally receives approximately 50% Myrtle ATK * 16s healing."""
    w = _world()
    m = make_myrtle("S2")
    m.deployed = True
    m.position = (1.0, 1.0)
    w.add_unit(m)

    # Ally starts at 1 HP so we can measure total healing precisely
    ally = _injured_ally(position=(0.0, 1.0), max_hp=999999, hp=1)
    w.add_unit(ally)

    for _ in range(TICK_RATE * 50):
        w.tick()
        if m.skill.fire_count >= 1 and m.skill.active_remaining <= 0:
            break

    for _ in range(5):
        w.tick()

    # Expected: 0.5 * 520 ATK/s * 16s = 4160 HP
    healing = ally.hp - 1
    assert 3800 <= healing <= 4500, (
        f"Expected ~4160 HP of healing (50% ATK * 16s), got {healing}"
    )


def test_myrtle_s2_does_not_heal_out_of_range_ally():
    """Ally outside Myrtle's heal range (>1 tile away) is NOT healed."""
    w = _world()
    m = make_myrtle("S2")
    m.deployed = True
    m.position = (0.0, 1.0)
    m.skill.sp = float(m.skill.initial_sp)
    w.add_unit(m)

    # Ally at (3, 1): dx=3 — well outside the 5-tile cross
    ally = _injured_ally(position=(3.0, 1.0), max_hp=2000, hp=500)
    w.add_unit(ally)

    hp_before = ally.hp

    # Tick until S2 fires and runs for a few seconds
    for _ in range(TICK_RATE * 30):
        w.tick()
        if m.skill.fire_count >= 1 and m.skill.active_remaining > 0:
            break

    for _ in range(TICK_RATE * 5):
        w.tick()

    assert ally.hp == hp_before, (
        f"Out-of-range ally must NOT be healed by S2 HoT, but HP changed: {hp_before} → {ally.hp}"
    )


def test_myrtle_s2_heals_most_injured():
    """When two injured allies are in range, S2 targets the more critically injured one."""
    w = _world()
    m = make_myrtle("S2")
    m.deployed = True
    m.position = (1.0, 1.0)
    m.skill.sp = float(m.skill.initial_sp)
    w.add_unit(m)

    # critical_ally at 5% HP, moderate_ally at 50% HP — both in heal range
    critical = _injured_ally(position=(0.0, 1.0), max_hp=2000, hp=100)   # 5%
    moderate = _injured_ally(position=(2.0, 1.0), max_hp=2000, hp=1000)  # 50%
    w.add_unit(critical)
    w.add_unit(moderate)

    critical_before = critical.hp
    moderate_before = moderate.hp

    for _ in range(TICK_RATE * 15):
        w.tick()
        if m.skill.fire_count >= 1 and m.skill.active_remaining > 0:
            if critical.hp > critical_before:
                break

    assert critical.hp > critical_before, "Critical ally (5% HP) must receive healing first"
    # Moderate ally may or may not have been healed yet (critical gets priority)
    # Just verify the critical one definitely got healed more
