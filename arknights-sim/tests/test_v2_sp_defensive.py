"""v2 SP charging — AUTO_DEFENSIVE (on-hit) integration tests."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, SkillComponent
from core.types import (
    AttackType, Faction, Profession, SPGainMode, SkillTrigger, TileType, TICK_RATE,
)
from core.systems import register_default_systems
from data.enemies import make_originium_slug
from data.characters import make_liskarm


PATH = [(x, 0) for x in range(4)]


def _world() -> World:
    grid = TileGrid(width=4, height=1)
    for i in range(4):
        grid.set_tile(TileState(x=i, y=0, type=TileType.GROUND))
    w = World(tile_grid=grid)
    register_default_systems(w)
    return w


def _make_defender_with_defensive_skill(sp_cost: int) -> UnitState:
    op = make_liskarm()
    op.deployed = True
    op.position = (1.0, 0.0)
    op.skill = SkillComponent(
        name="Test Defensive Skill",
        slot="S1",
        sp_cost=sp_cost,
        duration=0.0,
        sp_gain_mode=SPGainMode.AUTO_DEFENSIVE,
        trigger=SkillTrigger.AUTO,
        behavior_tag="",
    )
    return op


def test_auto_defensive_sp_charges_on_hit():
    """Operator with AUTO_DEFENSIVE gains 1 SP each time an enemy hits them."""
    w = _world()
    op = _make_defender_with_defensive_skill(sp_cost=10)
    w.add_unit(op)

    slug = make_originium_slug(path=PATH)
    slug.position = (1.0, 0.0)
    slug.deployed = True
    slug.blocked_by_unit_ids = [op.unit_id]
    slug.atk_cd = 0.0
    slug.atk_interval = 99.0   # we'll tick manually; one hit = slug attacks once
    w.add_unit(slug)

    # trigger one enemy attack on the defender
    slug.atk_cd = 0.0
    for _ in range(TICK_RATE):    # 1 second — slug will attack once (atk_interval=99)
        w.tick()
        if op.skill.sp >= 1.0:
            break

    assert op.skill.sp >= 1.0, \
        f"AUTO_DEFENSIVE operator should have gained SP after being hit, got {op.skill.sp}"


def test_auto_defensive_sp_not_gained_when_skill_active():
    """SP does not charge while skill is already active (active_remaining > 0)."""
    w = _world()
    op = _make_defender_with_defensive_skill(sp_cost=3)
    op.skill.sp = 3.0           # start at full SP so skill fires immediately
    op.skill.active_remaining = 5.0   # simulate active skill
    w.add_unit(op)

    slug = make_originium_slug(path=PATH)
    slug.position = (1.0, 0.0)
    slug.deployed = True
    slug.blocked_by_unit_ids = [op.unit_id]
    slug.atk_cd = 0.0
    w.add_unit(slug)

    sp_before = op.skill.sp
    for _ in range(5):
        w.tick()

    # SP must stay at 3.0 (not increase while skill is active)
    assert op.skill.sp == sp_before, \
        f"SP should not charge during active skill, got {op.skill.sp}"
