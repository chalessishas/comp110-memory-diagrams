"""Shining — Illuminate talent (heal→shield) + S2 Faith (instant shield)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, RangeShape
from core.types import TileType, TICK_RATE, Faction, AttackType, StatusKind
from core.systems import register_default_systems
from data.characters.shining import make_shining
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _tank(pos=(0, 1), hp=5000, atk=0) -> UnitState:
    t = UnitState(
        name="Tank",
        faction=Faction.ALLY,
        max_hp=hp, hp=hp, atk=atk, atk_interval=9999.0,
        block=1, attack_type=AttackType.PHYSICAL,
        range_shape=RangeShape(tiles=()), deployed=True,
        position=(float(pos[0]), float(pos[1])), alive=True,
    )
    return t


def _slug(pos=(2, 1), hp=9999, atk=300) -> UnitState:
    path = [(int(pos[0]), int(pos[1]))] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = atk; e.move_speed = 0.0
    e.deployed = True
    e.position = (float(pos[0]), float(pos[1]))
    return e


# ---------------------------------------------------------------------------
# Test 1: Illuminate talent is registered
# ---------------------------------------------------------------------------

def test_shining_illuminate_talent_registered():
    s = make_shining()
    assert len(s.talents) == 1
    assert s.talents[0].name == "Illuminate"


# ---------------------------------------------------------------------------
# Test 2: Illuminate applies SHIELD after Shining heals
# ---------------------------------------------------------------------------

def test_illuminate_applies_shield_on_heal():
    """When Shining heals an ally, that ally gains a SHIELD status."""
    w = _world()

    shining = make_shining(slot="S2")
    shining.deployed = True
    shining.position = (0.0, 1.0)
    shining.atk_cd = 0.0
    w.add_unit(shining)

    tank = _tank(pos=(1, 1), hp=5000)
    tank.hp = 4000   # damaged — eligible for heal
    w.add_unit(tank)

    # Let Shining heal once (atk_cd=0, no skill → normal heal)
    for _ in range(5):
        w.tick()

    assert tank.has_status(StatusKind.SHIELD), (
        "Tank must have SHIELD after being healed by Shining's Illuminate talent"
    )


# ---------------------------------------------------------------------------
# Test 3: SHIELD absorbs damage before HP
# ---------------------------------------------------------------------------

def test_shield_absorbs_damage():
    """A unit with SHIELD takes damage from shield pool before losing HP."""
    w = _world()

    # Use S2 to apply a large shield instantly
    shining = make_shining(slot="S2")
    shining.deployed = True
    shining.position = (0.0, 1.0)
    shining.atk_cd = 999.0
    shining.skill.sp = shining.skill.sp_cost
    w.add_unit(shining)

    tank = _tank(pos=(1, 1), hp=5000)
    tank.hp = 1000   # most injured → gets shield
    hp_original = tank.hp
    w.add_unit(tank)

    # S2 fires on next tick, applies shield
    w.tick()
    assert tank.has_status(StatusKind.SHIELD), "S2 must apply SHIELD to most-injured ally"

    shield_amount = next(
        s.params.get("amount", 0) for s in tank.statuses
        if s.kind == StatusKind.SHIELD
    )
    assert shield_amount > 0, "Shield pool must be positive"

    # Deal damage less than shield — HP should be unchanged
    damage_to_deal = shield_amount // 2
    tank.take_physical(damage_to_deal + tank.defence)   # ensure at least damage_to_deal raw

    # HP should not have changed (shield absorbed)
    assert tank.hp == hp_original, (
        f"SHIELD must absorb damage before HP; HP changed {hp_original} → {tank.hp}"
    )


# ---------------------------------------------------------------------------
# Test 4: SHIELD expires after duration
# ---------------------------------------------------------------------------

def test_illuminate_shield_expires():
    """Illuminate's shield expires after 10 seconds."""
    w = _world()

    shining = make_shining(slot="S2")
    shining.deployed = True
    shining.position = (0.0, 1.0)
    shining.atk_cd = 0.0
    w.add_unit(shining)

    tank = _tank(pos=(1, 1), hp=5000)
    tank.hp = 4000
    w.add_unit(tank)

    # Wait for heal and shield to be applied
    for _ in range(10):
        w.tick()

    assert tank.has_status(StatusKind.SHIELD), "Shield must be applied"

    # Disable Shining healing (prevent refresh)
    shining.atk_cd = 999.0

    # Advance 11 more seconds (past 10s expiry)
    for _ in range(TICK_RATE * 11):
        w.tick()

    assert not tank.has_status(StatusKind.SHIELD), "Illuminate shield must expire after 10s"


# ---------------------------------------------------------------------------
# Test 5: S2 applies shield to most-injured ally instantly
# ---------------------------------------------------------------------------

def test_s2_faith_applies_shield_instantly():
    """S2 Faith applies a large shield to the most-injured ally on activation."""
    w = _world()

    shining = make_shining(slot="S2")
    shining.deployed = True
    shining.position = (0.0, 1.0)
    shining.atk_cd = 999.0
    shining.skill.sp = shining.skill.sp_cost
    w.add_unit(shining)

    tank = _tank(pos=(1, 1), hp=5000)
    tank.hp = 1000
    w.add_unit(tank)

    w.tick()  # S2 fires

    assert tank.has_status(StatusKind.SHIELD), "S2 must apply SHIELD to most-injured ally"
    shield = next(s for s in tank.statuses if s.kind == StatusKind.SHIELD)
    expected = int(shining.effective_atk * 3.0)
    assert abs(shield.params["amount"] - expected) <= 1, (
        f"S2 shield should be ~300% Shining ATK ({expected}); got {shield.params['amount']}"
    )
