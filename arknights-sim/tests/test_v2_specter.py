"""Specter — Undying Will talent + S2 Pather's Light (ATK+160%, 5% lifesteal)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, StatusKind
from core.systems import register_default_systems
from data.characters.specter import make_specter, _S2_ATK_RATIO, _UNDYING_DURATION, _HP_RECOVER_RATIO
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


def _slug(pos=(2, 1), hp=99999, atk=0):
    path = [(int(pos[0]), int(pos[1]))] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = atk; e.move_speed = 0.0
    e.deployed = True; e.position = (float(pos[0]), float(pos[1]))
    return e


# ---------------------------------------------------------------------------
# Test 1: Undying Will talent is registered
# ---------------------------------------------------------------------------

def test_specter_talent_registered():
    s = make_specter()
    assert len(s.talents) == 1
    assert s.talents[0].name == "Undying Will"


# ---------------------------------------------------------------------------
# Test 2: undying_charges = 1 after battle start
# ---------------------------------------------------------------------------

def test_undying_charges_set_on_battle_start():
    """Talent on_battle_start sets undying_charges = 1."""
    w = _world()
    specter = make_specter()
    specter.deployed = True; specter.position = (0.0, 1.0); specter.atk_cd = 999.0
    w.add_unit(specter)
    # Before any tick, charges may be 0 (before on_battle_start fires)
    w.tick()
    assert specter.undying_charges == 1, (
        f"undying_charges must be 1 after battle start; got {specter.undying_charges}"
    )


# ---------------------------------------------------------------------------
# Test 3: Lethal hit triggers Undying Will (survives at 1 HP)
# ---------------------------------------------------------------------------

def test_undying_survives_lethal_hit():
    """When Specter would die, she survives at 1 HP and undying_charges decrements."""
    w = _world()
    specter = make_specter()
    specter.deployed = True; specter.position = (0.0, 1.0); specter.atk_cd = 999.0
    w.add_unit(specter)
    w.tick()  # on_battle_start fires, charges = 1

    # Force lethal damage
    specter.take_damage(specter.max_hp * 10)

    assert specter.alive, "Specter must still be alive after undying triggers"
    assert specter.hp == 1, f"HP must be exactly 1 after undying; got {specter.hp}"
    assert specter.undying_charges == 0, "undying_charges must be 0 after use"


# ---------------------------------------------------------------------------
# Test 4: Undying immune window — DAMAGE_IMMUNE applied after trigger
# ---------------------------------------------------------------------------

def test_undying_immune_phase():
    """After undying triggers, Specter gets DAMAGE_IMMUNE for 10s."""
    w = _world()
    specter = make_specter()
    specter.deployed = True; specter.position = (0.0, 1.0); specter.atk_cd = 999.0
    w.add_unit(specter)
    w.tick()  # on_battle_start

    specter.take_damage(specter.max_hp * 10)  # trigger undying

    w.tick()  # on_tick fires — applies DAMAGE_IMMUNE

    assert specter.has_status(StatusKind.DAMAGE_IMMUNE), (
        "Specter must have DAMAGE_IMMUNE during undying window"
    )
    # Damage during immune window should be 0
    hp_before = specter.hp
    specter.take_damage(9999)
    assert specter.hp == hp_before, "DAMAGE_IMMUNE must block all damage"


# ---------------------------------------------------------------------------
# Test 5: DEF buff during undying window
# ---------------------------------------------------------------------------

def test_undying_def_buff():
    """Undying Will also applies DEF +200% during the immune window."""
    from core.types import BuffAxis
    w = _world()
    specter = make_specter()
    specter.deployed = True; specter.position = (0.0, 1.0); specter.atk_cd = 999.0
    w.add_unit(specter)
    w.tick()

    base_def = specter.effective_def
    specter.take_damage(specter.max_hp * 10)
    w.tick()  # immune window starts

    expected_def = int(specter.defence * (1.0 + 2.00))
    assert specter.effective_def == expected_def, (
        f"DEF must be +200% during undying; expected {expected_def}, got {specter.effective_def}"
    )


# ---------------------------------------------------------------------------
# Test 6: HP recovery after immune window ends
# ---------------------------------------------------------------------------

def test_undying_hp_recovery():
    """After 10s immune window, Specter recovers to 40% max HP."""
    w = _world()
    specter = make_specter()
    specter.deployed = True; specter.position = (0.0, 1.0); specter.atk_cd = 999.0
    w.add_unit(specter)
    w.tick()

    specter.take_damage(specter.max_hp * 10)  # trigger at hp=1

    # Advance through the immune window (10s = TICK_RATE * 10 ticks)
    for _ in range(TICK_RATE * int(_UNDYING_DURATION) + 2):
        w.tick()

    expected_min_hp = int(specter.max_hp * _HP_RECOVER_RATIO)
    assert specter.hp >= expected_min_hp, (
        f"After undying window, HP must be >= {expected_min_hp}; got {specter.hp}"
    )
    assert not specter.has_status(StatusKind.DAMAGE_IMMUNE), (
        "DAMAGE_IMMUNE must expire after undying window"
    )


# ---------------------------------------------------------------------------
# Test 7: Second lethal hit kills (only one charge per deployment)
# ---------------------------------------------------------------------------

def test_undying_only_once():
    """Undying Will has one charge — second lethal hit kills Specter."""
    w = _world()
    specter = make_specter()
    specter.deployed = True; specter.position = (0.0, 1.0); specter.atk_cd = 999.0
    w.add_unit(specter)
    w.tick()

    specter.take_damage(specter.max_hp * 10)  # first lethal — survives
    assert specter.alive

    # Burn through immune window so DAMAGE_IMMUNE expires
    for _ in range(TICK_RATE * int(_UNDYING_DURATION) + 2):
        w.tick()

    specter.take_damage(specter.max_hp * 10)  # second lethal — dies
    assert not specter.alive, "Second lethal must kill Specter (no charges left)"


# ---------------------------------------------------------------------------
# Test 8: S2 ATK buff activates
# ---------------------------------------------------------------------------

def test_specter_s2_atk_buff():
    """S2 Pather's Light applies +160% ATK to Specter."""
    w = _world()
    specter = make_specter(slot="S2")
    specter.deployed = True; specter.position = (0.0, 1.0); specter.atk_cd = 999.0
    w.add_unit(specter)
    slug = _slug((1, 1))
    w.add_unit(slug)

    atk_base = specter.effective_atk
    specter.skill.sp = specter.skill.sp_cost
    w.tick()

    expected = int(atk_base * (1.0 + _S2_ATK_RATIO))
    assert specter.effective_atk == expected, (
        f"S2 must give ATK {expected}; got {specter.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 9: S2 lifesteal heals Specter on attack
# ---------------------------------------------------------------------------

def test_specter_s2_lifesteal():
    """S2 Pather's Light: 5% of damage dealt heals Specter."""
    w = _world()
    specter = make_specter(slot="S2")
    specter.deployed = True; specter.position = (0.0, 1.0); specter.atk_cd = 0.0
    w.add_unit(specter)
    slug = _slug((1, 1), hp=99999)
    w.add_unit(slug)

    # Injure Specter so heals are visible
    specter.hp = specter.max_hp // 2

    specter.skill.sp = specter.skill.sp_cost
    for _ in range(20):  # S2 fires on tick 1 (SKILL after COMBAT); first post-S2 attack at ~tick 13
        w.tick()

    assert specter.hp > specter.max_hp // 2, (
        "S2 lifesteal must restore HP above the damaged starting value"
    )
