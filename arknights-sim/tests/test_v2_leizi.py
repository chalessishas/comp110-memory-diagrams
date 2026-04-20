"""Leizi — Chain Caster archetype (chain_count=2) + S3 Thunderstruck Mane."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.leizi import make_leizi, _BASE_CHAIN_COUNT, _S3_CHAIN_COUNT, _S3_ATK_RATIO
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=8, height=3)
    for x in range(8):
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
# Test 1: Chain Caster archetype and chain_count
# ---------------------------------------------------------------------------

def test_leizi_chain_count():
    l = make_leizi()
    from core.types import RoleArchetype
    assert l.archetype == RoleArchetype.CASTER_CHAIN
    assert l.chain_count == _BASE_CHAIN_COUNT  # 2 extra targets
    assert l.chain_damage_ratio == 1.0


# ---------------------------------------------------------------------------
# Test 2: Single enemy — chain has no extra targets, only primary hit
# ---------------------------------------------------------------------------

def test_chain_with_single_enemy_hits_once():
    """When only one enemy in world, chain finds no extra targets — one hit."""
    w = _world()
    l = make_leizi()
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 0.0
    l.chain_count = 0   # disable chain for clean baseline
    w.add_unit(l)

    slug = _slug((2, 1), hp=99999)
    w.add_unit(slug)

    hp_before = slug.hp
    w.tick()

    dmg = hp_before - slug.hp
    expected = max(1, int(l.atk * (1 - slug.res / 100)))
    assert dmg == expected, f"Single hit: expected {expected}, got {dmg}"


# ---------------------------------------------------------------------------
# Test 3: Chain attacks 3 enemies (primary + 2) simultaneously
# ---------------------------------------------------------------------------

def test_chain_hits_three_enemies():
    """With chain_count=2 and 3 enemies in world, all 3 take damage in one attack."""
    w = _world()
    l = make_leizi()
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 0.0
    w.add_unit(l)

    s1 = _slug((2, 1), hp=99999)
    s2 = _slug((3, 1), hp=99999)
    s3 = _slug((4, 1), hp=99999)
    for s in (s1, s2, s3):
        w.add_unit(s)

    hp1 = s1.hp; hp2 = s2.hp; hp3 = s3.hp
    w.tick()

    assert s1.hp < hp1, "Primary target must be hit"
    assert s2.hp < hp2, "First chain target must be hit"
    assert s3.hp < hp3, "Second chain target must be hit"


# ---------------------------------------------------------------------------
# Test 4: Chain stops at chain_count — 4th enemy NOT hit
# ---------------------------------------------------------------------------

def test_chain_does_not_exceed_chain_count():
    """With chain_count=2, only 3 enemies hit total; 4th enemy untouched."""
    w = _world()
    l = make_leizi()
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 0.0
    w.add_unit(l)

    slugs = [_slug((2 + i, 1), hp=99999) for i in range(4)]
    for s in slugs:
        w.add_unit(s)

    hp_before = [s.hp for s in slugs]
    w.tick()

    hits = sum(1 for i, s in enumerate(slugs) if s.hp < hp_before[i])
    assert hits == 3, f"Chain_count=2 must hit exactly 3 enemies; hit {hits}"


# ---------------------------------------------------------------------------
# Test 5: S3 increases chain_count to 5
# ---------------------------------------------------------------------------

def test_s3_increases_chain_count():
    """S3 Thunderstruck Mane: chain_count jumps to 5 when skill fires."""
    w = _world()
    l = make_leizi(slot="S3")
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    w.add_unit(l)

    # Need a target so S3 can fire
    s = _slug((2, 1), hp=99999)
    w.add_unit(s)

    assert l.chain_count == _BASE_CHAIN_COUNT

    l.skill.sp = l.skill.sp_cost
    w.tick()

    assert l.chain_count == _S3_CHAIN_COUNT, (
        f"S3 must set chain_count={_S3_CHAIN_COUNT}; got {l.chain_count}"
    )


# ---------------------------------------------------------------------------
# Test 6: S3 ATK buff applies correctly, chain_count reverts on end
# ---------------------------------------------------------------------------

def test_s3_atk_buff_and_revert():
    """S3: ATK +50% during skill; chain_count reverts to 2 on skill end."""
    w = _world()
    l = make_leizi(slot="S3")
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    w.add_unit(l)

    s = _slug((2, 1), hp=9999999)  # huge HP to survive duration
    w.add_unit(s)

    atk_base = l.effective_atk
    l.skill.sp = l.skill.sp_cost
    w.tick()

    expected_atk = int(atk_base * (1.0 + _S3_ATK_RATIO))
    assert l.effective_atk == expected_atk, (
        f"S3 ATK buff: expected {expected_atk}, got {l.effective_atk}"
    )

    # Run past 20s duration to let skill expire
    for _ in range(TICK_RATE * 21):
        w.tick()

    assert l.skill.active_remaining == 0.0, "Skill must have expired"
    assert l.chain_count == _BASE_CHAIN_COUNT, (
        f"chain_count must revert to {_BASE_CHAIN_COUNT} after S3; got {l.chain_count}"
    )
    assert l.effective_atk == l.atk, "ATK buff must be removed after S3"
