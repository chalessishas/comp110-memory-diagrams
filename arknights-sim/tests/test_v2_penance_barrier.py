"""Penance — Blood Weaving talent: kill-stacking SHIELD + counter-Arts on hit received.

Tests cover:
  - Enemy dies in range → Penance gains SHIELD status
  - Enemy dies outside range → no SHIELD gained
  - Multiple kills stack shield amount
  - Shield capped at _MAX_SHIELD (2500)
  - SHIELD absorbs damage before HP
  - Counter-Arts fires when Penance is hit (enemy hp drops)
  - S2 "Verdict" applies ATK +60% buff
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, Faction, StatusKind, TICK_RATE
from core.systems import register_default_systems
from data.characters.penance import (
    make_penance, _SHIELD_PER_KILL, _MAX_SHIELD, _SHIELD_TAG,
    _COUNTER_RATIO, PENANCE_RANGE,
)
from data.enemies import make_originium_slug


def _world(w=8, h=4) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def _dead_slug(pos=(1, 0)) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 10)
    e.deployed = True
    e.position = (float(px), float(py))
    e.hp = 0
    e.alive = False
    e._just_died = True
    return e


def _penance_at(x: float, y: float) -> UnitState:
    p = make_penance("S2")
    p.deployed = True
    p.position = (x, y)
    p.atk_cd = 999.0
    return p


# ---------------------------------------------------------------------------
# Test 1: Enemy in range → SHIELD status appears
# ---------------------------------------------------------------------------

def test_kill_in_range_gives_shield():
    """Enemy dying within Penance's range grants a SHIELD status effect."""
    w = _world()
    penance = _penance_at(0.0, 0.0)
    w.add_unit(penance)

    # PENANCE_RANGE has (0,0) and (1,0) — slug at (1,0) is in range
    slug = _dead_slug(pos=(1, 0))
    w.add_unit(slug)
    w.tick()

    shield_statuses = [s for s in penance.statuses if s.kind == StatusKind.SHIELD
                       and s.source_tag == _SHIELD_TAG]
    assert len(shield_statuses) == 1, \
        f"Penance must have exactly 1 blood-weaving SHIELD; got {shield_statuses}"
    assert shield_statuses[0].params["amount"] == _SHIELD_PER_KILL, (
        f"Shield must be {_SHIELD_PER_KILL} after one kill; "
        f"got {shield_statuses[0].params['amount']}"
    )


# ---------------------------------------------------------------------------
# Test 2: Enemy outside range → no SHIELD
# ---------------------------------------------------------------------------

def test_kill_out_of_range_no_shield():
    """Enemy dying outside Penance's range must NOT grant a shield."""
    w = _world()
    penance = _penance_at(0.0, 0.0)
    w.add_unit(penance)

    # dx=3 is outside PENANCE_RANGE {(0,0),(1,0)}
    slug = _dead_slug(pos=(3, 0))
    w.add_unit(slug)
    w.tick()

    shield_statuses = [s for s in penance.statuses if s.kind == StatusKind.SHIELD
                       and s.source_tag == _SHIELD_TAG]
    assert len(shield_statuses) == 0, \
        f"Penance must NOT gain shield from kill outside range; got {shield_statuses}"


# ---------------------------------------------------------------------------
# Test 3: Multiple kills stack shield
# ---------------------------------------------------------------------------

def test_multiple_kills_stack_shield():
    """Two kills in range stack the shield to 2 × _SHIELD_PER_KILL."""
    w = _world()
    penance = _penance_at(0.0, 0.0)
    w.add_unit(penance)

    slug1 = _dead_slug(pos=(1, 0))
    slug2 = _dead_slug(pos=(0, 0))
    w.add_unit(slug1)
    w.add_unit(slug2)
    w.tick()

    shield = next((s for s in penance.statuses if s.source_tag == _SHIELD_TAG), None)
    assert shield is not None, "Shield must exist after two kills"
    expected = _SHIELD_PER_KILL * 2
    assert shield.params["amount"] == expected, (
        f"Shield must be {expected} after two kills; got {shield.params['amount']}"
    )


# ---------------------------------------------------------------------------
# Test 4: Shield capped at _MAX_SHIELD
# ---------------------------------------------------------------------------

def test_shield_capped_at_max():
    """Six kills in range must not push shield above _MAX_SHIELD (2500)."""
    w = _world()
    penance = _penance_at(0.0, 0.0)
    w.add_unit(penance)

    # 6 kills × 500 = 3000 would exceed cap → must clamp at 2500
    for _ in range(6):
        slug = _dead_slug(pos=(1, 0))
        w.add_unit(slug)
    w.tick()

    shield = next((s for s in penance.statuses if s.source_tag == _SHIELD_TAG), None)
    assert shield is not None, "Shield must exist"
    assert shield.params["amount"] <= _MAX_SHIELD, (
        f"Shield must be capped at {_MAX_SHIELD}; got {shield.params['amount']}"
    )


# ---------------------------------------------------------------------------
# Test 5: SHIELD absorbs damage before HP
# ---------------------------------------------------------------------------

def test_shield_absorbs_damage_before_hp():
    """When Penance has a blood-weaving shield, incoming damage depletes shield first."""
    from core.state.unit_state import StatusEffect

    w = _world()
    penance = _penance_at(0.0, 0.0)
    w.add_unit(penance)

    # Manually apply a 1000 HP shield
    from core.state.unit_state import StatusEffect
    penance.statuses.append(StatusEffect(
        kind=StatusKind.SHIELD,
        source_tag=_SHIELD_TAG,
        expires_at=float("inf"),
        params={"amount": 1000.0},
    ))

    hp_before = penance.hp
    penance.take_damage(300)

    shield_after = next((s for s in penance.statuses if s.source_tag == _SHIELD_TAG), None)
    assert penance.hp == hp_before, \
        f"HP must be untouched when shield absorbs all damage; hp={penance.hp}"
    assert shield_after is not None, "Shield must still exist (partially consumed)"
    assert shield_after.params["amount"] == 700.0, \
        f"Shield should have 700 HP left; got {shield_after.params['amount']}"


# ---------------------------------------------------------------------------
# Test 6: Counter-Arts fires when Penance is attacked
# ---------------------------------------------------------------------------

def test_counter_arts_deals_damage_to_attacker():
    """When a slug attacks Penance, the counter-Arts fires and reduces slug HP."""
    w = _world()
    penance = _penance_at(1.0, 0.0)
    w.add_unit(penance)

    PATH = [(x, 0) for x in range(4)]
    slug = make_originium_slug(path=PATH)
    slug.position = (1.0, 0.0)
    slug.deployed = True
    slug.blocked_by_unit_ids = [penance.unit_id]
    slug.atk_cd = 0.0
    slug.res = 0.0
    w.add_unit(slug)

    slug_hp_before = slug.hp

    for _ in range(TICK_RATE * 3):
        w.tick()
        if slug.hp < slug_hp_before:
            break

    assert slug.hp < slug_hp_before, (
        f"Counter-Arts must reduce attacker HP; slug HP unchanged at {slug.hp}"
    )


# ---------------------------------------------------------------------------
# Test 7: S2 "Verdict" applies ATK +60% buff
# ---------------------------------------------------------------------------

def test_s2_verdict_atk_buff():
    """Activating S2 'Verdict' boosts Penance's effective ATK by 60%."""
    w = _world()
    penance = make_penance("S2")
    penance.deployed = True
    penance.position = (0.0, 0.0)
    penance.atk_cd = 999.0
    penance.skill.sp = float(penance.skill.sp_cost)  # pre-charge
    w.add_unit(penance)

    atk_base = penance.effective_atk

    # Put a slug in range so requires_target=True fires
    PATH = [(x, 0) for x in range(4)]
    slug = make_originium_slug(path=PATH)
    slug.position = (1.0, 0.0)
    slug.deployed = True
    slug.atk_cd = 999.0
    w.add_unit(slug)

    w.tick()

    assert penance.skill.active_remaining > 0.0, "S2 must be active after tick"
    atk_buffed = penance.effective_atk
    expected = int(atk_base * (1.0 + 0.60))
    assert atk_buffed >= expected, (
        f"S2 must give +60% ATK; base={atk_base}, expected>={expected}, got={atk_buffed}"
    )
