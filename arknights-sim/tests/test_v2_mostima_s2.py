"""Mostima S2 Chaos — ranged AoE Arts damage + STUN within MYSTIC_RANGE."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, StatusKind, TICK_RATE
from core.systems import register_default_systems
from data.characters.mostima import (
    make_mostima,
    _S2_TAG, _S2_ATK_RATIO, _S2_STUN_DURATION, _S2_STUN_TAG,
)
from data.enemies import make_originium_slug


def _world(w=8, h=5) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def _slug(pos=(1, 2), hp=999999, res=0):
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 20)
    e.deployed = True
    e.position = (float(px), float(py))
    e.max_hp = hp; e.hp = hp
    e.res = res
    e.atk = 0; e.move_speed = 0.0
    return e


# ---------------------------------------------------------------------------
# Test 1: Config
# ---------------------------------------------------------------------------

def test_mostima_s2_config():
    m = make_mostima(slot="S2")
    sk = m.skill
    assert sk is not None
    assert sk.slot == "S2"
    assert sk.name == "Chaos"
    assert sk.sp_cost == 30
    assert sk.behavior_tag == _S2_TAG


# ---------------------------------------------------------------------------
# Test 2: Arts damage applied to enemies in range
# ---------------------------------------------------------------------------

def test_s2_deals_arts_damage():
    """S2 deals Arts damage (ATK × 210%) to enemies within MYSTIC_RANGE."""
    w = _world()
    m = make_mostima(slot="S2")
    m.deployed = True; m.position = (0.0, 2.0); m.atk_cd = 999.0
    w.add_unit(m)

    slug = _slug(pos=(1, 2), hp=999999, res=0)
    w.add_unit(slug)

    m.skill.sp = float(m.skill.sp_cost)
    hp_before = slug.hp
    w.tick()

    expected_dmg = int(m.effective_atk * _S2_ATK_RATIO)
    actual_dmg = hp_before - slug.hp
    assert actual_dmg == expected_dmg, (
        f"S2 Arts dmg: expected {expected_dmg}, got {actual_dmg}"
    )


# ---------------------------------------------------------------------------
# Test 3: STUN applied
# ---------------------------------------------------------------------------

def test_s2_applies_stun():
    """S2 must apply STUN to each hit enemy."""
    w = _world()
    m = make_mostima(slot="S2")
    m.deployed = True; m.position = (0.0, 2.0); m.atk_cd = 999.0
    w.add_unit(m)

    slug = _slug(pos=(2, 2))
    w.add_unit(slug)

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()

    assert slug.has_status(StatusKind.STUN), "S2 must apply STUN to enemies in range"


# ---------------------------------------------------------------------------
# Test 4: STUN source_tag and duration
# ---------------------------------------------------------------------------

def test_s2_stun_params():
    """STUN must carry correct source_tag and correct expiry."""
    w = _world()
    m = make_mostima(slot="S2")
    m.deployed = True; m.position = (0.0, 2.0); m.atk_cd = 999.0
    w.add_unit(m)

    slug = _slug(pos=(1, 2))
    w.add_unit(slug)

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()

    stun = next((s for s in slug.statuses if s.kind == StatusKind.STUN and s.source_tag == _S2_STUN_TAG), None)
    assert stun is not None, f"STUN with source_tag {_S2_STUN_TAG} must be present"
    dt = 1.0 / TICK_RATE
    assert abs(stun.expires_at - (w.global_state.elapsed + _S2_STUN_DURATION - dt)) < 0.5, (
        f"STUN expires_at should be ~{_S2_STUN_DURATION}s from application"
    )


# ---------------------------------------------------------------------------
# Test 5: Out-of-range enemies NOT hit
# ---------------------------------------------------------------------------

def test_s2_only_hits_in_range():
    """S2 must NOT hit enemies outside MYSTIC_RANGE."""
    w = _world()
    m = make_mostima(slot="S2")
    m.deployed = True; m.position = (0.0, 2.0); m.atk_cd = 999.0
    w.add_unit(m)

    s_in = _slug(pos=(2, 2), hp=999999)    # offset (2,0) — in MYSTIC_RANGE
    s_out = _slug(pos=(5, 2), hp=999999)   # offset (5,0) — out of range
    w.add_unit(s_in)
    w.add_unit(s_out)

    m.skill.sp = float(m.skill.sp_cost)
    hp_in_before = s_in.hp
    hp_out_before = s_out.hp
    w.tick()

    assert s_in.hp < hp_in_before, "In-range enemy must be hit"
    assert s_out.hp == hp_out_before, "Out-of-range enemy must NOT be hit"


# ---------------------------------------------------------------------------
# Test 6: S2 STUN shorter than S3 STUN (design difference)
# ---------------------------------------------------------------------------

def test_s2_stun_shorter_than_s3():
    """S2 STUN duration must be shorter than S3 STUN duration."""
    from data.characters.mostima import _S3_STUN_DURATION
    assert _S2_STUN_DURATION < _S3_STUN_DURATION, (
        f"S2 STUN ({_S2_STUN_DURATION}s) must be shorter than S3 STUN ({_S3_STUN_DURATION}s)"
    )
