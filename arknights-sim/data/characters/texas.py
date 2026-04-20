"""Texas (德克萨斯) — 5* Vanguard (Pioneer archetype).

Base stats from ArknightsGameData (E2 max, trust 100, char_102_texas).
  HP=1950, ATK=570, DEF=343, RES=0, atk_interval=1.05s, cost=13, block=2.

Talent "Tactical Delivery" (E2): grants +2 DP at operation start.
  (Pioneer trait: Block 2. NOT DP-on-kill; that is the Charger subclass.)

S2 "Sword Rain": Instant AoE (actually single-target burst).
  ATK +200%, immediately deals 2 physical hits to current target.
  Restores 3 DP on activation.
  sp_cost=18, initial_sp=9, AUTO_ATTACK (charges per attack), AUTO trigger.

S3 "Texas Rhapsody": Instant MANUAL.
  Deals 350% ATK Arts to all enemies in range. Stuns them for 2s. +3 DP.
  sp_cost=30, initial_sp=15, AUTO_ATTACK.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from math import floor
from core.state.unit_state import StatusEffect
from core.types import (
    AttackType, Faction, Profession, RoleArchetype,
    BuffAxis, BuffStack, SPGainMode, SkillTrigger, StatusKind,
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


# --- S3: Texas Rhapsody — instant Arts AoE + 2s STUN + 3 DP ---
_S3_TAG = "texas_s3_rhapsody"
_S3_ATK_MULTIPLIER = 3.50      # 350% ATK arts burst
_S3_STUN_DURATION = 2.0
_S3_DP_GAIN = 3


def _s3_on_start(world, carrier: UnitState) -> None:
    if carrier.position is None:
        return
    ox, oy = carrier.position
    tiles = set(carrier.range_shape.tiles)
    raw = int(floor(carrier.effective_atk * _S3_ATK_MULTIPLIER))
    now = world.global_state.elapsed
    stun_tag = f"{_S3_TAG}_stun"
    for enemy in world.enemies():
        if not enemy.alive or not enemy.deployed or enemy.position is None:
            continue
        dx = round(enemy.position[0]) - round(ox)
        dy = round(enemy.position[1]) - round(oy)
        if (dx, dy) not in tiles:
            continue
        dealt = enemy.take_arts(raw)
        world.global_state.total_damage_dealt += dealt
        enemy.statuses.append(StatusEffect(
            kind=StatusKind.STUN,
            source_tag=stun_tag,
            expires_at=now + _S3_STUN_DURATION,
        ))
    world.global_state.refund_dp(_S3_DP_GAIN)
    world.log(f"Texas S3 Rhapsody — {_S3_ATK_MULTIPLIER:.0%} ATK arts AoE, {_S3_STUN_DURATION}s stun, +{_S3_DP_GAIN} DP")


register_skill(_S3_TAG, on_start=_s3_on_start)


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
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Texas Rhapsody",
            slot="S3",
            sp_cost=30,
            initial_sp=15,
            duration=0.0,           # instant
            sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.MANUAL,
            requires_target=True,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
