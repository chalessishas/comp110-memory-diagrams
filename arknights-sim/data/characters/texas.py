"""Texas (德克萨斯) — 5* Vanguard (Pioneer archetype).

Base stats from ArknightsGameData (E2 max, trust 100, char_102_texas).
  HP=1950, ATK=570, DEF=343, RES=0, atk_interval=1.05s, cost=13, block=2.

Talent "Tactical Delivery" (E2): grants +2 DP at operation start.
  (Pioneer trait: Block 2. NOT DP-on-kill; that is the Charger subclass.)

S2 "Sword Rain": Instant AoE (actually single-target burst).
  ATK +200%, immediately deals 2 physical hits to current target.
  Restores 3 DP on activation.
  sp_cost=18, initial_sp=9, AUTO_ATTACK (charges per attack), AUTO trigger.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, Faction, Profession, RoleArchetype,
    BuffAxis, BuffStack, SPGainMode, SkillTrigger,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.texas import make_texas as _base_stats


PIONEER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_TACTICAL_DELIVERY_TAG = "texas_tactical_delivery"

# --- S2: Sword Rain ---
_S2_TAG = "texas_s2_sword_rain"
_S2_ATK_RATIO = 2.00        # ATK ×200% extra (total 3× base during burst)
_S2_HIT_COUNT = 2           # 2 immediate physical hits
_S2_DP_GAIN = 3             # +3 DP on activation
_S2_BUFF_TAG = "texas_s2_atk_buff"


def _on_battle_start(world, unit) -> None:
    world.global_state.refund_dp(2)  # E2 rank: +2 DP at operation start


register_talent(_TACTICAL_DELIVERY_TAG, on_battle_start=_on_battle_start)


def _s2_on_start(world, carrier: UnitState) -> None:
    # Apply ATK buff, do burst hits, then immediately remove buff (instant skill: on_end never fires)
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    world.global_state.refund_dp(_S2_DP_GAIN)
    target = getattr(carrier, "__target__", None)
    if target is not None and target.alive:
        atk = carrier.effective_atk
        for _ in range(_S2_HIT_COUNT):
            if not target.alive:
                break
            dealt = target.take_physical(atk)
            world.global_state.total_damage_dealt += dealt
    world.log(
        f"Texas S2 Sword Rain → +{_S2_DP_GAIN} DP, {_S2_HIT_COUNT}× "
        f"{carrier.effective_atk} phys on {target.name if target else 'no target'}"
    )
    # Remove buff inline — instant skills never trigger on_end
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start)


def make_texas(slot: str = "S2") -> UnitState:
    """Texas E2 max. Tactical Delivery: +2 DP at start. S2: +200% ATK burst + 2 hits + 3 DP."""
    op = _base_stats()
    op.name = "Texas"
    op.archetype = RoleArchetype.VAN_PIONEER
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = PIONEER_RANGE
    op.block = 2
    op.cost = 13
    op.talents = [TalentComponent(
        name="Tactical Delivery",
        behavior_tag=_TACTICAL_DELIVERY_TAG,
    )]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Sword Rain",
            slot="S2",
            sp_cost=18,
            initial_sp=9,
            duration=0.0,           # instant
            sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
