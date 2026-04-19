"""Perfumer passive talent — global HoT: all allies +5% ATK HP/s."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.perfumer import make_perfumer
from data.characters.fang import make_fang


def _world() -> World:
    grid = TileGrid(width=4, height=2)
    for x in range(4):
        for y in range(2):
            grid.set_tile(TileState(x=x, y=y, type=TileType.ELEVATED))
    w = World(tile_grid=grid)
    w.global_state.dp = 100
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _deploy_perf(w, pos=(0, 0)):
    p = make_perfumer()
    p.position = pos
    p.deployed = True
    w.add_unit(p)
    return p


def test_perfumer_talent_registered():
    """Perfumer unit has a talent registered in the registry."""
    p = make_perfumer()
    assert p.talents, "Perfumer must have at least one talent"
    assert p.talents[0].behavior_tag == "perfumer_passive_hot"


def test_perfumer_heals_injured_ally():
    """An injured deployed ally receives HP each tick while Perfumer is deployed."""
    w = _world()
    perf = _deploy_perf(w)

    ally = make_fang()
    ally.deployed = True
    ally.position = (2, 0)
    ally.max_hp = 1000
    ally.hp = 500   # 50% HP — should be healed
    w.add_unit(ally)

    hp_before = ally.hp
    for _ in range(TICK_RATE * 5):   # 5 seconds
        w.tick()

    assert ally.hp > hp_before, "Injured ally must gain HP from Perfumer passive"


def test_perfumer_heal_rate():
    """Over 10 seconds, ally should receive ≈ 10 × 5% × ATK HP (±15% tolerance).

    Perfumer's auto-attack is disabled (atk_cd=999) so only the passive HoT contributes.
    """
    w = _world()
    perf = _deploy_perf(w)
    perf.atk_cd = 999.0   # block combat heals; only passive talent fires

    ally = make_fang()
    ally.deployed = True
    ally.position = (2, 0)
    ally.max_hp = 99999
    ally.hp = 1     # nearly dead — ensure heal never saturates
    w.add_unit(ally)

    hp_before = ally.hp
    for _ in range(TICK_RATE * 10):
        w.tick()

    healed = ally.hp - hp_before
    expected = perf.effective_atk * 0.05 * 10   # 5% ATK * 10 seconds
    assert abs(healed - expected) / expected < 0.15, (
        f"Heal {healed:.1f} not within 15% of expected {expected:.1f}"
    )


def test_perfumer_does_not_overheal():
    """Ally at full HP should not receive healing (no overheal)."""
    w = _world()
    _deploy_perf(w)

    ally = make_fang()
    ally.deployed = True
    ally.position = (2, 0)
    ally.max_hp = 500
    ally.hp = 500   # full HP
    w.add_unit(ally)

    for _ in range(TICK_RATE * 10):
        w.tick()

    assert ally.hp == 500, "Full-HP ally must not be overhealed"


def test_perfumer_heals_multiple_allies():
    """All injured deployed allies receive the HoT simultaneously."""
    w = _world()
    _deploy_perf(w, pos=(0, 0))

    allies = []
    for i in range(3):
        a = make_fang()
        a.deployed = True
        a.position = (i + 1, 0)
        a.max_hp = 99999
        a.hp = 1
        w.add_unit(a)
        allies.append(a)

    for _ in range(TICK_RATE * 5):
        w.tick()

    for i, a in enumerate(allies):
        assert a.hp > 1, f"Ally {i} must be healed by Perfumer passive"


def test_perfumer_no_heal_when_not_deployed():
    """Passive HoT only fires when Perfumer is alive and deployed."""
    w = _world()
    perf = make_perfumer()
    perf.position = (0, 0)
    # NOT deployed — add via add_unit but deployed=False
    perf.deployed = False
    w.add_unit(perf)

    ally = make_fang()
    ally.deployed = True
    ally.position = (2, 0)
    ally.max_hp = 1000
    ally.hp = 500
    w.add_unit(ally)

    hp_before = ally.hp
    for _ in range(TICK_RATE * 10):
        w.tick()

    assert ally.hp == hp_before, "Passive must not fire when Perfumer is not deployed"
