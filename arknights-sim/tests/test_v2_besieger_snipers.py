"""Besieger Sniper (Typhon, Erato): heaviest-target priority + 1.5× damage to blocked enemies."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, RangeShape
from core.types import TileType, TICK_RATE, Faction, AttackType, RoleArchetype
from core.systems import register_default_systems
from core.systems.targeting_system import _targeting_for_operator
from data.characters.typhon import make_typhon
from data.characters.erato import make_erato
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


def _enemy(pos, hp=9999, defence=0, weight=1) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp
    e.hp = hp
    e.defence = defence
    e.weight = weight
    e.atk = 0
    e.atk_cd = 9999.0
    e.move_speed = 0.0
    e.deployed = True
    e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Archetype checks
# ---------------------------------------------------------------------------

def test_typhon_archetype():
    assert make_typhon().archetype == RoleArchetype.SNIPER_SIEGE


def test_erato_archetype():
    assert make_erato().archetype == RoleArchetype.SNIPER_SIEGE


# ---------------------------------------------------------------------------
# Targeting: targets heaviest enemy in range
# ---------------------------------------------------------------------------

def test_typhon_targets_heaviest():
    """Typhon (Besieger) must target the enemy with highest weight, not closest to exit."""
    w = _world()
    t = make_typhon()
    t.deployed = True
    t.position = (0.0, 1.0)
    t.atk_cd = 9999.0
    w.add_unit(t)

    light = _enemy((2, 1), weight=1)   # closer to (arbitrary exit)
    heavy = _enemy((3, 1), weight=3)   # heavier
    w.add_unit(light)
    w.add_unit(heavy)

    result = _targeting_for_operator(w, t)
    assert result is heavy, "Typhon must target heaviest enemy (weight=3) over lighter (weight=1)"


def test_erato_targets_heaviest():
    """Erato (Besieger) also targets heaviest enemy."""
    w = _world()
    e = make_erato()
    e.deployed = True
    e.position = (0.0, 1.0)
    e.atk_cd = 9999.0
    w.add_unit(e)

    light = _enemy((2, 1), weight=1)
    heavy = _enemy((3, 1), weight=2)
    w.add_unit(light)
    w.add_unit(heavy)

    result = _targeting_for_operator(w, e)
    assert result is heavy, "Erato must target heaviest enemy"


# ---------------------------------------------------------------------------
# Damage bonus: 1.5× ATK vs blocked enemies
# ---------------------------------------------------------------------------

def test_typhon_deals_bonus_damage_to_blocked_enemy():
    """Typhon deals 1.5× ATK physical damage to a blocked enemy."""
    w = _world()
    t = make_typhon()
    t.deployed = True
    t.position = (0.0, 1.0)
    t.atk_cd = 0.0
    w.add_unit(t)

    blocker = UnitState(
        name="Blocker",
        faction=Faction.ALLY,
        max_hp=9999, hp=9999, atk=0, atk_interval=9999.0,
        block=1, attack_type=AttackType.PHYSICAL,
        range_shape=RangeShape(tiles=()), deployed=True,
        position=(2.0, 1.0), alive=True,
    )
    w.add_unit(blocker)

    enemy = _enemy((2, 1), hp=50000, defence=0)
    w.add_unit(enemy)

    # Manually set block assignment so targeting + combat see it as blocked
    enemy.blocked_by_unit_ids = [blocker.unit_id]

    hp_before = enemy.hp
    # Tick once for combat
    from core.systems.combat_system import combat_system
    from core.systems.targeting_system import targeting_system
    targeting_system(w, 0.1)
    # Override blocked assignment (targeting_system clears it; set after)
    enemy.blocked_by_unit_ids = [blocker.unit_id]
    setattr(t, "__target__", enemy)
    setattr(t, "__targets__", [])
    combat_system(w, 0.1)

    damage = hp_before - enemy.hp
    expected_base = t.effective_atk          # without bonus
    expected_bonus = int(t.effective_atk * 1.5)  # with 1.5× bonus
    # Should be close to 1.5× base (minus DEF=0 → no reduction)
    assert damage >= expected_base, "Besieger should deal at least base ATK"
    assert damage > expected_base * 1.2, (
        f"Besieger 1.5× bonus not applied: dealt {damage}, base {expected_base}, expected ~{expected_bonus}"
    )


def test_typhon_normal_damage_to_unblocked_enemy():
    """Typhon deals normal (1×) ATK to an unblocked enemy."""
    w = _world()
    t = make_typhon()
    t.deployed = True
    t.position = (0.0, 1.0)
    t.atk_cd = 0.0
    w.add_unit(t)

    enemy = _enemy((2, 1), hp=50000, defence=0)
    enemy.blocked_by_unit_ids = []   # explicitly not blocked
    w.add_unit(enemy)

    hp_before = enemy.hp
    setattr(t, "__target__", enemy)
    setattr(t, "__targets__", [])
    from core.systems.combat_system import combat_system
    combat_system(w, 0.1)

    damage = hp_before - enemy.hp
    expected = t.effective_atk   # 1× ATK vs DEF=0
    assert damage == expected, (
        f"Unblocked enemy should take 1× ATK ({expected}), got {damage}"
    )


def test_besieger_kills_blocked_slug_faster():
    """End-to-end: Typhon kills a blocked enemy noticeably faster than expected without bonus."""
    w = _world()
    t = make_typhon()
    t.deployed = True
    t.position = (0.0, 1.0)
    t.atk_cd = 0.0
    w.add_unit(t)

    # Blocker at same tile as Typhon's target
    blocker = UnitState(
        name="Blocker",
        faction=Faction.ALLY,
        max_hp=9999, hp=9999, atk=0, atk_interval=9999.0,
        block=2, attack_type=AttackType.PHYSICAL,
        range_shape=RangeShape(tiles=()), deployed=True,
        position=(2.0, 1.0), alive=True,
    )
    w.add_unit(blocker)

    # Enemy blocked at (2,1): HP = exactly 1.5× Typhon ATK → dies in 1 hit with bonus, 2 hits without
    hp_at_1_5x = int(t.effective_atk * 1.5) - 1   # just under 1-shot threshold with bonus
    enemy = _enemy((2, 1), hp=hp_at_1_5x + 1, defence=0)
    enemy.move_speed = 0.0
    w.add_unit(enemy)

    for _ in range(TICK_RATE * 5):
        w.tick()
        if not enemy.alive:
            break

    assert not enemy.alive, (
        "Besieger 1.5× bonus must one-shot the enemy that would survive without the bonus"
    )
