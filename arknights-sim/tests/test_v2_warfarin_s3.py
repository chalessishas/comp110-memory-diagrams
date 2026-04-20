"""Warfarin S3 Exsanguination — ATK+80% + Arts damage aura 1×ATK/s to in-range enemies."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis
from core.systems import register_default_systems
from data.characters.warfarin import (
    make_warfarin,
    _S3_ATK_RATIO, _S3_BUFF_TAG, _S3_DAMAGE_RATIO, _S3_DURATION,
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


def _enemy(world: World, x: float = 1.0, y: float = 1.0, defence: int = 0, res: float = 0.0):
    from core.state.unit_state import UnitState
    from core.types import Faction
    e = UnitState(name="Enemy", faction=Faction.ENEMY, max_hp=99999, atk=0,
                  defence=defence, res=res)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


# Warfarin at (0,1): range tiles (+1,0),(+2,0),(+3,0) → world (1,1),(2,1),(3,1)
_WF_POS = (0.0, 1.0)
_ENEMY_IN = (1.0, 1.0)
_ENEMY_OUT = (4.0, 1.0)   # dx=4 — out of range


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def test_warfarin_s3_config():
    w = make_warfarin(slot="S3")
    sk = w.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.name == "Exsanguination"
    assert sk.sp_cost == 10


# ---------------------------------------------------------------------------
# ATK buff
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    """S3 applies ATK+80% on activation."""
    world = _world()
    wf = make_warfarin(slot="S3")
    wf.deployed = True; wf.position = _WF_POS; wf.atk_cd = 999.0
    wf.deploy_time = world.global_state.elapsed
    world.add_unit(wf)

    wf.skill.sp = float(wf.skill.sp_cost)
    world.tick()

    buff = next((b for b in wf.buffs if b.source_tag == _S3_BUFF_TAG), None)
    assert buff is not None, "S3 ATK buff must be applied"
    assert buff.axis == BuffAxis.ATK
    assert buff.value == _S3_ATK_RATIO


# ---------------------------------------------------------------------------
# Per-tick damage aura
# ---------------------------------------------------------------------------

def test_s3_damages_in_range_enemy():
    """S3 deals Arts damage to enemies in range each second."""
    world = _world()
    wf = make_warfarin(slot="S3")
    wf.deployed = True; wf.position = _WF_POS; wf.atk_cd = 999.0
    wf.deploy_time = world.global_state.elapsed
    enemy = _enemy(world, *_ENEMY_IN, res=0.0)
    world.add_unit(wf)

    wf.skill.sp = float(wf.skill.sp_cost)
    # 2 seconds + slack → guaranteed at least 1 pulse fires
    for _ in range(TICK_RATE * 2 + 2):
        world.tick()

    assert enemy.hp < enemy.max_hp, "In-range enemy must take damage from S3 aura"


def test_s3_damage_amount():
    """Aura damage = floor(effective_atk) × _S3_DAMAGE_RATIO (Arts, before RES)."""
    world = _world()
    wf = make_warfarin(slot="S3")
    wf.deployed = True; wf.position = _WF_POS; wf.atk_cd = 999.0
    wf.deploy_time = world.global_state.elapsed
    # Enemy with 0 RES to get raw Arts damage
    enemy = _enemy(world, *_ENEMY_IN, res=0.0)
    world.add_unit(wf)

    wf.skill.sp = float(wf.skill.sp_cost)
    world.tick()  # S3 activates (on_start called, accum=0 — on_tick not called this tick)

    # Run exactly TICK_RATE + 2 ticks → float accum ~1.2 → 1 pulse fires, not 2
    for _ in range(TICK_RATE + 2):
        world.tick()

    expected_pulse = int(wf.effective_atk * _S3_DAMAGE_RATIO)
    damage_taken = enemy.max_hp - enemy.hp
    assert damage_taken == expected_pulse, f"Expected {expected_pulse} damage, got {damage_taken}"


def test_s3_no_damage_out_of_range():
    """Enemies outside Warfarin's range do NOT take aura damage."""
    world = _world()
    wf = make_warfarin(slot="S3")
    wf.deployed = True; wf.position = _WF_POS; wf.atk_cd = 999.0
    wf.deploy_time = world.global_state.elapsed
    enemy_out = _enemy(world, *_ENEMY_OUT, res=0.0)
    world.add_unit(wf)

    wf.skill.sp = float(wf.skill.sp_cost)
    for _ in range(int(TICK_RATE * 2)):
        world.tick()

    assert enemy_out.hp == enemy_out.max_hp, "Out-of-range enemy must not take aura damage"


def test_s3_res_reduces_aura_damage():
    """Aura damage is mitigated by enemy RES."""
    world = _world()
    wf = make_warfarin(slot="S3")
    wf.deployed = True; wf.position = _WF_POS; wf.atk_cd = 999.0
    wf.deploy_time = world.global_state.elapsed
    enemy_no_res = _enemy(world, 1.0, 1.0, res=0.0)
    enemy_50res = _enemy(world, 2.0, 1.0, res=50.0)
    world.add_unit(wf)

    wf.skill.sp = float(wf.skill.sp_cost)
    for _ in range(int(TICK_RATE * 1.5)):
        world.tick()

    dmg_no_res = enemy_no_res.max_hp - enemy_no_res.hp
    dmg_50res = enemy_50res.max_hp - enemy_50res.hp
    assert dmg_50res < dmg_no_res, "50 RES enemy must take less aura damage"


# ---------------------------------------------------------------------------
# S3 expiry — buff cleared
# ---------------------------------------------------------------------------

def test_s3_buff_cleared_on_end():
    """ATK buff is removed when S3 expires."""
    world = _world()
    wf = make_warfarin(slot="S3")
    wf.deployed = True; wf.position = _WF_POS; wf.atk_cd = 999.0
    wf.deploy_time = world.global_state.elapsed
    world.add_unit(wf)

    wf.skill.sp = float(wf.skill.sp_cost)
    world.tick()

    for _ in range(int(TICK_RATE * (_S3_DURATION + 2))):
        world.tick()

    assert not any(b.source_tag == _S3_BUFF_TAG for b in wf.buffs), "ATK buff must clear on S3 end"


# ---------------------------------------------------------------------------
# Regression: S2 still works
# ---------------------------------------------------------------------------

def test_s2_regression():
    wf = make_warfarin(slot="S2")
    assert wf.skill is not None and wf.skill.slot == "S2"
    assert wf.skill.name == "Sanguinelant"
