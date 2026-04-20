"""Gnosis S3 Permafrost Theory — ATK+150% + instant FREEZE on each hit."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis, StatusKind
from core.systems import register_default_systems
from data.characters.gnosis import (
    make_gnosis,
    _S3_ATK_RATIO, _S3_BUFF_TAG, _S3_FREEZE_DURATION, _S3_DURATION,
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


def _slug(world: World, x: float = 2.0, y: float = 1.0):
    from core.state.unit_state import UnitState
    from core.types import Faction
    e = UnitState(name="Slug", faction=Faction.ENEMY, max_hp=9999, atk=0, defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def test_gnosis_s3_config():
    g = make_gnosis(slot="S3")
    sk = g.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.name == "Permafrost Theory"
    assert sk.sp_cost == 50


# ---------------------------------------------------------------------------
# ATK buff applied on activation
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    """S3 applies ATK+150% on activation."""
    w = _world()
    g = make_gnosis(slot="S3")
    g.deployed = True; g.position = (0.0, 1.0); g.atk_cd = 0.0
    slug = _slug(w)
    w.add_unit(g)

    g.skill.sp = float(g.skill.sp_cost)
    w.tick()

    buff = next((b for b in g.buffs if b.source_tag == _S3_BUFF_TAG), None)
    assert buff is not None, "S3 ATK buff must be applied"
    assert buff.axis == BuffAxis.ATK
    assert buff.value == _S3_ATK_RATIO


# ---------------------------------------------------------------------------
# Instant FREEZE on first hit (no COLD prerequisite)
# ---------------------------------------------------------------------------

def test_s3_first_hit_freezes_directly():
    """S3 applies FREEZE on first hit with S3 active, skipping COLD."""
    w = _world()
    g = make_gnosis(slot="S3")
    g.deployed = True; g.position = (0.0, 1.0); g.atk_cd = 999.0  # don't attack until S3 active
    slug = _slug(w)
    w.add_unit(g)

    g.skill.sp = float(g.skill.sp_cost)
    w.tick()  # tick 1: S3 activates (no attack yet)
    assert g.skill.active_remaining > 0.0, "S3 must be active"

    g.atk_cd = 0.0   # ready to attack on next tick
    w.tick()         # tick 2: Gnosis attacks with S3 active

    assert slug.has_status(StatusKind.FREEZE), "First hit must apply FREEZE (no COLD prerequisite)"
    assert not slug.has_status(StatusKind.COLD), "COLD must not appear when S3 FREEZE applied"


def test_s3_no_cold_during_s3():
    """During S3, targets go directly to FREEZE — COLD is never applied."""
    w = _world()
    g = make_gnosis(slot="S3")
    g.deployed = True; g.position = (0.0, 1.0); g.atk_cd = 999.0
    slug = _slug(w)
    w.add_unit(g)

    g.skill.sp = float(g.skill.sp_cost)
    w.tick()  # S3 activates
    g.atk_cd = 0.0
    w.tick()  # attack with S3 active

    assert not slug.has_status(StatusKind.COLD), "COLD must not be present during S3"
    assert slug.has_status(StatusKind.FREEZE), "Target must be FROZEN during S3"


# ---------------------------------------------------------------------------
# S3 expiry — buff cleared, talent reverts to COLD chain
# ---------------------------------------------------------------------------

def test_s3_buff_cleared_on_end():
    """ATK buff is removed when S3 expires."""
    w = _world()
    g = make_gnosis(slot="S3")
    g.deployed = True; g.position = (0.0, 1.0); g.atk_cd = 999.0
    _slug(w)
    w.add_unit(g)

    g.skill.sp = float(g.skill.sp_cost)
    w.tick()

    for _ in range(int(TICK_RATE * (_S3_DURATION + 2))):
        w.tick()

    assert not any(b.source_tag == _S3_BUFF_TAG for b in g.buffs), "ATK buff must clear on S3 end"


# ---------------------------------------------------------------------------
# Regression: S2 and talent still work
# ---------------------------------------------------------------------------

def test_s2_regression():
    g = make_gnosis(slot="S2")
    assert g.skill is not None and g.skill.slot == "S2"
    assert g.skill.name == "Frozen Silence"
