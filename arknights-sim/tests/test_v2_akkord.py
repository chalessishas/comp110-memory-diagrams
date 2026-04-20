"""Akkord — CASTER_BLAST blast_pierce line-pierce mechanic, talent, and S2."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import math
from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, Faction, StatusKind
from core.systems import register_default_systems
from data.characters.akkord import (
    make_akkord, _TALENT_ATK_RATIO, _S2_ATK_MULT, _S2_SLOW_DURATION,
)
from data.enemies import make_originium_slug


def _make_tile(x, y):
    return TileState(x=x, y=y, type=TileType.GROUND)


def _world() -> World:
    grid = TileGrid(width=10, height=5)
    for x in range(10):
        for y in range(5):
            grid.set_tile(_make_tile(x, y))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _slug(pos=(1, 2), hp=99999, defence=0, res=0.0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    s = make_originium_slug()
    s.max_hp = hp
    s.hp = hp
    s.defence = defence
    s.res = res
    s.path = [(px, py)] * 20
    s.path_progress = 0.0
    s.position = (float(px), float(py))
    s.move_speed = 0.0
    return s


def _deploy_akkord(world: World, pos=(0, 2), slot="S2") -> UnitState:
    op = make_akkord(slot=slot)
    op.position = (float(pos[0]), float(pos[1]))
    op.deployed = True
    world.add_unit(op)
    return op


def _run(world: World, seconds: float) -> None:
    ticks = int(seconds * 10)
    for _ in range(ticks):
        world.tick()


# --- Blast pierce mechanic ---


def test_blast_pierce_hits_enemies_in_line():
    """Normal attack pierces through all enemies aligned behind the primary target."""
    w = _world()
    op = _deploy_akkord(w, pos=(0, 2))

    # Primary target at (2,2), two more slugs behind at (4,2) and (6,2)
    s1 = _slug(pos=(2, 2), hp=5000)
    s2 = _slug(pos=(4, 2), hp=5000)
    s3 = _slug(pos=(6, 2), hp=5000)
    for s in (s1, s2, s3):
        w.add_unit(s)

    # One attack interval = 2.9s
    _run(w, 3.5)

    assert s1.hp < 5000, "primary target should be hit"
    assert s2.hp < 5000, "in-line enemy should be pierced"
    assert s3.hp < 5000, "further in-line enemy should be pierced"


def test_blast_pierce_misses_off_axis_enemy():
    """Enemy perpendicular to attack ray is NOT hit by blast pierce."""
    w = _world()
    op = _deploy_akkord(w, pos=(0, 2))

    s_target = _slug(pos=(3, 2), hp=5000)   # on ray (y=2)
    s_side   = _slug(pos=(3, 4), hp=5000)   # same x but different y — off axis
    w.add_unit(s_target)
    w.add_unit(s_side)

    _run(w, 3.5)

    assert s_target.hp < 5000
    assert s_side.hp == 5000, "off-axis enemy should NOT be hit"


def test_blast_pierce_behind_attacker_skipped():
    """Enemy behind the attacker (negative projection) is not hit."""
    w = _world()
    # Place Akkord at x=5; target at x=7 (direction +x); enemy at x=3 (behind)
    op = _deploy_akkord(w, pos=(5, 2))

    s_target  = _slug(pos=(7, 2), hp=5000)
    s_behind  = _slug(pos=(3, 2), hp=5000)  # x=3 is behind op at x=5 going right
    w.add_unit(s_target)
    w.add_unit(s_behind)

    _run(w, 3.5)

    assert s_target.hp < 5000
    assert s_behind.hp == 5000, "enemy behind attacker should NOT be hit"


# --- Talent: ATK+17% when ally in range ---


def test_talent_atk_buff_with_ally_in_range():
    """Akkord gains ATK+17% when another ally is deployed in her range."""
    w = _world()
    op = _deploy_akkord(w, pos=(0, 2))

    # Deploy a dummy ally inside Akkord's range (dx=2, dy=0 → (2,2))
    ally = make_akkord(slot="S2")
    ally.position = (2.0, 2.0)
    ally.deployed = True
    w.add_unit(ally)

    base_atk = op.effective_atk
    _run(w, 0.5)  # let on_tick fire

    assert op.effective_atk > base_atk, "ATK should increase with ally in range"
    expected = int(op.atk * (1 + _TALENT_ATK_RATIO))
    assert op.effective_atk == expected


def test_talent_no_buff_without_ally():
    """Without any ally in range, Akkord's ATK is not buffed."""
    w = _world()
    op = _deploy_akkord(w, pos=(0, 2))

    base_atk = op.effective_atk
    _run(w, 0.5)

    assert op.effective_atk == base_atk, "ATK should not change without ally"


def test_talent_buff_removed_when_ally_leaves():
    """When the ally in range dies, the ATK buff is removed next tick."""
    w = _world()
    op = _deploy_akkord(w, pos=(0, 2))

    ally = make_akkord(slot="S2")
    ally.position = (2.0, 2.0)
    ally.deployed = True
    w.add_unit(ally)

    _run(w, 0.5)
    assert op.effective_atk > op.atk

    # Kill the ally
    ally.alive = False
    ally.deployed = False

    _run(w, 0.5)
    assert op.effective_atk == op.atk, "buff should be removed when ally gone"


# --- S2: Harmonic Blast ---


def test_s2_instant_burst_hits_multiple():
    """S2 fires instantly and deals damage to primary + all in-line enemies."""
    w = _world()
    op = _deploy_akkord(w, pos=(0, 2), slot="S2")
    assert op.skill is not None

    s1 = _slug(pos=(2, 2), hp=50000)
    s2 = _slug(pos=(4, 2), hp=50000)
    s3 = _slug(pos=(4, 0), hp=50000)  # off-axis (y=0 vs blast ray y=2)
    for s in (s1, s2, s3):
        w.add_unit(s)

    # Fill SP manually and fire
    op.skill.sp = float(op.skill.sp_cost)
    _run(w, 0.2)

    assert s1.hp < 50000, "primary target should be hit by S2"
    assert s2.hp < 50000, "in-line enemy should be hit by S2"
    assert s3.hp == 50000, "off-axis enemy should NOT be hit by S2"


def test_s2_damage_multiplier():
    """S2 deals 150% ATK Arts damage (verifiable with 0 RES enemies)."""
    w = _world()
    op = _deploy_akkord(w, pos=(0, 2), slot="S2")

    slug = _slug(pos=(3, 2), hp=99999, res=0.0)
    w.add_unit(slug)

    op.skill.sp = float(op.skill.sp_cost)
    op.atk_cd = 99.0  # prevent regular attack from firing in the same tick as S2
    _run(w, 0.2)

    damage_taken = 99999 - slug.hp
    expected = int(op.effective_atk * _S2_ATK_MULT)
    assert damage_taken == expected, f"S2 dmg={damage_taken}, expected={expected}"


def test_s2_applies_slow():
    """S2 applies SLOW status to all enemies hit."""
    w = _world()
    op = _deploy_akkord(w, pos=(0, 2), slot="S2")

    s1 = _slug(pos=(2, 2), hp=99999)
    s2 = _slug(pos=(4, 2), hp=99999)
    for s in (s1, s2):
        w.add_unit(s)

    op.skill.sp = float(op.skill.sp_cost)
    _run(w, 0.2)

    for s in (s1, s2):
        if s.hp < 99999:  # was hit
            kinds = [st.kind for st in s.statuses]
            assert StatusKind.SLOW in kinds, f"{s.name} should have SLOW after S2"
