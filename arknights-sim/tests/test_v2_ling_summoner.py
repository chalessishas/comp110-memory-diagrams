"""Ling — SUP_SUMMONER: summons Long Xian dragon ally via S3.

SUP_SUMMONER trait:
  - Can summon additional ally units (Long Xian dragons) to fight
  - archetype = SUP_SUMMONER

Talent "Dragon's Blood":
  - While a Long Xian is deployed, allies within Ling's range get +_TALENT_ATK_BONUS flat ATK
  - Aura disappears when Long Xian dies or is recalled

S3 "Draconic Inspiration": 30s duration
  - Spawns a Long Xian dragon (faction=ALLY) at Ling's position
  - Long Xian fights autonomously (physical, melee, block=2)
  - On S3 end, Long Xian is recalled (alive=False)

Tests cover:
  - Archetype is SUP_SUMMONER, attack_type=ARTS
  - Ling's ARTS attacks damage enemies
  - S3 spawns a new ally unit (Long Xian) in the world
  - Long Xian has faction=ALLY and correct stats
  - Long Xian attacks enemies (damages them over time)
  - Talent aura buffs in-range allies while Long Xian is present
  - Long Xian is recalled (not alive) after S3 ends
  - No aura buff after Long Xian is recalled
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, RangeShape
from core.types import (
    TileType, TICK_RATE, DT, Faction, AttackType, RoleArchetype,
)
from core.systems import register_default_systems
from data.characters.ling import (
    make_ling, _make_long_xian,
    _TALENT_ATK_BONUS, _S3_DURATION, _TALENT_BUFF_TAG,
)
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=8, height=5)
    for x in range(8):
        for y in range(5):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _slug(pos=(3, 2), hp=99999) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = 0; e.res = 0.0
    e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


def _ally(pos=(1, 2)) -> UnitState:
    return UnitState(
        name="Ally",
        faction=Faction.ALLY,
        max_hp=2000, hp=2000, atk=400,
        defence=0, res=0.0,
        atk_interval=999.0, block=1,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=False,
        range_shape=RangeShape(tiles=()),
        deployed=True, position=(float(pos[0]), float(pos[1])),
    )


# ---------------------------------------------------------------------------
# Test 1: Archetype
# ---------------------------------------------------------------------------

def test_ling_archetype():
    l = make_ling()
    assert l.archetype == RoleArchetype.SUP_SUMMONER
    assert l.attack_type == AttackType.ARTS


# ---------------------------------------------------------------------------
# Test 2: ARTS attacks damage enemies
# ---------------------------------------------------------------------------

def test_ling_arts_attacks():
    """Ling deals ARTS damage to enemies."""
    w = _world()
    l = make_ling()
    l.deployed = True; l.position = (0.0, 2.0); l.atk_cd = 0.0
    w.add_unit(l)

    e = _slug(pos=(2, 2))
    w.add_unit(e)

    for _ in range(3):
        w.tick()

    assert e.hp < 99999, f"Ling must deal ARTS damage; hp={e.hp}"


# ---------------------------------------------------------------------------
# Test 3: S3 spawns Long Xian as a new ally
# ---------------------------------------------------------------------------

def test_s3_spawns_long_xian():
    """S3 activation must add a new ally unit (Long Xian) to the world."""
    w = _world()
    l = make_ling()
    l.deployed = True; l.position = (0.0, 2.0)
    w.add_unit(l)

    e = _slug(pos=(4, 2))
    w.add_unit(e)

    allies_before = len(w.allies())

    l.skill.sp = float(l.skill.sp_cost)
    w.tick()  # S3 activates

    assert l.skill.active_remaining > 0.0, "S3 must be active"
    allies_after = len(w.allies())
    assert allies_after > allies_before, (
        f"S3 must spawn a Long Xian; allies before={allies_before}, after={allies_after}"
    )


# ---------------------------------------------------------------------------
# Test 4: Long Xian has correct faction and is deployed
# ---------------------------------------------------------------------------

def test_long_xian_is_ally():
    """Spawned Long Xian must be faction=ALLY and deployed."""
    w = _world()
    l = make_ling()
    l.deployed = True; l.position = (0.0, 2.0)
    w.add_unit(l)

    e = _slug(pos=(4, 2))
    w.add_unit(e)

    l.skill.sp = float(l.skill.sp_cost)
    w.tick()

    assert l.skill.active_remaining > 0.0
    summon_id = l._ling_summon_id
    assert summon_id is not None
    dragon = w.unit_by_id(summon_id)
    assert dragon is not None and dragon.alive, "Long Xian must be alive"
    assert dragon.faction == Faction.ALLY, "Long Xian must be faction=ALLY"
    assert dragon.deployed is True


# ---------------------------------------------------------------------------
# Test 5: Long Xian attacks enemies
# ---------------------------------------------------------------------------

def test_long_xian_attacks_enemies():
    """Long Xian dragon deals physical damage to nearby enemies."""
    w = _world()
    l = make_ling()
    l.deployed = True; l.position = (0.0, 2.0)
    w.add_unit(l)

    # Enemy close to where dragon will be spawned
    e = _slug(pos=(1, 2), hp=99999)
    w.add_unit(e)

    l.skill.sp = float(l.skill.sp_cost)
    w.tick()  # S3 activates, dragon spawns

    assert l.skill.active_remaining > 0.0
    hp_after_spawn = e.hp

    # Let the dragon attack
    for _ in range(int(TICK_RATE * 3)):
        w.tick()

    assert e.hp < hp_after_spawn, (
        f"Long Xian must attack and damage enemies; hp at spawn={hp_after_spawn}, now={e.hp}"
    )


# ---------------------------------------------------------------------------
# Test 6: Talent aura buffs in-range allies while dragon lives
# ---------------------------------------------------------------------------

def test_talent_aura_while_dragon_alive():
    """In-range allies get ATK buff from Dragon's Blood while Long Xian is present."""
    w = _world()
    l = make_ling()
    l.deployed = True; l.position = (0.0, 2.0); l.atk_cd = 999.0
    w.add_unit(l)

    ally = _ally(pos=(1, 2))
    base_atk = ally.effective_atk
    w.add_unit(ally)

    e = _slug(pos=(4, 2))
    w.add_unit(e)

    l.skill.sp = float(l.skill.sp_cost)
    w.tick()  # S3 activates, dragon spawns

    assert l.skill.active_remaining > 0.0
    w.tick()  # aura tick

    dragon_buffs = [b for b in ally.buffs if b.source_tag == _TALENT_BUFF_TAG]
    assert len(dragon_buffs) == 1, (
        f"Ally must have Dragon's Blood aura buff; buffs={dragon_buffs}"
    )
    assert ally.effective_atk > base_atk, (
        f"Ally ATK must be buffed; base={base_atk}, now={ally.effective_atk}"
    )
    expected = base_atk + _TALENT_ATK_BONUS
    assert abs(ally.effective_atk - expected) <= 2


# ---------------------------------------------------------------------------
# Test 7: Long Xian recalled when S3 ends
# ---------------------------------------------------------------------------

def test_long_xian_recalled_on_s3_end():
    """When S3 ends, Long Xian must be recalled (alive=False)."""
    w = _world()
    l = make_ling()
    l.deployed = True; l.position = (0.0, 2.0)
    w.add_unit(l)

    e = _slug(pos=(4, 2))
    w.add_unit(e)

    l.skill.sp = float(l.skill.sp_cost)
    w.tick()
    assert l.skill.active_remaining > 0.0

    dragon_id = l._ling_summon_id

    # Run until S3 expires
    for _ in range(int(TICK_RATE * (_S3_DURATION + 1))):
        w.tick()

    assert l.skill.active_remaining == 0.0, "S3 must have ended"
    dragon = w.unit_by_id(dragon_id)
    assert dragon is not None
    assert not dragon.alive, "Long Xian must be recalled (alive=False) after S3 ends"


# ---------------------------------------------------------------------------
# Test 8: No aura after dragon is recalled
# ---------------------------------------------------------------------------

def test_no_aura_after_recall():
    """After Long Xian is recalled, the Dragon's Blood aura must be removed."""
    w = _world()
    l = make_ling()
    l.deployed = True; l.position = (0.0, 2.0); l.atk_cd = 999.0
    w.add_unit(l)

    ally = _ally(pos=(1, 2))
    w.add_unit(ally)

    e = _slug(pos=(4, 2))
    w.add_unit(e)

    l.skill.sp = float(l.skill.sp_cost)
    w.tick()
    assert l.skill.active_remaining > 0.0
    w.tick()  # aura should be applied

    assert any(b.source_tag == _TALENT_BUFF_TAG for b in ally.buffs), \
        "Aura must be active while dragon lives"

    # Run until S3 ends + 2 ticks for cleanup
    for _ in range(int(TICK_RATE * (_S3_DURATION + 1)) + 2):
        w.tick()

    assert l.skill.active_remaining == 0.0

    aura_buffs = [b for b in ally.buffs if b.source_tag == _TALENT_BUFF_TAG]
    assert len(aura_buffs) == 0, (
        f"Dragon's Blood aura must be gone after recall; buffs={aura_buffs}"
    )
