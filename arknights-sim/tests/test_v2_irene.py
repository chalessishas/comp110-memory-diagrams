"""Irene — Blade of Judgement FRAGILE-on-hit talent + S3 ATK burst."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, AttackType, StatusKind
from core.systems import register_default_systems
from data.characters.irene import (
    make_irene, _TALENT_TAG, _TALENT_FRAGILE_AMOUNT,
    _TALENT_FRAGILE_DURATION, _S3_ATK_RATIO, _S3_DURATION,
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


def _slug(pos=(1, 1), hp=99999, defence=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp
    e.hp = hp
    e.defence = defence
    e.atk = 0
    e.move_speed = 0.0
    e.deployed = True
    e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Talent registered
# ---------------------------------------------------------------------------

def test_irene_talent_registered():
    irene = make_irene()
    assert len(irene.talents) == 1
    assert irene.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: First attack applies FRAGILE status to enemy
# ---------------------------------------------------------------------------

def test_blade_of_judgement_applies_fragile():
    """After Irene hits an enemy, that enemy has FRAGILE status."""
    w = _world()
    irene = make_irene()
    irene.deployed = True
    irene.position = (0.0, 1.0)
    irene.atk_cd = 0.0
    irene.skill = None
    w.add_unit(irene)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    w.tick()  # Irene attacks, on_attack_hit fires

    assert slug.has_status(StatusKind.FRAGILE), "Enemy must be FRAGILE after hit"


# ---------------------------------------------------------------------------
# Test 3: FRAGILE increases damage dealt to enemy
# ---------------------------------------------------------------------------

def test_blade_of_judgement_fragile_amplifies_damage():
    """Second hit deals more damage than first because FRAGILE is active."""
    w = _world()
    irene = make_irene()
    irene.deployed = True
    irene.position = (0.0, 1.0)
    irene.atk_cd = 0.0
    irene.skill = None
    w.add_unit(irene)

    # Enemy with 0 defence so damage = ATK exactly; then FRAGILE adds 20%
    slug = _slug(pos=(1, 1), hp=999999, defence=0)
    w.add_unit(slug)

    hp_before_first = slug.hp
    w.tick()  # first hit, no FRAGILE yet — FRAGILE applied after hit
    dmg_first = hp_before_first - slug.hp

    # Advance to second attack cycle
    for _ in range(int(irene.atk_interval * TICK_RATE) + 1):
        w.tick()

    hp_before_second = slug.hp
    # Wait for another attack
    for _ in range(int(irene.atk_interval * TICK_RATE) + 1):
        w.tick()

    dmg_second = hp_before_second - slug.hp

    assert slug.has_status(StatusKind.FRAGILE), "FRAGILE must still be active"
    assert dmg_second > dmg_first, (
        f"Second hit ({dmg_second}) must be larger than first ({dmg_first}) due to FRAGILE"
    )
    expected_second = int(dmg_first * (1.0 + _TALENT_FRAGILE_AMOUNT))
    assert dmg_second == expected_second, (
        f"Expected second hit = {expected_second} (+20%), got {dmg_second}"
    )


# ---------------------------------------------------------------------------
# Test 4: FRAGILE amount matches parameter
# ---------------------------------------------------------------------------

def test_blade_of_judgement_fragile_amount():
    """FRAGILE status has the correct amount parameter."""
    w = _world()
    irene = make_irene()
    irene.deployed = True
    irene.position = (0.0, 1.0)
    irene.atk_cd = 0.0
    irene.skill = None
    w.add_unit(irene)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    w.tick()

    fragile = next(s for s in slug.statuses if s.kind == StatusKind.FRAGILE)
    assert fragile.params.get("amount") == _TALENT_FRAGILE_AMOUNT


# ---------------------------------------------------------------------------
# Test 5: FRAGILE expires after 2 seconds without being refreshed
# ---------------------------------------------------------------------------

def test_blade_of_judgement_fragile_expires():
    """FRAGILE clears after _TALENT_FRAGILE_DURATION seconds of no attacks."""
    w = _world()
    irene = make_irene()
    irene.deployed = True
    irene.position = (0.0, 1.0)
    irene.atk_cd = 0.0
    irene.skill = None
    w.add_unit(irene)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    w.tick()  # first attack → FRAGILE applied
    assert slug.has_status(StatusKind.FRAGILE), "FRAGILE must be present"

    # Prevent further attacks
    irene.atk_cd = 999.0

    # Wait past the FRAGILE duration
    for _ in range(int(TICK_RATE * (_TALENT_FRAGILE_DURATION + 1))):
        w.tick()

    assert not slug.has_status(StatusKind.FRAGILE), (
        "FRAGILE must expire after 2s without refresh"
    )


# ---------------------------------------------------------------------------
# Test 6: S3 activates ATK buff
# ---------------------------------------------------------------------------

def test_irene_s3_atk_buff():
    """S3 fires: ATK increases by +80%."""
    w = _world()
    irene = make_irene()
    irene.deployed = True
    irene.position = (0.0, 1.0)
    irene.atk_cd = 999.0
    w.add_unit(irene)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    atk_base = irene.effective_atk
    irene.skill.sp = irene.skill.sp_cost
    w.tick()

    assert irene.skill.active_remaining > 0.0, "S3 must be active"
    expected = int(atk_base * (1.0 + _S3_ATK_RATIO))
    assert irene.effective_atk == expected, (
        f"S3 ATK should be {expected}, got {irene.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 7: FRAGILE still applied during S3
# ---------------------------------------------------------------------------

def test_irene_fragile_applies_during_s3():
    """Talent FRAGILE applies on every hit, including during S3."""
    w = _world()
    irene = make_irene()
    irene.deployed = True
    irene.position = (0.0, 1.0)
    irene.atk_cd = 0.0
    w.add_unit(irene)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    irene.skill.sp = irene.skill.sp_cost
    for _ in range(5):
        w.tick()

    assert slug.has_status(StatusKind.FRAGILE), "FRAGILE must apply during S3 as well"


# ---------------------------------------------------------------------------
# Test 8: S3 ATK buff removed on expiry
# ---------------------------------------------------------------------------

def test_irene_s3_buff_removed_on_end():
    """ATK reverts to base after S3 expires."""
    w = _world()
    irene = make_irene()
    irene.deployed = True
    irene.position = (0.0, 1.0)
    irene.atk_cd = 999.0
    w.add_unit(irene)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    atk_base = irene.effective_atk
    irene.skill.sp = irene.skill.sp_cost
    w.tick()

    for _ in range(int(TICK_RATE * (_S3_DURATION + 1))):
        w.tick()

    assert irene.skill.active_remaining == 0.0, "S3 must have expired"
    assert irene.effective_atk == atk_base, "ATK must revert to base after S3"
