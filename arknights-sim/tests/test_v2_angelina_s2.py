"""Angelina S2 Frigid Breath — AoE Arts damage + COLD application."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, StatusKind, TICK_RATE
from core.systems import register_default_systems
from data.characters.angelina import (
    make_angelina,
    _S2_TAG, _S2_ATK_RATIO, _S2_COLD_DURATION, _S2_COLD_TAG,
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

def test_angelina_s2_config():
    a = make_angelina(slot="S2")
    sk = a.skill
    assert sk is not None
    assert sk.slot == "S2"
    assert sk.name == "Frigid Breath"
    assert sk.sp_cost == 25
    assert sk.behavior_tag == _S2_TAG


# ---------------------------------------------------------------------------
# Test 2: Arts damage applied to enemies in range
# ---------------------------------------------------------------------------

def test_s2_deals_arts_damage():
    """S2 deals Arts damage (ATK × 150%) to enemies in range."""
    w = _world()
    ang = make_angelina(slot="S2")
    ang.deployed = True; ang.position = (0.0, 2.0); ang.atk_cd = 999.0
    w.add_unit(ang)

    slug = _slug(pos=(1, 2), hp=999999, res=0)
    w.add_unit(slug)

    ang.skill.sp = float(ang.skill.sp_cost)
    hp_before = slug.hp
    w.tick()

    expected_dmg = int(ang.effective_atk * _S2_ATK_RATIO)
    actual_dmg = hp_before - slug.hp
    assert actual_dmg == expected_dmg, (
        f"S2 Arts damage: expected {expected_dmg}, got {actual_dmg}"
    )


# ---------------------------------------------------------------------------
# Test 3: COLD applied to hit enemies
# ---------------------------------------------------------------------------

def test_s2_applies_cold():
    """S2 must apply COLD status to each enemy hit."""
    w = _world()
    ang = make_angelina(slot="S2")
    ang.deployed = True; ang.position = (0.0, 2.0); ang.atk_cd = 999.0
    w.add_unit(ang)

    slug = _slug(pos=(2, 2))
    w.add_unit(slug)

    ang.skill.sp = float(ang.skill.sp_cost)
    w.tick()

    assert slug.has_status(StatusKind.COLD), "S2 must apply COLD to enemies in range"


# ---------------------------------------------------------------------------
# Test 4: COLD carries correct source_tag and duration
# ---------------------------------------------------------------------------

def test_s2_cold_params():
    """COLD status must have correct source_tag and expiry ≈ elapsed + 3s."""
    w = _world()
    ang = make_angelina(slot="S2")
    ang.deployed = True; ang.position = (0.0, 2.0); ang.atk_cd = 999.0
    w.add_unit(ang)

    slug = _slug(pos=(1, 2))
    w.add_unit(slug)

    ang.skill.sp = float(ang.skill.sp_cost)
    w.tick()

    cold = next((s for s in slug.statuses if s.kind == StatusKind.COLD and s.source_tag == _S2_COLD_TAG), None)
    assert cold is not None, f"COLD with source_tag {_S2_COLD_TAG} must be present"
    dt = 1.0 / TICK_RATE
    assert abs(cold.expires_at - (w.global_state.elapsed + _S2_COLD_DURATION - dt)) < 0.5, (
        f"COLD expires_at must be ~{_S2_COLD_DURATION}s from application"
    )


# ---------------------------------------------------------------------------
# Test 5: Out-of-range enemies NOT hit
# ---------------------------------------------------------------------------

def test_s2_only_hits_in_range():
    """S2 must NOT hit enemies outside the operator's range shape."""
    w = _world()
    ang = make_angelina(slot="S2")
    ang.deployed = True; ang.position = (0.0, 2.0); ang.atk_cd = 999.0
    w.add_unit(ang)

    s_in = _slug(pos=(1, 2), hp=999999)    # in range (1,0) relative
    s_out = _slug(pos=(6, 2), hp=999999)   # out of range (tile offset 6 > 4 max)
    w.add_unit(s_in)
    w.add_unit(s_out)

    ang.skill.sp = float(ang.skill.sp_cost)
    hp_in_before = s_in.hp
    hp_out_before = s_out.hp
    w.tick()

    assert s_in.hp < hp_in_before, "In-range enemy must be hit"
    assert s_out.hp == hp_out_before, "Out-of-range enemy must NOT be hit"


# ---------------------------------------------------------------------------
# Test 6: Multiple enemies all hit
# ---------------------------------------------------------------------------

def test_s2_hits_multiple_enemies():
    """S2 AoE must hit all enemies within range simultaneously."""
    w = _world()
    ang = make_angelina(slot="S2")
    ang.deployed = True; ang.position = (0.0, 2.0); ang.atk_cd = 999.0
    w.add_unit(ang)

    s1 = _slug(pos=(1, 2), hp=999999); w.add_unit(s1)
    s2 = _slug(pos=(2, 2), hp=999999); w.add_unit(s2)
    s3 = _slug(pos=(2, 1), hp=999999); w.add_unit(s3)  # (2,-1) offset is in DECEL_RANGE

    hp1, hp2, hp3 = s1.hp, s2.hp, s3.hp
    ang.skill.sp = float(ang.skill.sp_cost)
    w.tick()

    assert s1.hp < hp1, "S2 must hit enemy at (1,2)"
    assert s2.hp < hp2, "S2 must hit enemy at (2,2)"
    assert s3.hp < hp3, "S2 must hit enemy at (2,1)"
    assert s1.has_status(StatusKind.COLD)
    assert s2.has_status(StatusKind.COLD)
    assert s3.has_status(StatusKind.COLD)
