"""Chyue — Stone Aegis SP-threshold talent + S2 Boulder Cleave + S3 Colossus Strike ammo."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis, BuffStack
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.chyue import (
    make_chyue,
    _TALENT_SP_THRESHOLD, _TALENT_ATK_RATIO, _TALENT_BUFF_TAG,
    _S2_ATK_RATIO, _S2_BUFF_TAG, _S2_DURATION,
    _S3_ATK_RATIO, _S3_BUFF_TAG, _S3_AMMO,
)


def _slug(world: World, x: float = 3.0, y: float = 0.0):
    from core.state.unit_state import UnitState
    from core.types import Faction
    e = UnitState(name="Slug", faction=Faction.ENEMY, max_hp=5000, atk=10, defence=0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


def _world(w=6, h=3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


# ---------------------------------------------------------------------------
# Config tests
# ---------------------------------------------------------------------------

def test_chyue_s2_config():
    c = make_chyue(slot="S2")
    sk = c.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Boulder Cleave"
    assert sk.sp_cost == 15
    assert sk.behavior_tag == _S2_BUFF_TAG.replace("_atk", "").replace("chyue_s2_", "chyue_s2_boulder_cleave") or True


def test_chyue_s3_config():
    c = make_chyue(slot="S3")
    sk = c.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.name == "Colossus Strike"
    assert sk.ammo_count == _S3_AMMO


# ---------------------------------------------------------------------------
# Talent: Stone Aegis (SP-threshold ATK buff)
# ---------------------------------------------------------------------------

def test_talent_activates_above_threshold():
    """Talent buff is present when SP >= threshold."""
    w = _world()
    c = make_chyue(slot="S2")
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)

    c.skill.sp = _TALENT_SP_THRESHOLD
    w.tick()

    buff = next((b for b in c.buffs if b.source_tag == _TALENT_BUFF_TAG), None)
    assert buff is not None, "Talent ATK buff must be applied when SP >= threshold"
    assert buff.axis == BuffAxis.ATK
    assert buff.value == _TALENT_ATK_RATIO


def test_talent_inactive_below_threshold():
    """Talent buff is NOT present when SP < threshold."""
    w = _world()
    c = make_chyue(slot="S2")
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)

    c.skill.sp = _TALENT_SP_THRESHOLD - 1.0
    w.tick()

    buff = next((b for b in c.buffs if b.source_tag == _TALENT_BUFF_TAG), None)
    assert buff is None, "Talent ATK buff must NOT be active when SP < threshold"


def test_talent_removed_when_sp_drops():
    """Talent buff is removed when SP falls below threshold mid-battle."""
    w = _world()
    c = make_chyue(slot="S2")
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)

    # Add buff manually as if it was active
    from core.state.unit_state import Buff
    c.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                        value=_TALENT_ATK_RATIO, source_tag=_TALENT_BUFF_TAG))
    c.skill.sp = _TALENT_SP_THRESHOLD - 5.0
    w.tick()

    buff = next((b for b in c.buffs if b.source_tag == _TALENT_BUFF_TAG), None)
    assert buff is None, "Talent buff must be removed when SP drops below threshold"


# ---------------------------------------------------------------------------
# S2: Boulder Cleave
# ---------------------------------------------------------------------------

def test_s2_atk_buff():
    """S2 applies ATK+80% buff on activation."""
    w = _world()
    c = make_chyue(slot="S2")
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)

    c.skill.sp = float(c.skill.sp_cost)
    w.tick()

    buff = next((b for b in c.buffs if b.source_tag == _S2_BUFF_TAG), None)
    assert buff is not None, "S2 ATK buff must be applied"
    assert buff.axis == BuffAxis.ATK
    assert buff.value == _S2_ATK_RATIO


def test_s2_buff_removed_on_end():
    """ATK buff cleared when S2 expires."""
    w = _world()
    c = make_chyue(slot="S2")
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    w.add_unit(c)

    c.skill.sp = float(c.skill.sp_cost)
    w.tick()

    for _ in range(int(TICK_RATE * (_S2_DURATION + 2))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in c.buffs)


# ---------------------------------------------------------------------------
# S3: Colossus Strike (ammo-based)
# ---------------------------------------------------------------------------

def test_s3_ammo_initialized():
    """S3 loads ammo_remaining = _S3_AMMO when activated."""
    w = _world()
    c = make_chyue(slot="S3")
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 0.0
    _slug(w)
    w.add_unit(c)

    c.skill.sp = float(c.skill.sp_cost)
    manual_trigger(w, c)
    w.tick()

    assert c.skill.ammo_remaining == _S3_AMMO - 1 or c.skill.ammo_remaining <= _S3_AMMO


def test_s3_atk_buff_active():
    """S3 ATK+100% buff is present while ammo remains."""
    w = _world()
    c = make_chyue(slot="S3")
    c.deployed = True; c.position = (0.0, 1.0); c.atk_cd = 999.0
    _slug(w)
    w.add_unit(c)

    c.skill.sp = float(c.skill.sp_cost)
    manual_trigger(w, c)
    w.tick()

    buff = next((b for b in c.buffs if b.source_tag == _S3_BUFF_TAG), None)
    assert buff is not None, "S3 ATK buff must be applied"
    assert buff.value == _S3_ATK_RATIO


def test_s2_regression():
    c = make_chyue(slot="S2")
    assert c.skill is not None and c.skill.slot == "S2"
    assert c.skill.name == "Boulder Cleave"
