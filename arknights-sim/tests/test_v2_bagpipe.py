"""Bagpipe — Glorious March talent (Vanguard ATK +25%) + S3 Last Wish."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, StatusKind
from core.systems import register_default_systems
from data.characters.bagpipe import make_bagpipe, _MARCH_ATK_RATIO, _S3_ATK_RATIO
from data.characters.myrtle import make_myrtle
from data.characters.texas import make_texas
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


def _slug(pos=(2, 1), hp=99999, atk=0):
    path = [(int(pos[0]), int(pos[1]))] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = atk; e.move_speed = 0.0
    e.deployed = True; e.position = (float(pos[0]), float(pos[1]))
    return e


# ---------------------------------------------------------------------------
# Test 1: Talent is registered
# ---------------------------------------------------------------------------

def test_bagpipe_talent_registered():
    b = make_bagpipe()
    assert len(b.talents) == 1
    assert b.talents[0].name == "Glorious March"


# ---------------------------------------------------------------------------
# Test 2: Glorious March buffs other Vanguards' ATK
# ---------------------------------------------------------------------------

def test_glorious_march_buffs_vanguard_atk():
    """While Bagpipe is deployed, all other Vanguards get ATK +25%."""
    w = _world()

    bagpipe = make_bagpipe(slot="S3")
    bagpipe.deployed = True; bagpipe.position = (0.0, 1.0); bagpipe.atk_cd = 999.0
    w.add_unit(bagpipe)

    myrtle = make_myrtle(slot="S1")
    myrtle.deployed = True; myrtle.position = (1.0, 1.0); myrtle.atk_cd = 999.0
    w.add_unit(myrtle)

    atk_base = myrtle.effective_atk
    w.tick()  # passive_talent_system fires

    expected = int(atk_base * (1.0 + _MARCH_ATK_RATIO))
    assert myrtle.effective_atk == expected, (
        f"Glorious March must give Myrtle ATK {expected}; got {myrtle.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: Glorious March does NOT buff non-Vanguards
# ---------------------------------------------------------------------------

def test_glorious_march_skips_non_vanguard():
    """Glorious March applies only to Vanguards."""
    from core.state.unit_state import UnitState, RangeShape
    from core.types import Faction, AttackType, Profession
    w = _world()

    bagpipe = make_bagpipe()
    bagpipe.deployed = True; bagpipe.position = (0.0, 1.0); bagpipe.atk_cd = 999.0
    w.add_unit(bagpipe)

    guard = UnitState(
        name="Guard", faction=Faction.ALLY, max_hp=5000, hp=5000, atk=500,
        atk_interval=9999.0, block=1, attack_type=AttackType.PHYSICAL,
        range_shape=RangeShape(tiles=()), deployed=True, position=(1.0, 1.0), alive=True,
    )
    guard.profession = Profession.GUARD
    atk_base = guard.atk
    w.add_unit(guard)

    w.tick()

    assert guard.effective_atk == atk_base, (
        "Glorious March must not buff non-Vanguards"
    )


# ---------------------------------------------------------------------------
# Test 4: Glorious March buff removed when Bagpipe retreats
# ---------------------------------------------------------------------------

def test_glorious_march_removed_on_retreat():
    """When Bagpipe retreats, Vanguard buff expires quickly."""
    w = _world()
    w.global_state.dp = 100.0  # ensure retreat refund works

    bagpipe = make_bagpipe()
    bagpipe.deployed = True; bagpipe.position = (0.0, 1.0); bagpipe.atk_cd = 999.0
    w.add_unit(bagpipe)

    myrtle = make_myrtle(slot="S1")
    myrtle.deployed = True; myrtle.position = (1.0, 1.0); myrtle.atk_cd = 999.0
    w.add_unit(myrtle)

    w.tick()  # buff applied
    assert myrtle.effective_atk > myrtle.atk, "Buff must be active before retreat"

    # Retreat Bagpipe
    w.retreat(bagpipe)

    # Advance 5 ticks — short-lived buff expires (0.3s window)
    for _ in range(5):
        w.tick()

    assert myrtle.effective_atk == myrtle.atk, "Buff must expire after Bagpipe retreats"


# ---------------------------------------------------------------------------
# Test 5: S3 ATK buff activates
# ---------------------------------------------------------------------------

def test_bagpipe_s3_atk_buff():
    """S3 Last Wish applies +200% ATK to Bagpipe."""
    w = _world()
    bagpipe = make_bagpipe(slot="S3")
    bagpipe.deployed = True; bagpipe.position = (0.0, 1.0); bagpipe.atk_cd = 999.0
    w.add_unit(bagpipe)
    slug = _slug((1, 1))
    w.add_unit(slug)

    atk_base = bagpipe.effective_atk
    bagpipe.skill.sp = bagpipe.skill.sp_cost
    w.tick()

    expected = int(atk_base * (1.0 + _S3_ATK_RATIO))
    # Note: Glorious March doesn't apply to Bagpipe herself
    assert bagpipe.effective_atk == expected, (
        f"S3 must give ATK {expected}; got {bagpipe.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 6: S3 applies SLOW on hit
# ---------------------------------------------------------------------------

def test_bagpipe_s3_slow_on_hit():
    """S3: hitting an enemy applies SLOW for 1 second."""
    w = _world()
    bagpipe = make_bagpipe(slot="S3")
    bagpipe.deployed = True; bagpipe.position = (0.0, 1.0); bagpipe.atk_cd = 0.0
    w.add_unit(bagpipe)
    slug = _slug((1, 1), hp=99999)
    w.add_unit(slug)

    bagpipe.skill.sp = bagpipe.skill.sp_cost
    for _ in range(15):
        w.tick()

    assert slug.has_status(StatusKind.SLOW), "Enemy must be SLOWED by S3 on hit"
