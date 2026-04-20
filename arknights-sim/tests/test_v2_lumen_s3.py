"""Lumen S3 Emergency Protocol — burst heal all + ATK+100% + heal_targets→7."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis
from core.systems import register_default_systems
from data.characters.lumen import (
    make_lumen,
    _S3_ATK_RATIO, _S3_BUFF_TAG, _S3_BURST_RATIO,
    _S3_HEAL_TARGETS, _S3_DURATION, _BASE_HEAL_TARGETS,
)


def _world(w=6, h=3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def _ally(world: World, x: float = 2.0, y: float = 1.0, max_hp: int = 1000, start_hp: int = 500):
    from core.state.unit_state import UnitState
    from core.types import Faction
    a = UnitState(name="Ally", faction=Faction.ALLY, max_hp=max_hp, atk=0, defence=0, res=0.0)
    a.alive = True; a.deployed = True; a.position = (x, y)
    a.hp = start_hp
    world.add_unit(a)
    return a


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def test_lumen_s3_config():
    l = make_lumen(slot="S3")
    sk = l.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.name == "Emergency Protocol"
    assert sk.sp_cost == 35


# ---------------------------------------------------------------------------
# Burst heal on activation
# ---------------------------------------------------------------------------

def test_s3_burst_heals_all_allies():
    """S3 activation instantly heals every deployed ally."""
    w = _world()
    l = make_lumen(slot="S3")
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    l.deploy_time = w.global_state.elapsed

    ally1 = _ally(w, x=1.0, y=1.0, max_hp=1000, start_hp=400)
    ally2 = _ally(w, x=2.0, y=1.0, max_hp=800, start_hp=300)
    w.add_unit(l)

    expected_burst = int(l.effective_atk * _S3_BURST_RATIO)

    l.skill.sp = float(l.skill.sp_cost)
    w.tick()  # S3 activates → burst fires in on_start

    assert ally1.hp > 400, "Ally1 must be healed by S3 burst"
    assert ally2.hp > 300, "Ally2 must be healed by S3 burst"


def test_s3_burst_amount():
    """Burst heal equals 150% of Lumen's effective ATK."""
    w = _world()
    l = make_lumen(slot="S3")
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    l.deploy_time = w.global_state.elapsed

    # Single ally that can absorb the full burst (start_hp=1, max_hp=99999)
    ally = _ally(w, x=1.0, y=1.0, max_hp=99999, start_hp=1)
    w.add_unit(l)

    expected_burst = int(l.effective_atk * _S3_BURST_RATIO)
    l.skill.sp = float(l.skill.sp_cost)
    w.tick()

    healed = ally.hp - 1
    assert healed == expected_burst, f"Expected burst={expected_burst}, got {healed}"


def test_s3_does_not_overheal():
    """Burst heal caps at max_hp."""
    w = _world()
    l = make_lumen(slot="S3")
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    l.deploy_time = w.global_state.elapsed

    ally = _ally(w, x=1.0, y=1.0, max_hp=100, start_hp=99)
    w.add_unit(l)

    l.skill.sp = float(l.skill.sp_cost)
    w.tick()

    assert ally.hp <= ally.max_hp, "HP must not exceed max_hp"


# ---------------------------------------------------------------------------
# ATK buff applied on activation
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    """S3 applies ATK+100% on activation."""
    w = _world()
    l = make_lumen(slot="S3")
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    l.deploy_time = w.global_state.elapsed
    w.add_unit(l)

    l.skill.sp = float(l.skill.sp_cost)
    w.tick()

    buff = next((b for b in l.buffs if b.source_tag == _S3_BUFF_TAG), None)
    assert buff is not None, "S3 ATK buff must be applied"
    assert buff.axis == BuffAxis.ATK
    assert buff.value == _S3_ATK_RATIO


# ---------------------------------------------------------------------------
# heal_targets increases during S3
# ---------------------------------------------------------------------------

def test_s3_heal_targets_increases():
    """S3 expands heal_targets to 7."""
    w = _world()
    l = make_lumen(slot="S3")
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    l.deploy_time = w.global_state.elapsed
    w.add_unit(l)

    assert l.heal_targets == _BASE_HEAL_TARGETS
    l.skill.sp = float(l.skill.sp_cost)
    w.tick()

    assert l.heal_targets == _S3_HEAL_TARGETS, f"Expected {_S3_HEAL_TARGETS}, got {l.heal_targets}"


# ---------------------------------------------------------------------------
# S3 expiry — state reverted
# ---------------------------------------------------------------------------

def test_s3_reverts_on_end():
    """ATK buff and heal_targets revert when S3 expires."""
    w = _world()
    l = make_lumen(slot="S3")
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    l.deploy_time = w.global_state.elapsed
    w.add_unit(l)

    l.skill.sp = float(l.skill.sp_cost)
    w.tick()

    for _ in range(int(TICK_RATE * (_S3_DURATION + 2))):
        w.tick()

    assert not any(b.source_tag == _S3_BUFF_TAG for b in l.buffs), "ATK buff must clear on S3 end"
    assert l.heal_targets == _BASE_HEAL_TARGETS, "heal_targets must revert to base on S3 end"


# ---------------------------------------------------------------------------
# Regression: S2 still works
# ---------------------------------------------------------------------------

def test_s2_regression():
    l = make_lumen(slot="S2")
    assert l.skill is not None and l.skill.slot == "S2"
    assert l.skill.name == "Group Recovery"
