"""Skadi S3 Abyssal Resonance — ATK+200% / RES+100 / 3%-per-second HP drain."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis
from core.systems import register_default_systems
from data.characters.skadi import (
    make_skadi,
    _S3_ATK_RATIO, _S3_RES_BONUS, _S3_DRAIN_PCT,
    _S3_BUFF_TAG_ATK, _S3_BUFF_TAG_RES, _S3_DURATION,
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


def _slug(world: World, x: float = 1.0, y: float = 1.0):
    from core.state.unit_state import UnitState
    from core.types import Faction
    e = UnitState(name="Slug", faction=Faction.ENEMY, max_hp=9999, atk=0, defence=0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def test_skadi_s3_config():
    s = make_skadi(slot="S3")
    sk = s.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.name == "Abyssal Resonance"
    assert sk.sp_cost == 55


# ---------------------------------------------------------------------------
# Buffs applied on activation
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    """S3 applies ATK+200% buff on activation."""
    w = _world()
    s = make_skadi(slot="S3")
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    _slug(w)
    w.add_unit(s)

    s.skill.sp = float(s.skill.sp_cost)
    w.tick()

    buff = next((b for b in s.buffs if b.source_tag == _S3_BUFF_TAG_ATK), None)
    assert buff is not None, "S3 ATK buff must be applied"
    assert buff.axis == BuffAxis.ATK
    assert buff.value == _S3_ATK_RATIO


def test_s3_res_buff():
    """S3 applies RES+100 buff on activation."""
    w = _world()
    s = make_skadi(slot="S3")
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    _slug(w)
    w.add_unit(s)

    s.skill.sp = float(s.skill.sp_cost)
    w.tick()

    buff = next((b for b in s.buffs if b.source_tag == _S3_BUFF_TAG_RES), None)
    assert buff is not None, "S3 RES buff must be applied"
    assert buff.axis == BuffAxis.RES
    assert buff.value == _S3_RES_BONUS


# ---------------------------------------------------------------------------
# HP drain during skill
# ---------------------------------------------------------------------------

def test_s3_drains_hp_over_time():
    """HP decreases while S3 is active (drain fires each second)."""
    w = _world()
    s = make_skadi(slot="S3")
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    _slug(w)
    w.add_unit(s)

    s.skill.sp = float(s.skill.sp_cost)
    w.tick()  # activate

    hp_after_activation = s.hp
    # Tick for 5 seconds — expect measurable HP loss
    for _ in range(int(TICK_RATE * 5)):
        w.tick()

    assert s.hp < hp_after_activation, "HP must decrease while S3 drain is active"


def test_s3_drain_does_not_kill():
    """HP drain stops at 1 — Skadi cannot kill herself with S3."""
    w = _world()
    s = make_skadi(slot="S3")
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    _slug(w)
    w.add_unit(s)

    s.skill.sp = float(s.skill.sp_cost)
    w.tick()

    # Drain for the full skill duration + extra
    for _ in range(int(TICK_RATE * (_S3_DURATION + 5))):
        w.tick()

    assert s.hp >= 1, "HP drain must never reduce Skadi to 0"
    assert s.alive, "Skadi must remain alive through entire drain"


# ---------------------------------------------------------------------------
# Buffs cleared on skill end
# ---------------------------------------------------------------------------

def test_s3_buffs_cleared_on_end():
    """Both ATK and RES buffs are removed when S3 expires."""
    w = _world()
    s = make_skadi(slot="S3")
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    _slug(w)
    w.add_unit(s)

    s.skill.sp = float(s.skill.sp_cost)
    w.tick()

    for _ in range(int(TICK_RATE * (_S3_DURATION + 2))):
        w.tick()

    assert not any(b.source_tag == _S3_BUFF_TAG_ATK for b in s.buffs), "ATK buff must be cleared after S3"
    assert not any(b.source_tag == _S3_BUFF_TAG_RES for b in s.buffs), "RES buff must be cleared after S3"


# ---------------------------------------------------------------------------
# Regression: S2 still works
# ---------------------------------------------------------------------------

def test_s2_regression():
    s = make_skadi(slot="S2")
    assert s.skill is not None and s.skill.slot == "S2"
    assert s.skill.name == "Surge"
