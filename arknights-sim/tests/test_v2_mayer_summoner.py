"""Mayer — SUP_SUMMONER: spawns mech-otter tokens that fight alongside her.

Talent "Mechanical Mechanic": On deploy, summon 1 mech-otter token.
S2 "EMP Pattern": ATK +40% self, spawn 1 additional mech-otter token.

Tests cover:
  - Archetype SUP_SUMMONER
  - Token spawned on deploy (talent on_battle_start)
  - Token is an ally at Mayer's position
  - Token has correct stats (HP, ATK, DEF)
  - S2 spawns additional token (2 tokens total)
  - S2 applies ATK +40% to Mayer
  - S2 ATK buff removed on end
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, RoleArchetype
from core.systems import register_default_systems
from data.characters.mayer import (
    make_mayer,
    _TALENT_TAG, _S2_ATK_RATIO, _S2_ATK_BUFF_TAG, _S2_DURATION,
    _TOKEN_NAME, _TOKEN_HP, _TOKEN_ATK,
    _MAYER_TOKENS_ATTR,
)
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


def _slug(pos=(2, 1), hp=99999) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = 0; e.move_speed = 0.0; e.res = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Archetype SUP_SUMMONER
# ---------------------------------------------------------------------------

def test_mayer_archetype():
    m = make_mayer()
    assert m.archetype == RoleArchetype.SUP_SUMMONER
    assert m.block == 1
    assert len(m.talents) == 1
    assert m.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: Token spawned on deploy
# ---------------------------------------------------------------------------

def test_talent_spawns_token_on_deploy():
    """Talent must spawn 1 mech-otter token when Mayer is deployed."""
    w = _world()
    m = make_mayer()
    m.deployed = True; m.position = (0.0, 1.0)

    allies_before = len(w.allies())
    w.add_unit(m)  # triggers on_battle_start

    allies_after = len(w.allies())
    assert allies_after == allies_before + 2, (  # Mayer + 1 token
        f"Must have Mayer + 1 token; allies={allies_after}"
    )


# ---------------------------------------------------------------------------
# Test 3: Token is an ally at Mayer's position
# ---------------------------------------------------------------------------

def test_token_is_ally_at_mayer_position():
    """Token must be an ally with correct name at Mayer's tile."""
    w = _world()
    m = make_mayer()
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    tokens = [u for u in w.allies() if u.name == _TOKEN_NAME]
    assert len(tokens) == 1, f"Must have exactly 1 token; found {len(tokens)}"
    assert tokens[0].position == m.position, "Token must be at Mayer's position"


# ---------------------------------------------------------------------------
# Test 4: Token has correct stats
# ---------------------------------------------------------------------------

def test_token_stats():
    """Mech-otter token must have HP=1550, ATK=970."""
    w = _world()
    m = make_mayer()
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    tokens = [u for u in w.allies() if u.name == _TOKEN_NAME]
    assert len(tokens) == 1
    assert tokens[0].max_hp == _TOKEN_HP, f"Token HP must be {_TOKEN_HP}; got {tokens[0].max_hp}"
    assert tokens[0].atk == _TOKEN_ATK, f"Token ATK must be {_TOKEN_ATK}; got {tokens[0].atk}"


# ---------------------------------------------------------------------------
# Test 5: S2 spawns additional token
# ---------------------------------------------------------------------------

def test_s2_spawns_additional_token():
    """S2 must spawn an additional otter token (2 total)."""
    w = _world()
    m = make_mayer()
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)  # 1 token from talent

    tokens_before = [u for u in w.allies() if u.name == _TOKEN_NAME]
    assert len(tokens_before) == 1, "Must have 1 token after deploy"

    m.skill.sp = float(m.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, m)

    tokens_after = [u for u in w.allies() if u.name == _TOKEN_NAME]
    assert len(tokens_after) == 2, (
        f"S2 must spawn 1 more token (total=2); got {len(tokens_after)}"
    )


# ---------------------------------------------------------------------------
# Test 6: S2 applies ATK +40% to Mayer
# ---------------------------------------------------------------------------

def test_s2_atk_buff():
    """S2 EMP Pattern must apply ATK +40% to Mayer."""
    w = _world()
    m = make_mayer()
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    base_atk = m.effective_atk
    m.skill.sp = float(m.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, m)

    assert m.skill.active_remaining > 0.0, "S2 must be active"
    expected_atk = int(base_atk * (1 + _S2_ATK_RATIO))
    assert abs(m.effective_atk - expected_atk) <= 2, (
        f"S2 ATK must be ×{1+_S2_ATK_RATIO}; expected={expected_atk}, got={m.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 7: S2 ATK buff removed on end
# ---------------------------------------------------------------------------

def test_s2_buff_removed_on_end():
    """After S2 ends, ATK must return to base."""
    w = _world()
    m = make_mayer()
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    m.skill.sp = float(m.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, m)

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert m.skill.active_remaining == 0.0, "S2 must have ended"
    s2_buffs = [buf for buf in m.buffs if buf.source_tag == _S2_ATK_BUFF_TAG]
    assert len(s2_buffs) == 0, "S2 ATK buff must be cleared after skill ends"


# ---------------------------------------------------------------------------
# Test 8: on_death cascade — Mayer dies → tokens despawn
# ---------------------------------------------------------------------------

def test_tokens_despawn_when_mayer_dies():
    """When Mayer is killed, all her mech-otter tokens must also be despawned."""
    w = _world()
    m = make_mayer(slot=None)   # no skill, just talent
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    # Mayer now has 1 token (from on_battle_start)
    tokens = [u for u in w.units if u.name == _TOKEN_NAME]
    assert len(tokens) == 1, "Mayer must have spawned 1 token on deploy"
    token = tokens[0]

    # Kill Mayer via direct HP manipulation → forces take_damage path
    damage_needed = m.max_hp + 1000
    m.take_damage(damage_needed)

    assert not m.alive, "Mayer must be dead"

    # Run one tick so cleanup_system dispatches on_death
    w.tick()

    assert not token.alive or not token.deployed, (
        f"Token must despawn when Mayer dies; alive={token.alive}, deployed={token.deployed}"
    )


# ---------------------------------------------------------------------------
# Test 9: on_death cascade does not affect enemies or unrelated allies
# ---------------------------------------------------------------------------

def test_death_cascade_only_affects_mayer_tokens():
    """When Mayer dies, unrelated allied units must NOT be affected."""
    from data.characters.liskarm import make_liskarm

    w = _world()
    m = make_mayer(slot=None)
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    lisk = make_liskarm()
    lisk.deployed = True; lisk.position = (2.0, 1.0)
    w.add_unit(lisk)

    lisk_hp_before = lisk.hp

    m.take_damage(m.max_hp + 1000)
    w.tick()

    assert not m.alive, "Mayer must be dead"
    assert lisk.alive, "Liskarm must NOT be affected by Mayer's death cascade"
    assert lisk.hp == lisk_hp_before, "Liskarm HP must be unchanged"


# ---------------------------------------------------------------------------
# Test 10: on_death fires exactly once (no double-cascade on repeated ticks)
# ---------------------------------------------------------------------------

def test_death_cascade_fires_once():
    """Tokens despawned on tick 1 must stay despawned after many subsequent ticks."""
    w = _world()
    m = make_mayer(slot=None)
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    token = next(u for u in w.units if u.name == _TOKEN_NAME)

    m.take_damage(m.max_hp + 1000)
    for _ in range(TICK_RATE * 3):   # 3 seconds of ticks
        w.tick()

    assert not token.alive or not token.deployed, "Token must remain despawned"
    # _just_died must not linger
    assert not getattr(m, "_just_died", False), "_just_died flag must be cleared after one tick"


# ---------------------------------------------------------------------------
# Test 11: on_retreat cascade — Mayer retreats → tokens despawn
# ---------------------------------------------------------------------------

def test_tokens_despawn_when_mayer_retreats():
    """When Mayer is retreated, all mech-otter tokens must be despawned."""
    w = _world()
    m = make_mayer(slot=None)   # no skill, just talent
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    tokens = [u for u in w.units if u.name == _TOKEN_NAME]
    assert len(tokens) == 1, "Mayer must have spawned 1 token on deploy"
    token = tokens[0]
    assert token.alive, "Token must be alive before retreat"

    # Retreat Mayer — on_retreat fires synchronously
    w.retreat(m)

    assert not m.deployed, "Mayer must no longer be deployed"
    assert not token.alive or not token.deployed, (
        f"Token must despawn when Mayer retreats; alive={token.alive}, deployed={token.deployed}"
    )
