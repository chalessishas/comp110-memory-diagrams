"""Myrtle talent 'Glistening': all Vanguards recover 25 HP/s while Myrtle is deployed."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.myrtle import make_myrtle, _GLISTENING_HEAL_RATE
from data.characters.fang import make_fang
from data.characters.texas import make_texas


def _world() -> World:
    grid = TileGrid(width=4, height=3)
    for x in range(4):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


# ---------------------------------------------------------------------------
# Test 1: Myrtle talent Glistening is registered
# ---------------------------------------------------------------------------

def test_myrtle_glistening_talent_registered():
    m = make_myrtle()
    assert len(m.talents) == 1
    assert m.talents[0].name == "Glistening"


# ---------------------------------------------------------------------------
# Test 2: Glistening heals damaged Vanguard over time
# ---------------------------------------------------------------------------

def test_glistening_heals_vanguard():
    """Myrtle's Glistening talent restores HP to a damaged Vanguard ally."""
    w = _world()

    myrtle = make_myrtle(slot="S1")
    myrtle.deployed = True
    myrtle.position = (0.0, 1.0)
    myrtle.atk_cd = 999.0
    w.add_unit(myrtle)

    fang = make_fang()
    fang.deployed = True
    fang.position = (1.0, 1.0)
    fang.atk_cd = 999.0
    fang.hp = fang.max_hp - 500   # 500 HP missing
    w.add_unit(fang)

    # 10 ticks = 1 second → expect ~25 HP healed
    for _ in range(TICK_RATE):
        w.tick()

    healed = fang.hp - (fang.max_hp - 500)
    assert healed >= 24, f"Expected ~25 HP healed in 1s, got {healed}"


# ---------------------------------------------------------------------------
# Test 3: Glistening does NOT heal non-Vanguard allies
# ---------------------------------------------------------------------------

def test_glistening_skips_non_vanguard():
    """Glistening only heals Vanguards; a damaged non-Vanguard should not be healed."""
    from core.state.unit_state import UnitState, RangeShape
    from core.types import Faction, AttackType
    w = _world()

    myrtle = make_myrtle(slot="S1")
    myrtle.deployed = True
    myrtle.position = (0.0, 1.0)
    myrtle.atk_cd = 999.0
    w.add_unit(myrtle)

    # A non-vanguard ally (no profession set → default None)
    from core.types import Profession
    guard = UnitState(
        name="Guard",
        faction=Faction.ALLY,
        max_hp=5000, hp=4000, atk=0, atk_interval=9999.0,
        block=1, attack_type=AttackType.PHYSICAL,
        range_shape=RangeShape(tiles=()), deployed=True,
        position=(1.0, 1.0), alive=True,
    )
    guard.profession = Profession.GUARD
    w.add_unit(guard)

    hp_before = guard.hp
    for _ in range(TICK_RATE * 5):
        w.tick()

    assert guard.hp == hp_before, (
        f"Glistening must not heal non-Vanguards; HP changed {hp_before} → {guard.hp}"
    )


# ---------------------------------------------------------------------------
# Test 4: Glistening does not overheal (HP capped at max)
# ---------------------------------------------------------------------------

def test_glistening_no_overheal():
    """A Vanguard at full HP should not receive healing above max_hp."""
    w = _world()

    myrtle = make_myrtle(slot="S1")
    myrtle.deployed = True
    myrtle.position = (0.0, 1.0)
    myrtle.atk_cd = 999.0
    w.add_unit(myrtle)

    fang = make_fang()
    fang.deployed = True
    fang.position = (1.0, 1.0)
    fang.atk_cd = 999.0
    fang.hp = fang.max_hp   # already full
    w.add_unit(fang)

    for _ in range(TICK_RATE * 10):
        w.tick()

    assert fang.hp == fang.max_hp, "Full-HP Vanguard must not exceed max_hp"


# ---------------------------------------------------------------------------
# Test 5: Glistening heals multiple Vanguards simultaneously
# ---------------------------------------------------------------------------

def test_glistening_heals_multiple_vanguards():
    """Glistening applies to all deployed Vanguards at once."""
    w = _world()

    myrtle = make_myrtle(slot="S1")
    myrtle.deployed = True
    myrtle.position = (0.0, 1.0)
    myrtle.atk_cd = 999.0
    w.add_unit(myrtle)

    fang = make_fang()
    fang.deployed = True
    fang.position = (1.0, 1.0)
    fang.atk_cd = 999.0
    fang.hp = fang.max_hp - 200
    w.add_unit(fang)

    texas = make_texas()
    texas.deployed = True
    texas.position = (2.0, 1.0)
    texas.atk_cd = 999.0
    texas.hp = texas.max_hp - 200
    w.add_unit(texas)

    fang_hp_before = fang.hp
    texas_hp_before = texas.hp

    for _ in range(TICK_RATE * 2):
        w.tick()

    assert fang.hp > fang_hp_before, "Fang (Vanguard) must be healed by Glistening"
    assert texas.hp > texas_hp_before, "Texas (Vanguard) must be healed by Glistening"
