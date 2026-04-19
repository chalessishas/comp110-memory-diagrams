"""Thorns — Thorn Prick talent (arts counter on hit) + S3 AOE attack mode."""
from __future__ import annotations
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, AttackType, Mobility
from core.systems import register_default_systems
from core.systems.talent_registry import fire_on_hit_received
from data.characters.thorns import make_thorns, _COUNTER_RATE, _TALENT_TAG
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


def _enemy(pos, hp=9999, atk=200, res=0) -> UnitState:
    """Enemy pinned at pos (move_speed=0, long path so it never reaches goal)."""
    px, py = int(pos[0]), int(pos[1])
    # Path anchors enemy at its tile; extra waypoints ensure path_progress never hits len-1
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp
    e.hp = hp
    e.atk = atk
    e.res = float(res)
    e.atk_cd = 0.0
    e.move_speed = 0.0
    e.deployed = True
    e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Talent is registered
# ---------------------------------------------------------------------------

def test_thorns_talent_registered():
    thorns = make_thorns()
    assert len(thorns.talents) == 1
    assert thorns.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: Thorn Prick deals arts counter when Thorns receives damage
# ---------------------------------------------------------------------------

def test_thorns_counter_deals_arts_damage():
    """When an enemy attacks Thorns, Thorns' talent retaliates with arts damage."""
    w = _world()
    thorns = make_thorns()
    thorns.deployed = True
    thorns.position = (0.0, 1.0)
    thorns.atk_cd = 999.0
    w.add_unit(thorns)

    attacker = _enemy(pos=(0, 1), hp=50000, atk=200, res=0)
    w.add_unit(attacker)

    hp_before = attacker.hp
    # Manually fire talent hook with non-zero damage
    fire_on_hit_received(w, thorns, attacker, 100)

    assert attacker.hp < hp_before, "Thorn Prick must deal arts damage to the attacker"


# ---------------------------------------------------------------------------
# Test 3: Counter amount = floor(180% ATK)
# ---------------------------------------------------------------------------

def test_thorns_counter_amount():
    """Counter damage = floor(COUNTER_RATE * Thorns.effective_atk), mitigated by attacker RES."""
    w = _world()
    thorns = make_thorns()
    thorns.deployed = True
    thorns.position = (0.0, 1.0)
    thorns.atk_cd = 999.0
    w.add_unit(thorns)

    attacker = _enemy(pos=(0, 1), hp=99999, atk=0, res=0)
    w.add_unit(attacker)

    fire_on_hit_received(w, thorns, attacker, 100)
    expected_raw = int(math.floor(thorns.effective_atk * _COUNTER_RATE))
    # Arts damage with 0 RES: damage = expected_raw * (1 - res/100) = expected_raw
    actual = 99999 - attacker.hp
    assert actual == expected_raw, f"Counter should be {expected_raw} but got {actual}"


# ---------------------------------------------------------------------------
# Test 4: Counter does nothing when damage=0
# ---------------------------------------------------------------------------

def test_thorns_counter_skips_zero_damage():
    """Talent does not fire when incoming damage is 0."""
    w = _world()
    thorns = make_thorns()
    thorns.deployed = True
    thorns.position = (0.0, 1.0)
    w.add_unit(thorns)

    attacker = _enemy(pos=(0, 1), hp=9999, atk=0)
    w.add_unit(attacker)

    hp_before = attacker.hp
    fire_on_hit_received(w, thorns, attacker, 0)
    assert attacker.hp == hp_before, "No counter should fire when damage=0"


# ---------------------------------------------------------------------------
# Test 5: S3 sets __targets__ (all in range) when active
# ---------------------------------------------------------------------------

def test_thorns_s3_aoe_mode_sets_targets():
    """During S3, targeting_system uses __targets__ (all in range) instead of __target__."""
    from core.systems.targeting_system import targeting_system
    w = _world()
    thorns = make_thorns()
    thorns.deployed = True
    thorns.position = (0.0, 1.0)
    thorns.atk_cd = 999.0
    w.add_unit(thorns)

    e1 = _enemy(pos=(1, 1), hp=5000)
    e2 = _enemy(pos=(2, 1), hp=5000)
    w.add_unit(e1)
    w.add_unit(e2)

    # Force S3 active
    thorns.skill.sp = thorns.skill.sp_cost
    w.tick()  # activates S3

    targeting_system(w, 0.0)
    targets = getattr(thorns, "__targets__", [])
    assert len(targets) >= 2, "S3 must populate __targets__ with all in-range enemies"
    assert getattr(thorns, "__target__", "UNSET") is None, "__target__ must be None during S3"


# ---------------------------------------------------------------------------
# Test 6: S3 AOE combat damages all in-range enemies each attack
# ---------------------------------------------------------------------------

def test_thorns_s3_combat_hits_all_enemies():
    """During S3, every attack cycle deals damage to ALL enemies in range."""
    w = _world()
    thorns = make_thorns()
    thorns.deployed = True
    thorns.position = (0.0, 1.0)
    thorns.atk_cd = 0.0
    w.add_unit(thorns)

    e1 = _enemy(pos=(1, 1), hp=50000)
    e2 = _enemy(pos=(2, 1), hp=50000)
    w.add_unit(e1)
    w.add_unit(e2)

    thorns.skill.sp = thorns.skill.sp_cost
    # Run enough ticks for S3 to activate and one attack to fire
    for _ in range(TICK_RATE * 3):
        w.tick()

    assert e1.hp < 50000, "e1 (pos 1) must take damage during S3 AOE"
    assert e2.hp < 50000, "e2 (pos 2) must take damage during S3 AOE"


# ---------------------------------------------------------------------------
# Test 7: S3 reverts to single-target after duration
# ---------------------------------------------------------------------------

def test_thorns_s3_reverts_after_duration():
    """After 30s, S3 ends and _attack_all_in_range resets to False."""
    w = _world()
    thorns = make_thorns()
    thorns.deployed = True
    thorns.position = (0.0, 1.0)
    thorns.atk_cd = 999.0
    w.add_unit(thorns)

    thorns.skill.sp = thorns.skill.sp_cost
    w.tick()  # activates S3, active_remaining = 30.0

    assert getattr(thorns, "_attack_all_in_range", False) is True, "S3 must activate AOE mode"

    for _ in range(TICK_RATE * 30 + 1):
        w.tick()

    assert getattr(thorns, "_attack_all_in_range", True) is False, (
        "After 30s, S3 must revert _attack_all_in_range to False"
    )
    assert thorns.skill.active_remaining == 0.0, "S3 duration must have expired"
