"""Nian — Talent (3 Shields), S2 Copper Seal (disarm+DEF+counter), S3 Iron Defense (ATK+ally DEF+Block).

Tests:
  - Talent: 3 shields granted on deploy
  - Talent: shields absorb damage before HP
  - S2 config (name, slot, sp_cost, initial_sp, duration, MANUAL)
  - S2 start: DEF+130% buff applied, block incremented
  - S2 disarm: operator does not attack during S2
  - S2 counter: attacker receives Arts damage when hitting Nian during S2
  - S2 counter: silence applied to attacker
  - S2 end: DEF buff removed, block restored
  - S3 config
  - S3 start: ATK+120% applied
  - S3 ally DEF: nearby ally gets DEF+80% during S3
  - S3 ally block: nearby ally block increases by 1 during S3
  - S3 end: ally buffs removed, block restored
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import (
    TileType, Faction, BuffAxis, SPGainMode, SkillTrigger, StatusKind, TICK_RATE,
)
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from core.systems.talent_registry import fire_on_deploy
from data.characters.nian import (
    make_nian,
    _TALENT_TAG, _SHIELD_TAG, _SHIELD_CHARGES, _SHIELD_PER_CHARGE,
    _S2_TAG, _S2_DEF_RATIO, _S2_DEF_BUFF_TAG, _S2_COUNTER_RATIO,
    _S3_TAG, _S3_ATK_RATIO, _S3_ATK_BUFF_TAG, _S3_ALLY_DEF_RATIO, _S3_ALLY_DEF_BUFF_TAG,
)


def _world() -> World:
    grid = TileGrid(width=8, height=5)
    for x in range(8):
        for y in range(5):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ally(world: World, x: float, y: float, block: int = 1) -> UnitState:
    a = UnitState(name="Ally", faction=Faction.ALLY, max_hp=3000, atk=400, defence=200, res=0)
    a.alive = True; a.deployed = True; a.position = (x, y)
    a.block = block
    world.add_unit(a)
    return a


def _enemy(world: World, x: float, y: float, atk: int = 300) -> UnitState:
    e = UnitState(name="Slug", faction=Faction.ENEMY, max_hp=9999, atk=atk, defence=0, res=0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


# ── Talent: Clairvoyance (3 Shields) ────────────────────────────────────────

def _deploy_nian(w: World, slot: str = "S2") -> UnitState:
    """Helper: add Nian to world and trigger on_deploy for shield."""
    op = make_nian(slot=slot)
    op.deployed = True; op.position = (0.0, 2.0); op.atk_cd = 999.0
    w.add_unit(op)
    fire_on_deploy(w, op)
    return op


def test_talent_grants_three_shields():
    w = _world()
    op = _deploy_nian(w)
    shield_statuses = [s for s in op.statuses if s.source_tag == _SHIELD_TAG]
    assert len(shield_statuses) == _SHIELD_CHARGES, f"Expected {_SHIELD_CHARGES} shield statuses"


def test_shields_absorb_before_hp():
    w = _world()
    op = _deploy_nian(w)
    original_hp = op.hp
    op.take_damage(100)  # absorbed by shield
    assert op.hp == original_hp, "Shield should absorb hit before HP"


def test_shield_depletes_absorbing_damage():
    w = _world()
    op = _deploy_nian(w)
    total_shield = sum(s.params.get("amount", 0) for s in op.statuses if s.source_tag == _SHIELD_TAG)
    assert total_shield >= _SHIELD_PER_CHARGE * _SHIELD_CHARGES


# ── S2: Copper Seal ──────────────────────────────────────────────────────────

def test_s2_config():
    op = make_nian(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Copper Seal"
    assert sk.sp_cost == 50
    assert sk.initial_sp == 35
    assert abs(sk.duration - 35.0) < 1e-6
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.behavior_tag == _S2_TAG


def test_s2_def_buff_applied():
    w = _world()
    op = make_nian(slot="S2")
    op.deployed = True; op.position = (0.0, 2.0); op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    buff = next((b for b in op.buffs if b.source_tag == _S2_DEF_BUFF_TAG), None)
    assert buff is not None and abs(buff.value - _S2_DEF_RATIO) < 1e-6


def test_s2_block_increases():
    w = _world()
    op = make_nian(slot="S2")
    op.deployed = True; op.position = (0.0, 2.0); op.atk_cd = 999.0
    original_block = op.block
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert op.block == original_block + 1


def test_s2_disarms_operator():
    """During S2, operator does not attack (atk_cd frozen high)."""
    w = _world()
    op = make_nian(slot="S2")
    op.deployed = True; op.position = (0.0, 2.0)
    _enemy(w, 1.0, 2.0)
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    # Large atk_cd set on S2 start → won't attack for a long time
    assert op.atk_cd >= 100.0, "S2 should freeze atk_cd to prevent attacking"


def test_s2_counter_arts_on_hit():
    """When Nian is hit during S2, attacker takes Arts damage."""
    w = _world()
    op = make_nian(slot="S2")
    op.deployed = True; op.position = (0.0, 2.0); op.atk_cd = 999.0
    enemy = _enemy(w, 1.0, 2.0, atk=300)
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    enemy_hp_before = enemy.hp
    op.take_damage(300)  # trigger on_hit_received via talent system
    # Note: on_hit_received fires through talent system; simulate by calling directly
    from core.systems.talent_registry import fire_on_hit_received
    fire_on_hit_received(w, op, enemy, 300)
    assert enemy.hp < enemy_hp_before, "Attacker should take Arts counter damage"


def test_s2_counter_silences_attacker():
    w = _world()
    op = make_nian(slot="S2")
    op.deployed = True; op.position = (0.0, 2.0); op.atk_cd = 999.0
    enemy = _enemy(w, 1.0, 2.0)
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    from core.systems.talent_registry import fire_on_hit_received
    fire_on_hit_received(w, op, enemy, 300)
    assert any(s.kind == StatusKind.SILENCE for s in enemy.statuses)


def test_s2_no_counter_outside_skill():
    """Counter does NOT fire when S2 is inactive."""
    w = _world()
    op = make_nian(slot="S2")
    op.deployed = True; op.position = (0.0, 2.0); op.atk_cd = 999.0
    enemy = _enemy(w, 1.0, 2.0)
    w.add_unit(op)
    enemy_hp_before = enemy.hp
    from core.systems.talent_registry import fire_on_hit_received
    fire_on_hit_received(w, op, enemy, 300)
    assert enemy.hp == enemy_hp_before, "No counter when S2 inactive"


def test_s2_buffs_cleared_on_end():
    w = _world()
    op = make_nian(slot="S2")
    op.deployed = True; op.position = (0.0, 2.0); op.atk_cd = 999.0
    w.add_unit(op)
    original_block = op.block
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (35.0 + 1.0))):
        w.tick()
    assert not any(b.source_tag == _S2_DEF_BUFF_TAG for b in op.buffs)
    assert op.block == original_block


# ── S3: Iron Defense ─────────────────────────────────────────────────────────

def test_s3_config():
    op = make_nian(slot="S3")
    sk = op.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.name == "Iron Defense"
    assert sk.sp_cost == 85
    assert sk.initial_sp == 70
    assert abs(sk.duration - 45.0) < 1e-6
    assert sk.trigger == SkillTrigger.MANUAL


def test_s3_atk_buff_applied():
    w = _world()
    op = make_nian(slot="S3")
    op.deployed = True; op.position = (0.0, 2.0); op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    buff = next((b for b in op.buffs if b.source_tag == _S3_ATK_BUFF_TAG), None)
    assert buff is not None and abs(buff.value - _S3_ATK_RATIO) < 1e-6


def test_s3_ally_def_buff_applied():
    """Nearby ally receives DEF+80% during S3."""
    w = _world()
    op = make_nian(slot="S3")
    op.deployed = True; op.position = (0.0, 2.0); op.atk_cd = 999.0
    ally = _ally(w, 1.0, 2.0)
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    buff = next((b for b in ally.buffs if b.source_tag == _S3_ALLY_DEF_BUFF_TAG), None)
    assert buff is not None and abs(buff.value - _S3_ALLY_DEF_RATIO) < 1e-6


def test_s3_ally_block_incremented():
    """Nearby ally block increases by 1 during S3."""
    w = _world()
    op = make_nian(slot="S3")
    op.deployed = True; op.position = (0.0, 2.0); op.atk_cd = 999.0
    ally = _ally(w, 1.0, 2.0, block=2)
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert ally.block == 3, "Ally block should be 2+1=3 during S3"


def test_s3_out_of_range_ally_not_buffed():
    """Ally outside S3 range does not receive DEF buff."""
    w = _world()
    op = make_nian(slot="S3")
    op.deployed = True; op.position = (0.0, 2.0); op.atk_cd = 999.0
    ally_far = _ally(w, 5.0, 2.0)  # distance 5 > range 2
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert not any(b.source_tag == _S3_ALLY_DEF_BUFF_TAG for b in ally_far.buffs)


def test_s3_buffs_cleared_on_end():
    """All S3 buffs (own ATK + ally DEF + ally block) removed on S3 end."""
    w = _world()
    op = make_nian(slot="S3")
    op.deployed = True; op.position = (0.0, 2.0); op.atk_cd = 999.0
    ally = _ally(w, 1.0, 2.0, block=2)
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (45.0 + 1.0))):
        w.tick()
    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in op.buffs)
    assert not any(b.source_tag == _S3_ALLY_DEF_BUFF_TAG for b in ally.buffs)
    assert ally.block == 2, "Ally block should be restored after S3"
