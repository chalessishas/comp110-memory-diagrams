"""Nearl — Holy Knight's Light: passive AoE HP restore every 25 seconds."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction
from core.systems import register_default_systems
from data.characters.nearl import make_nearl, _HEAL_INTERVAL, _HEAL_RATIO, _TALENT_TAG


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ally(pos, max_hp=1000, hp_frac=0.5) -> UnitState:
    a = UnitState(name="TestAlly", faction=Faction.ALLY, max_hp=max_hp)
    a.hp = int(max_hp * hp_frac)
    a.deployed = True
    a.position = (float(pos[0]), float(pos[1]))
    return a


# ---------------------------------------------------------------------------
# Test 1: Talent is registered with on_tick hook
# ---------------------------------------------------------------------------

def test_nearl_talent_registered():
    nearl = make_nearl()
    assert len(nearl.talents) == 1
    assert nearl.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: No heal before 25s elapsed
# ---------------------------------------------------------------------------

def test_nearl_no_heal_before_interval():
    """Ally HP must not change before 25s accumulates."""
    w = _world()
    nearl = make_nearl()
    nearl.deployed = True
    nearl.position = (0.0, 1.0)
    w.add_unit(nearl)

    ally = _ally(pos=(0, 1), max_hp=2000, hp_frac=0.5)
    w.add_unit(ally)

    hp_before = ally.hp
    # Run for 24s — just under the threshold
    for _ in range(TICK_RATE * 24):
        w.tick()

    assert ally.hp == hp_before, "No heal should fire before 25s threshold"


# ---------------------------------------------------------------------------
# Test 3: Heal fires at 25s, restores 8% of max_hp
# ---------------------------------------------------------------------------

def test_nearl_heals_at_25s():
    """After 25s, all in-range injured allies receive 8% max_hp healing."""
    w = _world()
    nearl = make_nearl()
    nearl.deployed = True
    nearl.position = (0.0, 1.0)
    w.add_unit(nearl)

    max_hp = 2000
    ally = _ally(pos=(0, 1), max_hp=max_hp, hp_frac=0.5)
    w.add_unit(ally)

    hp_before = ally.hp
    expected_heal = int(max_hp * _HEAL_RATIO)  # 8% of 2000 = 160

    # Run 25s + 1 tick to trigger pulse
    for _ in range(int(TICK_RATE * _HEAL_INTERVAL) + 1):
        w.tick()

    assert ally.hp > hp_before, "Nearl must heal ally after 25s"
    assert ally.hp == min(max_hp, hp_before + expected_heal), (
        f"Heal should be exactly {expected_heal} HP"
    )


# ---------------------------------------------------------------------------
# Test 4: Heal does not affect full-HP allies
# ---------------------------------------------------------------------------

def test_nearl_skips_full_hp_allies():
    """Full-HP allies are not healed by Holy Knight's Light."""
    w = _world()
    nearl = make_nearl()
    nearl.deployed = True
    nearl.position = (0.0, 1.0)
    w.add_unit(nearl)

    ally = _ally(pos=(0, 1), max_hp=1000, hp_frac=1.0)
    w.add_unit(ally)

    for _ in range(int(TICK_RATE * _HEAL_INTERVAL) + 1):
        w.tick()

    assert ally.hp == ally.max_hp, "Full-HP ally should not receive healing"
    assert w.global_state.total_healing_done == 0, "total_healing_done should stay 0"


# ---------------------------------------------------------------------------
# Test 5: Heal only hits allies within range (cross pattern)
# ---------------------------------------------------------------------------

def test_nearl_heal_range_excludes_distant_allies():
    """Ally 3 tiles away (outside 5-tile cross) is NOT healed."""
    w = _world()
    nearl = make_nearl()
    nearl.deployed = True
    nearl.position = (0.0, 1.0)
    w.add_unit(nearl)

    nearby = _ally(pos=(1, 1), max_hp=1000, hp_frac=0.5)   # (1,0) relative — in range
    distant = _ally(pos=(3, 1), max_hp=1000, hp_frac=0.5)  # (3,0) relative — out of range
    w.add_unit(nearby)
    w.add_unit(distant)

    for _ in range(int(TICK_RATE * _HEAL_INTERVAL) + 1):
        w.tick()

    assert nearby.hp > int(1000 * 0.5), "Nearby ally (in range) must be healed"
    assert distant.hp == int(1000 * 0.5), "Distant ally (out of range) must NOT be healed"


# ---------------------------------------------------------------------------
# Test 6: Heal fires repeatedly (second pulse at ~50s)
# ---------------------------------------------------------------------------

def test_nearl_heals_twice():
    """Passive heal pulses every 25s — second pulse fires at ~50s."""
    w = _world()
    nearl = make_nearl()
    nearl.deployed = True
    nearl.position = (0.0, 1.0)
    w.add_unit(nearl)

    ally = _ally(pos=(0, 1), max_hp=10000, hp_frac=0.1)   # very injured
    w.add_unit(ally)

    hp_after_1st = None
    # Run 26s → first pulse fires, record HP
    for _ in range(int(TICK_RATE * 26)):
        w.tick()
    hp_after_1st = ally.hp

    # Run another 26s → second pulse fires
    for _ in range(int(TICK_RATE * 26)):
        w.tick()

    assert hp_after_1st is not None and hp_after_1st > int(10000 * 0.1), "First pulse must fire"
    assert ally.hp > hp_after_1st, "Second pulse must fire and increase HP further"


# ---------------------------------------------------------------------------
# Test 7: total_healing_done accumulates across pulses
# ---------------------------------------------------------------------------

def test_nearl_healing_tracked():
    """Each heal pulse increments global_state.total_healing_done."""
    w = _world()
    nearl = make_nearl()
    nearl.deployed = True
    nearl.position = (0.0, 1.0)
    w.add_unit(nearl)

    ally = _ally(pos=(0, 1), max_hp=5000, hp_frac=0.5)
    w.add_unit(ally)

    for _ in range(int(TICK_RATE * _HEAL_INTERVAL) + 1):
        w.tick()

    assert w.global_state.total_healing_done > 0, (
        "Nearl heal must be tracked in total_healing_done"
    )
