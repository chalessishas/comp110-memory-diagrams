"""Ptilopsis talent 'Unisonant': all operators gain +0.3 SP/s while deployed."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.ptilopsis import make_ptilopsis
from data.characters.myrtle import make_myrtle
from data.characters.texas import make_texas


def _world() -> World:
    grid = TileGrid(width=4, height=3)
    for x in range(4):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


# ---------------------------------------------------------------------------
# Test 1: Talent is registered
# ---------------------------------------------------------------------------

def test_ptilopsis_talent_registered():
    p = make_ptilopsis()
    assert len(p.talents) == 1
    assert p.talents[0].name == "Unisonant"


# ---------------------------------------------------------------------------
# Test 2: Unisonant accelerates SP gain for ally
# ---------------------------------------------------------------------------

def test_unisonant_accelerates_sp():
    """With Ptilopsis deployed, ally gains SP faster than alone (0.3 SP/s bonus)."""
    w = _world()

    ptilo = make_ptilopsis()
    ptilo.deployed = True
    ptilo.position = (0.0, 1.0)
    ptilo.atk_cd = 999.0
    w.add_unit(ptilo)

    myrtle = make_myrtle(slot="S1")
    myrtle.deployed = True
    myrtle.position = (1.0, 1.0)
    myrtle.atk_cd = 999.0
    myrtle.skill.sp = 0.0
    w.add_unit(myrtle)

    # Without Ptilopsis: AUTO_TIME adds 1.0 SP/s → 10 ticks = 1.0 SP
    # With Ptilopsis bonus: 1.3 SP/s → 10 ticks ≈ 1.3 SP
    for _ in range(TICK_RATE):
        w.tick()

    assert myrtle.skill.sp > 1.05, (
        f"Ptilopsis should accelerate SP beyond 1.0/s; got {myrtle.skill.sp:.3f} SP in 1s"
    )


# ---------------------------------------------------------------------------
# Test 3: Unisonant does NOT benefit Ptilopsis herself
# ---------------------------------------------------------------------------

def test_unisonant_skips_self():
    """Ptilopsis's talent does not apply the SP bonus to herself."""
    w = _world()

    ptilo = make_ptilopsis(slot="S1")
    ptilo.deployed = True
    ptilo.position = (0.0, 1.0)
    ptilo.atk_cd = 999.0
    ptilo.skill.sp = 0.0
    w.add_unit(ptilo)

    # 10 ticks = 1s — Ptilopsis's own skill charges only via AUTO_TIME (1 SP/s)
    # If talent applied to self: would be 1.3 SP/s
    for _ in range(TICK_RATE):
        w.tick()

    # SP should be approximately 1.0 (AUTO_TIME only), not 1.3 (with bonus)
    assert ptilo.skill.sp <= 1.05, (
        f"Ptilopsis should NOT get the SP bonus herself; got {ptilo.skill.sp:.3f}"
    )


# ---------------------------------------------------------------------------
# Test 4: Unisonant does not exceed sp_cost
# ---------------------------------------------------------------------------

def test_unisonant_sp_capped():
    """SP gained via Unisonant never exceeds the skill's sp_cost."""
    w = _world()

    ptilo = make_ptilopsis()
    ptilo.deployed = True
    ptilo.position = (0.0, 1.0)
    ptilo.atk_cd = 999.0
    w.add_unit(ptilo)

    myrtle = make_myrtle(slot="S1")
    myrtle.deployed = True
    myrtle.position = (1.0, 1.0)
    myrtle.atk_cd = 999.0
    myrtle.skill.sp = 0.0
    w.add_unit(myrtle)

    # Run for a long time — SP should cap at sp_cost and not overflow
    for _ in range(TICK_RATE * 60):
        w.tick()

    assert myrtle.skill.sp <= myrtle.skill.sp_cost, (
        f"SP must not exceed sp_cost; got {myrtle.skill.sp} > {myrtle.skill.sp_cost}"
    )


# ---------------------------------------------------------------------------
# Test 5: Unisonant does not grant SP to active skills
# ---------------------------------------------------------------------------

def test_unisonant_skips_active_skill():
    """An ally whose skill is currently active should not gain extra SP."""
    w = _world()

    ptilo = make_ptilopsis()
    ptilo.deployed = True
    ptilo.position = (0.0, 1.0)
    ptilo.atk_cd = 999.0
    w.add_unit(ptilo)

    myrtle = make_myrtle(slot="S1")
    myrtle.deployed = True
    myrtle.position = (1.0, 1.0)
    myrtle.atk_cd = 999.0
    myrtle.skill.sp = myrtle.skill.sp_cost   # ready
    w.add_unit(myrtle)

    w.tick()  # Myrtle S1 fires
    assert myrtle.skill.active_remaining > 0.0, "S1 must be active"
    sp_while_active = myrtle.skill.sp

    for _ in range(5):
        w.tick()

    # SP should remain at 0 (skill fired and reset), not accumulate while active
    assert myrtle.skill.sp <= sp_while_active + 0.1, (
        "SP must not accumulate while skill is active"
    )
