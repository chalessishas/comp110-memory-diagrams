"""Weedy S3 "Torrential Stream" — ATK+160%, ARTS attacks, AoE all-in-range, 2s BIND on hit, 30s AUTO.

Tests cover:
  - S3 configured correctly (slot, sp_cost, initial_sp, duration, AUTO trigger, requires_target=True)
  - ATK +160% buff applied on S3 start
  - attack_type converts to ARTS during S3
  - _attack_all_in_range flag set during S3
  - BIND applied to enemies on attack during S3
  - ATK buff and ARTS type and _attack_all_in_range cleared on S3 end
  - S2 regression (Water Jet)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, AttackType, SkillTrigger, SPGainMode, StatusKind
from core.systems import register_default_systems
from data.characters.weedy import (
    make_weedy,
    _S3_TAG, _S3_ATK_RATIO, _S3_BUFF_TAG, _S3_DURATION,
    _S3_BIND_DURATION, _S3_BIND_TAG,
    _s3_on_start, _s3_on_end,
)
from data.enemies import make_originium_slug


def _world(w: int = 6, h: int = 3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def _slug(pos=(1, 0), hp=99999, defence=0, res=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 20)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = defence; e.res = float(res)
    e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    weedy = make_weedy(slot="S3")
    sk = weedy.skill
    assert sk is not None
    assert sk.slot == "S3"
    assert sk.name == "Torrential Stream"
    assert sk.sp_cost == 45
    assert sk.initial_sp == 20
    assert sk.duration == _S3_DURATION
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.requires_target is True
    assert sk.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK +160% applied on S3 start
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    weedy = make_weedy(slot="S3")
    base_atk = weedy.effective_atk
    weedy.deployed = True; weedy.position = (0.0, 0.0); weedy.atk_cd = 999.0
    w.add_unit(weedy)

    _s3_on_start(w, weedy)

    buff = next((b for b in weedy.buffs if b.source_tag == _S3_BUFF_TAG), None)
    assert buff is not None, "S3 ATK buff must be present"
    expected = int(base_atk * (1.0 + _S3_ATK_RATIO))
    assert abs(weedy.effective_atk - expected) <= 2


# ---------------------------------------------------------------------------
# Test 3: attack_type converts to ARTS during S3
# ---------------------------------------------------------------------------

def test_s3_attack_type_arts():
    w = _world()
    weedy = make_weedy(slot="S3")
    assert weedy.attack_type == AttackType.PHYSICAL, "Weedy base attack must be PHYSICAL"
    weedy.deployed = True; weedy.position = (0.0, 0.0); weedy.atk_cd = 999.0
    w.add_unit(weedy)

    _s3_on_start(w, weedy)

    assert weedy.attack_type == AttackType.ARTS, "During S3, attack_type must be ARTS"


# ---------------------------------------------------------------------------
# Test 4: _attack_all_in_range flag set during S3
# ---------------------------------------------------------------------------

def test_s3_attack_all_in_range_flag():
    w = _world()
    weedy = make_weedy(slot="S3")
    weedy.deployed = True; weedy.position = (0.0, 0.0); weedy.atk_cd = 999.0
    w.add_unit(weedy)

    assert not getattr(weedy, "_attack_all_in_range", False), "Flag must be False before S3"
    _s3_on_start(w, weedy)
    assert getattr(weedy, "_attack_all_in_range", False), "Flag must be True during S3"


# ---------------------------------------------------------------------------
# Test 5: BIND applied on attack during S3
# ---------------------------------------------------------------------------

def test_s3_bind_on_hit():
    w = _world()
    weedy = make_weedy(slot="S3")
    weedy.deployed = True; weedy.position = (0.0, 0.0); weedy.atk_cd = 999.0
    w.add_unit(weedy)

    enemy = _slug(pos=(1, 0))
    w.add_unit(enemy)

    # Tick 1: S3 auto-activates (SP full, has target); attack blocked by atk_cd=999
    weedy.skill.sp = float(weedy.skill.sp_cost)
    w.tick()
    assert weedy.skill.active_remaining > 0.0, "S3 must be active before testing bind"

    # Tick 2: attack fires with _weedy_bind_active=True → talent applies BIND
    weedy.atk_cd = 0.0
    w.tick()

    bind = next(
        (s for s in enemy.statuses if s.kind == StatusKind.BIND and s.source_tag == _S3_BIND_TAG),
        None,
    )
    assert bind is not None, "Enemy must be BINDed after S3 attack"
    assert bind.expires_at > w.global_state.elapsed, "Bind must not be expired"


# ---------------------------------------------------------------------------
# Test 6: All S3 effects cleared on end
# ---------------------------------------------------------------------------

def test_s3_cleared_on_end():
    w = _world()
    weedy = make_weedy(slot="S3")
    base_atk = weedy.effective_atk
    weedy.deployed = True; weedy.position = (0.0, 0.0); weedy.atk_cd = 999.0
    w.add_unit(weedy)

    _s3_on_start(w, weedy)
    assert weedy.attack_type == AttackType.ARTS
    assert getattr(weedy, "_attack_all_in_range", False)

    _s3_on_end(w, weedy)

    assert weedy.attack_type == AttackType.PHYSICAL, "attack_type must revert to PHYSICAL"
    assert not getattr(weedy, "_attack_all_in_range", False), "_attack_all_in_range must be cleared"
    assert not getattr(weedy, "_weedy_bind_active", False), "_weedy_bind_active must be cleared"
    assert not any(b.source_tag == _S3_BUFF_TAG for b in weedy.buffs), "ATK buff must be cleared"
    assert abs(weedy.effective_atk - base_atk) <= 1


# ---------------------------------------------------------------------------
# Test 7: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    weedy = make_weedy(slot="S2")
    sk = weedy.skill
    assert sk is not None
    assert sk.slot == "S2"
    assert sk.name == "Water Jet"
    assert sk.sp_cost == 25
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
