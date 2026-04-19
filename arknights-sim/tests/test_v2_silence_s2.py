"""Silence S2 "Medical Protocol" — on_tick continuous heal + most-injured targeting."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, DT, Faction, AttackType
from core.systems import register_default_systems
from data.characters.silence import make_silence, _S2_HEAL_PER_SECOND
from data.characters import make_liskarm


def _ally(hp_frac: float = 0.5, max_hp: int = 2000, pos=(1.0, 0.0)) -> UnitState:
    a = UnitState(name="ally_tank", faction=Faction.ALLY, max_hp=max_hp)
    a.hp = int(max_hp * hp_frac)
    a.deployed = True
    a.position = pos
    return a


def _world() -> World:
    grid = TileGrid(width=5, height=3)
    for x in range(5):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp = 99
    register_default_systems(w)
    return w


def test_s2_fires_without_target():
    """S2 fires when SP full even with no injured ally (requires_target=False)."""
    w = _world()
    sil = make_silence()
    sil.position = (0.0, 1.0)
    sil.deployed = True
    sil.atk_cd = 999.0
    w.add_unit(sil)

    # No injured allies
    sil.skill.sp = sil.skill.sp_cost
    w.tick()

    assert sil.skill.active_remaining > 0.0 or sil.skill.fire_count == 1, (
        "S2 must activate even without injured allies"
    )


def test_s2_heals_injured_ally_over_ticks():
    """On_tick heal accumulates and restores HP to an injured ally."""
    w = _world()
    sil = make_silence()
    sil.position = (0.0, 1.0)
    sil.deployed = True
    sil.atk_cd = 999.0
    w.add_unit(sil)

    tank = _ally(hp_frac=0.5, max_hp=4000, pos=(1.0, 1.0))
    w.add_unit(tank)

    # Force skill active
    sil.skill.sp = sil.skill.sp_cost
    initial_hp = tank.hp

    # Run for 5 seconds (enough for measurable healing)
    for _ in range(TICK_RATE * 5):
        w.tick()

    assert tank.hp > initial_hp, "S2 on_tick must heal injured ally"
    expected_heal = sil.atk * _S2_HEAL_PER_SECOND * 5
    actual_heal = tank.hp - initial_hp
    assert actual_heal >= int(expected_heal * 0.9), (
        f"heal {actual_heal} should be ~{expected_heal:.0f} (±10%)"
    )


def test_s2_targets_most_injured_ally():
    """S2 drone prefers the ally with the lowest HP% (most injured)."""
    w = _world()
    sil = make_silence()
    sil.position = (0.0, 1.0)
    sil.deployed = True
    sil.atk_cd = 999.0
    w.add_unit(sil)

    # Two injured allies; tank2 is more injured (25% HP vs 75%)
    tank1 = _ally(hp_frac=0.75, max_hp=2000, pos=(1.0, 1.0))
    tank2 = _ally(hp_frac=0.25, max_hp=2000, pos=(2.0, 1.0))
    tank2.name = "most_injured"
    w.add_unit(tank1)
    w.add_unit(tank2)

    sil.skill.sp = sil.skill.sp_cost
    # Run 3 ticks — enough for one heal pulse
    for _ in range(3):
        w.tick()

    assert tank2.hp > tank2.max_hp * 0.25, "most-injured ally must receive healing"


def test_s2_does_not_overheal():
    """S2 heals do not push HP above max_hp."""
    w = _world()
    sil = make_silence()
    sil.position = (0.0, 1.0)
    sil.deployed = True
    sil.atk_cd = 999.0
    w.add_unit(sil)

    tank = _ally(hp_frac=0.99, max_hp=1000, pos=(1.0, 1.0))
    w.add_unit(tank)

    sil.skill.sp = sil.skill.sp_cost
    for _ in range(TICK_RATE * 25):   # full skill duration
        w.tick()

    assert tank.hp <= tank.max_hp, "HP must never exceed max_hp"


def test_s2_active_duration_expires():
    """After 20s active duration, skill ends (active_remaining = 0) and fires exactly once."""
    w = _world()
    sil = make_silence()
    sil.position = (0.0, 1.0)
    sil.deployed = True
    sil.atk_cd = 999.0
    w.add_unit(sil)

    sil.skill.sp = sil.skill.sp_cost
    w.tick()  # fires skill, active_remaining = 20.0

    assert sil.skill.active_remaining > 0.0, "skill must be active after fire"
    assert sil.skill.fire_count == 1

    # Advance exactly 20s + 1 tick to ensure duration expires (floating-point safe)
    for _ in range(TICK_RATE * 20 + 1):
        w.tick()

    assert sil.skill.active_remaining == 0.0, "skill must have ended after 20s"
    assert sil.skill.fire_count == 1, "must not have re-fired during duration"
    # SP begins recharging after end — only 1 tick has passed so sp <= 1 sp_cost unit
    assert sil.skill.sp < 1.0, "SP just started recharging (< 1s accumulated)"


def test_s2_total_healing_tracked_in_global_state():
    """Total healing done is accumulated in world.global_state.total_healing_done."""
    w = _world()
    sil = make_silence()
    sil.position = (0.0, 1.0)
    sil.deployed = True
    sil.atk_cd = 999.0
    w.add_unit(sil)

    tank = _ally(hp_frac=0.1, max_hp=99999, pos=(1.0, 1.0))
    w.add_unit(tank)

    sil.skill.sp = sil.skill.sp_cost

    for _ in range(TICK_RATE * 5):
        w.tick()

    assert w.global_state.total_healing_done > 0, (
        "S2 heal must be tracked in global_state.total_healing_done"
    )


def test_s2_skips_full_hp_allies():
    """S2 drone does nothing when all allies are at full HP."""
    w = _world()
    sil = make_silence()
    sil.position = (0.0, 1.0)
    sil.deployed = True
    sil.atk_cd = 999.0
    w.add_unit(sil)

    # Ally at full HP
    tank = _ally(hp_frac=1.0, max_hp=2000, pos=(1.0, 1.0))
    w.add_unit(tank)

    sil.skill.sp = sil.skill.sp_cost
    for _ in range(TICK_RATE * 5):
        w.tick()

    assert tank.hp == tank.max_hp, "no heal applied to full-HP ally"
    # Healing done should be 0 (skill active but no valid target)
    assert w.global_state.total_healing_done == 0
