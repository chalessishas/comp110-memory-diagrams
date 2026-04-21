"""Amiya S1 "Tactical Chant γ", S2 "Spirit Burst", S3 "Chimera".

Tests cover:
  - S1 config (MANUAL, sp_cost=35, initial_sp=5, duration=30)
  - S1 ASPD+80 buff applied on start, cleared on end
  - S2 config (AUTO, sp_cost=100, initial_sp=0, duration=25)
  - S2 ATK buff applied (+290% ratio = 3.9× total)
  - S2 self-Stun 10s applied after skill ends
  - S2 ATK buff cleared before self-stun
  - S3 config (MANUAL, sp_cost=120, initial_sp=0, duration=30)
  - S3 ATK+240% buff applied
  - S3 Max HP doubled, current HP scales up
  - S3 attack type changes to TRUE
  - S3 range expands
  - S3 auto-retreat when skill ends
  - S3 HP restored after auto-retreat
  - Talent: kill restores 8 SP (when skill inactive)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, AttackType, StatusKind, SkillTrigger, SPGainMode
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from core.systems.talent_registry import fire_on_kill
from data.characters.amiya import (
    make_amiya,
    CASTER_RANGE, CHIMERA_RANGE,
    _S1_TAG, _S1_ASPD_BONUS, _S1_ASPD_BUFF_TAG, _S1_DURATION,
    _S2_TAG, _S2_ATK_RATIO, _S2_ATK_BUFF_TAG, _S2_STUN_TAG, _S2_STUN_DURATION, _S2_DURATION,
    _S3_TAG, _S3_ATK_RATIO, _S3_ATK_BUFF_TAG, _S3_HP_MULTIPLIER, _S3_DURATION,
    _TALENT_SP_ON_KILL,
)


def _world() -> World:
    grid = TileGrid(width=8, height=3)
    for x in range(8):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _enemy(world: World, x: float = 3.0, y: float = 1.0, hp: int = 9999) -> UnitState:
    e = UnitState(name="Slug", faction=Faction.ENEMY, max_hp=hp, atk=0, defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


# ── S1: Tactical Chant γ ─────────────────────────────────────────────────────

def test_s1_config():
    op = make_amiya(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Tactical Chant γ"
    assert sk.sp_cost == 35
    assert sk.initial_sp == 5
    assert abs(sk.duration - _S1_DURATION) < 1e-6
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.requires_target is False
    assert sk.behavior_tag == _S1_TAG


def test_s1_aspd_buff_applied():
    w = _world()
    op = make_amiya(slot="S1")
    base_interval = op.current_atk_interval
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    buff = next((b for b in op.buffs if b.source_tag == _S1_ASPD_BUFF_TAG), None)
    assert buff is not None
    assert abs(buff.value - _S1_ASPD_BONUS) < 1e-6
    # ASPD+80 shortens attack interval: new_interval = base / (180/100)
    expected = base_interval / ((100.0 + _S1_ASPD_BONUS) / 100.0)
    assert abs(op.current_atk_interval - expected) < 0.01


def test_s1_aspd_buff_cleared_on_end():
    w = _world()
    op = make_amiya(slot="S1")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    base_interval = op.current_atk_interval
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    for _ in range(int(TICK_RATE * (_S1_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S1_ASPD_BUFF_TAG for b in op.buffs)
    assert abs(op.current_atk_interval - base_interval) < 0.01


# ── S2: Spirit Burst ──────────────────────────────────────────────────────────

def test_s2_config():
    op = make_amiya(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Spirit Burst"
    assert sk.sp_cost == 100
    assert sk.initial_sp == 0
    assert abs(sk.duration - _S2_DURATION) < 1e-6
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.requires_target is False
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff_applied():
    w = _world()
    op = make_amiya(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    w.tick()  # AUTO trigger fires when SP is full

    buff = next((b for b in op.buffs if b.source_tag == _S2_ATK_BUFF_TAG), None)
    assert buff is not None
    assert abs(buff.value - _S2_ATK_RATIO) < 1e-6
    expected = int(op.atk * (1 + _S2_ATK_RATIO))
    assert op.effective_atk == expected


def test_s2_self_stun_after_skill():
    w = _world()
    op = make_amiya(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    w.tick()  # fire S2

    # Advance past skill duration
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert any(s.kind == StatusKind.STUN and s.source_tag == _S2_STUN_TAG
               for s in op.statuses)


def test_s2_atk_buff_cleared_before_stun():
    w = _world()
    op = make_amiya(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S2_ATK_BUFF_TAG for b in op.buffs)
    assert any(s.kind == StatusKind.STUN for s in op.statuses)


def test_s2_stun_expires():
    """Self-stun eventually clears after 10s."""
    w = _world()
    op = make_amiya(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    # Skip past skill + stun duration
    for _ in range(int(TICK_RATE * (_S2_DURATION + _S2_STUN_DURATION + 2.0))):
        w.tick()

    stun_statuses = [s for s in op.statuses if s.kind == StatusKind.STUN]
    assert len(stun_statuses) == 0


# ── S3: Chimera ───────────────────────────────────────────────────────────────

def test_s3_config():
    op = make_amiya(slot="S3")
    sk = op.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.name == "Chimera"
    assert sk.sp_cost == 120
    assert sk.initial_sp == 0
    assert abs(sk.duration - _S3_DURATION) < 1e-6
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.behavior_tag == _S3_TAG


def test_s3_atk_buff_applied():
    w = _world()
    op = make_amiya(slot="S3")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    buff = next((b for b in op.buffs if b.source_tag == _S3_ATK_BUFF_TAG), None)
    assert buff is not None
    assert abs(buff.value - _S3_ATK_RATIO) < 1e-6
    expected = int(op.atk * (1 + _S3_ATK_RATIO))
    assert op.effective_atk == expected


def test_s3_hp_doubled():
    w = _world()
    op = make_amiya(slot="S3")
    base_max_hp = op.max_hp  # 1680
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert op.max_hp == base_max_hp * _S3_HP_MULTIPLIER
    assert op.hp <= op.max_hp
    assert op.hp >= base_max_hp  # current hp increases by the gained amount


def test_s3_true_damage():
    w = _world()
    op = make_amiya(slot="S3")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert op.attack_type == AttackType.TRUE


def test_s3_range_expands():
    w = _world()
    op = make_amiya(slot="S3")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    assert op.range_shape == CASTER_RANGE

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert op.range_shape == CHIMERA_RANGE
    assert len(op.range_shape.tiles) > len(CASTER_RANGE.tiles)


def test_s3_auto_retreat():
    """Amiya is automatically retreated when S3 ends."""
    w = _world()
    op = make_amiya(slot="S3")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    w.global_state.dp = 20  # enough DP so retreat refund works
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    for _ in range(int(TICK_RATE * (_S3_DURATION + 1.0))):
        w.tick()

    assert not op.deployed


def test_s3_hp_restored_after_retreat():
    """Max HP returns to base value after S3 ends (retreat)."""
    w = _world()
    op = make_amiya(slot="S3")
    base_max_hp = op.max_hp
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    w.global_state.dp = 20
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert op.max_hp == base_max_hp * _S3_HP_MULTIPLIER

    for _ in range(int(TICK_RATE * (_S3_DURATION + 1.0))):
        w.tick()

    assert op.max_hp == base_max_hp
    assert op.hp <= base_max_hp


def test_s3_attack_type_restored_after_retreat():
    w = _world()
    op = make_amiya(slot="S3")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    w.global_state.dp = 20
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert op.attack_type == AttackType.TRUE

    for _ in range(int(TICK_RATE * (_S3_DURATION + 1.0))):
        w.tick()

    assert op.attack_type == AttackType.ARTS


# ── Talent: Sarkaz King ───────────────────────────────────────────────────────

def test_talent_sp_on_kill():
    w = _world()
    op = make_amiya(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    dead_enemy = _enemy(w, hp=1)
    dead_enemy.alive = False

    sp_before = op.skill.sp + 10.0  # arbitrary SP below max
    op.skill.sp = sp_before

    fire_on_kill(w, op, dead_enemy)

    assert op.skill.sp == min(float(op.skill.sp_cost), sp_before + _TALENT_SP_ON_KILL)


def test_talent_no_sp_during_active_skill():
    """Talent does NOT refund SP while S2 is active."""
    w = _world()
    op = make_amiya(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    dead_enemy = _enemy(w, hp=1)
    dead_enemy.alive = False

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()  # start S2
    assert op.skill.active_remaining > 0

    sp_during_skill = op.skill.sp
    fire_on_kill(w, op, dead_enemy)

    assert op.skill.sp == sp_during_skill  # no change during active skill
