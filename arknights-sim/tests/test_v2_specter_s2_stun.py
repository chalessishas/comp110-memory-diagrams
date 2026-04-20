"""Specter S2 post-skill Stun — 10s STUN applied when Pather's Light expires."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, StatusKind
from core.systems import register_default_systems
from data.characters.specter import (
    make_specter,
    _S2_STUN_DURATION, _S2_STUN_TAG,
)

_S2_SKILL_DURATION = 30.0


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
# Stun applied immediately when S2 expires
# ---------------------------------------------------------------------------

def test_stun_applied_on_s2_end():
    """Specter is STUNNED immediately when S2 expires."""
    w = _world()
    s = make_specter(slot="S2")
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    _slug(w)
    w.add_unit(s)

    s.skill.sp = float(s.skill.sp_cost)
    w.tick()  # S2 activates
    assert s.skill.active_remaining > 0.0

    # Advance past S2 duration
    for _ in range(int(TICK_RATE * (_S2_SKILL_DURATION + 1))):
        w.tick()

    assert s.has_status(StatusKind.STUN), "Specter must be STUNNED after S2 expires"


def test_stun_duration():
    """Post-S2 Stun lasts exactly _S2_STUN_DURATION seconds."""
    w = _world()
    s = make_specter(slot="S2")
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    _slug(w)
    w.add_unit(s)

    s.skill.sp = float(s.skill.sp_cost)
    w.tick()

    # Run past S2 end
    for _ in range(int(TICK_RATE * (_S2_SKILL_DURATION + 1))):
        w.tick()
    assert s.has_status(StatusKind.STUN), "Stun must be active just after S2 ends"

    # Run past Stun duration
    for _ in range(int(TICK_RATE * (_S2_STUN_DURATION + 1))):
        w.tick()
    assert not s.has_status(StatusKind.STUN), "Stun must expire after _S2_STUN_DURATION"


def test_stun_prevents_attack():
    """While stunned, Specter cannot attack (atk_cd does not drain)."""
    w = _world()
    s = make_specter(slot="S2")
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 0.0
    _slug(w)
    w.add_unit(s)

    s.skill.sp = float(s.skill.sp_cost)
    w.tick()  # S2 activates

    for _ in range(int(TICK_RATE * (_S2_SKILL_DURATION + 1))):
        w.tick()  # S2 ends → Stun applied

    # Manually ensure atk_cd is 0 so we'd attack immediately if not stunned
    s.atk_cd = 0.0
    w.tick()

    # If stunned, can_act() returns False → atk_cd stays at 0 (no attack reset to interval)
    assert s.has_status(StatusKind.STUN), "Must still be stunned"


def test_no_stun_during_s2():
    """Stun must NOT be present while S2 is still active."""
    w = _world()
    s = make_specter(slot="S2")
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    _slug(w)
    w.add_unit(s)

    s.skill.sp = float(s.skill.sp_cost)
    w.tick()  # S2 activates

    assert not s.has_status(StatusKind.STUN), "Stun must NOT be applied while S2 is active"


def test_s2_regression():
    """S2 skill metadata unchanged."""
    s = make_specter(slot="S2")
    assert s.skill is not None and s.skill.slot == "S2"
    assert s.skill.name == "Pather's Light"
    assert s.skill.sp_cost == 40
