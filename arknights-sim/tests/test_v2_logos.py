"""Logos — deploy-time-gated ATK talent + S2 + S3."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis
from core.systems import register_default_systems
from data.characters.logos import (
    make_logos,
    _TALENT_DELAY, _TALENT_ATK_RATIO, _TALENT_BUFF_TAG,
    _S2_ATK_RATIO, _S2_BUFF_TAG, _S2_DURATION,
    _S3_ATK_RATIO, _S3_BUFF_TAG, _S3_DURATION,
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


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def test_logos_s2_config():
    l = make_logos(slot="S2")
    sk = l.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Theorem Derivation"
    assert sk.sp_cost == 25


def test_logos_s3_config():
    l = make_logos(slot="S3")
    sk = l.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.name == "Absolute Logos"
    assert sk.sp_cost == 40


# ---------------------------------------------------------------------------
# Talent: Stable Hypothesis — deploy-time-gated ATK buff
# ---------------------------------------------------------------------------

def test_talent_not_active_before_delay():
    """No talent buff before _TALENT_DELAY seconds have passed."""
    w = _world()
    l = make_logos(slot="S2")
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    w.add_unit(l)
    l.deploy_time = w.global_state.elapsed

    # Tick for (TALENT_DELAY - 1) seconds
    for _ in range(int(TICK_RATE * (_TALENT_DELAY - 1))):
        w.tick()

    buff = next((b for b in l.buffs if b.source_tag == _TALENT_BUFF_TAG), None)
    assert buff is None, "Talent buff must NOT be active before delay expires"


def test_talent_activates_after_delay():
    """Talent buff appears after _TALENT_DELAY seconds since deploy."""
    w = _world()
    l = make_logos(slot="S2")
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    w.add_unit(l)
    l.deploy_time = w.global_state.elapsed

    for _ in range(int(TICK_RATE * (_TALENT_DELAY + 1))):
        w.tick()

    buff = next((b for b in l.buffs if b.source_tag == _TALENT_BUFF_TAG), None)
    assert buff is not None, "Talent buff must be active after delay expires"
    assert buff.axis == BuffAxis.ATK
    assert buff.value == _TALENT_ATK_RATIO


def test_talent_is_permanent_once_active():
    """Talent buff persists for 30s after activation — no removal."""
    w = _world()
    l = make_logos(slot="S2")
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    w.add_unit(l)
    l.deploy_time = w.global_state.elapsed

    for _ in range(int(TICK_RATE * (_TALENT_DELAY + 30))):
        w.tick()

    buff = next((b for b in l.buffs if b.source_tag == _TALENT_BUFF_TAG), None)
    assert buff is not None, "Talent buff must persist once applied"


# ---------------------------------------------------------------------------
# S2
# ---------------------------------------------------------------------------

def test_s2_atk_buff():
    """S2 applies ATK+60% buff."""
    w = _world()
    l = make_logos(slot="S2")
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    w.add_unit(l)

    l.skill.sp = float(l.skill.sp_cost)
    w.tick()

    buff = next((b for b in l.buffs if b.source_tag == _S2_BUFF_TAG), None)
    assert buff is not None, "S2 ATK buff must be applied"
    assert buff.value == _S2_ATK_RATIO


def test_s2_buff_removed_on_end():
    """S2 ATK buff cleared on expiry."""
    w = _world()
    l = make_logos(slot="S2")
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    w.add_unit(l)

    l.skill.sp = float(l.skill.sp_cost)
    w.tick()

    for _ in range(int(TICK_RATE * (_S2_DURATION + 2))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in l.buffs)


# ---------------------------------------------------------------------------
# S3 regression
# ---------------------------------------------------------------------------

def test_s3_regression():
    l = make_logos(slot="S3")
    assert l.skill is not None and l.skill.slot == "S3"
    assert l.skill.name == "Absolute Logos"
