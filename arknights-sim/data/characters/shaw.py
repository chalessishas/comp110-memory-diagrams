"""Shaw (萧) — 4* Specialist (Pusher archetype).

Pusher trait: Attacks push the target backward 1 tile along their path.
  Implemented via push_distance=1 + _apply_push in combat_system.

Talent "Gale" (E1): push_distance becomes 2 (auto-applied at E2 level here).

S2 "Powerful Current" (M3): Instant ranged burst — deals 280% ATK Arts damage to
  all enemies in a line, each pushed back 3 tiles.
  sp_cost=15, initial_sp=5, AUTO_ATTACK.

Base stats: E2 max, trust 100 (hand-authored from wiki).
  HP=1857, ATK=499, DEF=271, RES=0, atk_interval=1.2s, cost=11, block=1.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape, TalentComponent
from core.types import (
    AttackType, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.combat_system import _apply_push
from core.systems.talent_registry import register_talent


# --- Talent: Gale — push distance 1 → 2 at E2 ---
_TALENT_TAG = "shaw_gale"
_BASE_PUSH = 1
_GALE_PUSH = 2


def _gale_on_battle_start(world, carrier: UnitState) -> None:
    carrier.push_distance = _GALE_PUSH
    world.log(f"Shaw Gale — push_distance → {_GALE_PUSH}")


register_talent(_TALENT_TAG, on_battle_start=_gale_on_battle_start)


PUSHER_RANGE = RangeShape(tiles=((0, 0), (1, 0), (2, 0)))   # melee + 2 tiles forward
PUSHER_RANGE_EXTENDED = RangeShape(tiles=((0, 0), (1, 0), (2, 0), (3, 0)))

_S2_TAG = "shaw_s2_powerful_current"
_S2_ATK_MULT = 2.80   # 280% ATK
_S2_PUSH_DIST = 3     # S2 pushes 3 tiles


def _s2_on_start(world, unit: UnitState) -> None:
    if unit.position is None:
        return
    ox, oy = unit.position
    tiles = set(PUSHER_RANGE_EXTENDED.tiles)
    burst_atk = int(unit.effective_atk * _S2_ATK_MULT)
    for enemy in list(world.enemies()):
        if not enemy.alive or enemy.position is None:
            continue
        dx = round(enemy.position[0]) - round(ox)
        dy = round(enemy.position[1]) - round(oy)
        if (dx, dy) not in tiles:
            continue
        # Arts damage (Pusher S2 is Arts in game)
        dealt = enemy.take_arts(burst_atk)
        world.global_state.total_damage_dealt += dealt
        world.log(f"Shaw S2 → {enemy.name}  dmg={dealt}  ({enemy.hp}/{enemy.max_hp})")
        if enemy.alive:
            _apply_push(enemy, _S2_PUSH_DIST)
            world.log(f"Shaw S2 pushes {enemy.name} back {_S2_PUSH_DIST} tiles")


register_skill(_S2_TAG, on_start=_s2_on_start)


def make_shaw(slot: str = "S2") -> UnitState:
    """Shaw E2 max. Pusher trait: push 2 tiles per attack. S2: AoE Arts burst + 3-tile push."""
    op = UnitState(
        name="Shaw",
        faction=Faction.ALLY,
        max_hp=1857,
        atk=499,
        defence=271,
        res=0.0,
        atk_interval=1.2,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=11,
        redeploy_cd=70.0,
    )
    op.archetype = RoleArchetype.SPEC_PUSHER
    op.range_shape = PUSHER_RANGE
    op.push_distance = _BASE_PUSH   # base 1; Gale talent raises to 2 on deploy
    op.talents = [TalentComponent(name="Gale", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Powerful Current",
            slot="S2",
            sp_cost=15,
            initial_sp=5,
            duration=0.0,         # instant
            sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    return op
