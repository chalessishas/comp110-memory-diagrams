"""Gnosis — Theoretical Analysis RES_DOWN-on-hit talent + S2 ATK burst."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, StatusKind, BuffAxis
from core.systems import register_default_systems
from data.characters.gnosis import (
    make_gnosis, _TALENT_TAG, _RES_DOWN_AMOUNT, _RES_DOWN_DURATION,
    _S2_ATK_RATIO, _S2_DURATION,
)
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


def _slug(pos=(1, 1), hp=999999, res=0.0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp
    e.hp = hp
    e.res = res
    e.defence = 0
    e.atk = 0
    e.move_speed = 0.0
    e.deployed = True
    e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Talent registered
# ---------------------------------------------------------------------------

def test_gnosis_talent_registered():
    g = make_gnosis()
    assert len(g.talents) == 1
    assert g.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: First hit applies RES_DOWN status
# ---------------------------------------------------------------------------

def test_theoretical_analysis_applies_res_down():
    """After Gnosis hits an enemy, that enemy has RES_DOWN status."""
    w = _world()
    g = make_gnosis()
    g.deployed = True
    g.position = (0.0, 1.0)
    g.atk_cd = 0.0
    g.skill = None
    w.add_unit(g)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    w.tick()

    assert slug.has_status(StatusKind.RES_DOWN), "Enemy must have RES_DOWN after hit"


# ---------------------------------------------------------------------------
# Test 3: RES_DOWN status has correct amount param
# ---------------------------------------------------------------------------

def test_res_down_amount_param():
    """RES_DOWN status carries the correct amount parameter."""
    w = _world()
    g = make_gnosis()
    g.deployed = True
    g.position = (0.0, 1.0)
    g.atk_cd = 0.0
    g.skill = None
    w.add_unit(g)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    w.tick()

    rd = next(s for s in slug.statuses if s.kind == StatusKind.RES_DOWN)
    assert rd.params.get("amount") == _RES_DOWN_AMOUNT


# ---------------------------------------------------------------------------
# Test 4: RES_DOWN reduces effective RES
# ---------------------------------------------------------------------------

def test_res_down_reduces_effective_res():
    """After RES_DOWN applied, enemy's effective RES is reduced by _RES_DOWN_AMOUNT."""
    w = _world()
    g = make_gnosis()
    g.deployed = True
    g.position = (0.0, 1.0)
    g.atk_cd = 0.0
    g.skill = None
    w.add_unit(g)

    slug = _slug(pos=(1, 1), res=20.0)
    w.add_unit(slug)

    res_before = slug.effective_stat(BuffAxis.RES, base=slug.res)
    assert res_before == 20.0, f"Expected base res=20, got {res_before}"

    w.tick()  # first hit → RES_DOWN applied

    res_after = slug.effective_stat(BuffAxis.RES, base=slug.res)
    expected = 20.0 - _RES_DOWN_AMOUNT
    assert res_after == expected, (
        f"Effective RES must drop to {expected}, got {res_after}"
    )


# ---------------------------------------------------------------------------
# Test 5: RES_DOWN increases arts damage dealt
# ---------------------------------------------------------------------------

def test_res_down_amplifies_arts_damage():
    """Second hit (with RES_DOWN active) deals more arts damage than first."""
    w = _world()
    g = make_gnosis()
    g.deployed = True
    g.position = (0.0, 1.0)
    g.atk_cd = 0.0
    g.skill = None
    w.add_unit(g)

    slug = _slug(pos=(1, 1), hp=999999, res=0.0)
    w.add_unit(slug)

    hp_before_first = slug.hp
    w.tick()
    dmg_first = hp_before_first - slug.hp  # no RES_DOWN yet

    # Advance to second attack (RES_DOWN active)
    for _ in range(int(g.atk_interval * TICK_RATE) + 1):
        w.tick()
    hp_before_second = slug.hp
    for _ in range(int(g.atk_interval * TICK_RATE) + 1):
        w.tick()
    dmg_second = hp_before_second - slug.hp

    assert slug.has_status(StatusKind.RES_DOWN), "RES_DOWN must still be active"
    assert dmg_second > dmg_first, (
        f"Second hit ({dmg_second}) must exceed first ({dmg_first}) due to RES_DOWN"
    )
    # With res=0 base, RES_DOWN -15 → 1.15× damage
    expected_second = max(1, int(dmg_first * (1.0 + _RES_DOWN_AMOUNT / 100.0)))
    assert dmg_second == expected_second, (
        f"Expected second hit = {expected_second}, got {dmg_second}"
    )


# ---------------------------------------------------------------------------
# Test 6: RES_DOWN expires after _RES_DOWN_DURATION
# ---------------------------------------------------------------------------

def test_res_down_expires():
    """RES_DOWN clears after _RES_DOWN_DURATION seconds without refresh."""
    w = _world()
    g = make_gnosis()
    g.deployed = True
    g.position = (0.0, 1.0)
    g.atk_cd = 0.0
    g.skill = None
    w.add_unit(g)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    w.tick()
    assert slug.has_status(StatusKind.RES_DOWN), "RES_DOWN must be present"

    g.atk_cd = 999.0
    for _ in range(int(TICK_RATE * (_RES_DOWN_DURATION + 1))):
        w.tick()

    assert not slug.has_status(StatusKind.RES_DOWN), "RES_DOWN must expire after 2s"
    # Buff should also be removed
    res_down_buffs = [b for b in slug.buffs if b.axis == BuffAxis.RES and b.value < 0]
    assert len(res_down_buffs) == 0, "RES_DOWN buff must also expire"


# ---------------------------------------------------------------------------
# Test 7: S2 activates ATK buff
# ---------------------------------------------------------------------------

def test_gnosis_s2_atk_buff():
    """S2 fires: ATK increases by +80%."""
    w = _world()
    g = make_gnosis()
    g.deployed = True
    g.position = (0.0, 1.0)
    g.atk_cd = 999.0
    w.add_unit(g)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    atk_base = g.effective_atk
    g.skill.sp = g.skill.sp_cost
    w.tick()

    assert g.skill.active_remaining > 0.0, "S2 must be active"
    expected = int(atk_base * (1.0 + _S2_ATK_RATIO))
    assert g.effective_atk == expected, (
        f"S2 ATK should be {expected}, got {g.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 8: S2 ATK buff removed on expiry
# ---------------------------------------------------------------------------

def test_gnosis_s2_buff_removed_on_end():
    """ATK reverts to base after S2 expires."""
    w = _world()
    g = make_gnosis()
    g.deployed = True
    g.position = (0.0, 1.0)
    g.atk_cd = 999.0
    w.add_unit(g)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    atk_base = g.effective_atk
    g.skill.sp = g.skill.sp_cost
    w.tick()

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert g.skill.active_remaining == 0.0, "S2 must have expired"
    assert g.effective_atk == atk_base, "ATK must revert to base after S2"
