"""SilverAsh — 6* Guard (Lord archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
Skill behaviour hand-authored here; regenerate base via:
  python tools/gen_characters.py char_172_svrash
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape, TalentComponent,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.silverash import make_silverash as _base_stats


# Guard 分支「领主」标准远程 2-格范围：前一格 + 前后邻居（十字形）
# 实际 in-game 范围图更复杂；此处先用能覆盖 "attack tile in front" 的最小集
GUARD_LORD_RANGE = RangeShape(tiles=(
    (0, 0),          # 本格（melee block）
    (1, 0),          # 前一格（lord 的远程特性）
))


# --- Talent: Silver Sword ---
# Global aura: all deployed melee operators (excl. SilverAsh himself) gain +20% ATK.
_TALENT_TAG = "silverash_silver_sword"
_TALENT_ATK_RATIO = 0.20
_TALENT_BUFF_TAG = "silverash_silver_sword_atk"
_TALENT_BUFF_TTL = 0.3   # seconds; re-stamped each tick to keep buff live


def _talent_on_tick(world, carrier: UnitState, dt: float) -> None:
    now = world.global_state.elapsed
    new_expires = now + _TALENT_BUFF_TTL + dt
    for ally in world.allies():
        if ally is carrier or not ally.alive or not ally.deployed:
            continue
        if not ally.attack_range_melee:
            # remove stale buff if ally switched to ranged (edge case)
            ally.buffs = [b for b in ally.buffs if b.source_tag != _TALENT_BUFF_TAG]
            continue
        existing = next((b for b in ally.buffs if b.source_tag == _TALENT_BUFF_TAG), None)
        if existing is not None:
            existing.expires_at = new_expires
        else:
            ally.buffs.append(Buff(
                axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                value=_TALENT_ATK_RATIO, source_tag=_TALENT_BUFF_TAG,
                expires_at=new_expires,
            ))


def _talent_on_death(world, carrier: UnitState) -> None:
    for ally in world.allies():
        ally.buffs = [b for b in ally.buffs if b.source_tag != _TALENT_BUFF_TAG]


def _talent_on_retreat(world, carrier: UnitState) -> None:
    _talent_on_death(world, carrier)


register_talent(
    _TALENT_TAG,
    on_tick=_talent_on_tick,
    on_death=_talent_on_death,
    on_retreat=_talent_on_retreat,
)


# --- S3 Truesilver Slash behavior ---
_S3_TAG = "silverash_s3_truesilver_slash"
_S3_ATK_RATIO = 1.80   # +180% at rank III
_S3_BUFF_TAG = "silverash_s3_atk_buff"
_STRIKE_COUNT = 3
_STRIKE_INTERVAL = 0.15   # seconds between each of the 3 strikes (~game animation timing)


def _make_strike_handler(carrier: UnitState):
    """Returns an EventQueue handler that sweeps all enemies in carrier's range."""
    def _handler(world, event) -> None:
        if not carrier.alive or not carrier.deployed:
            return
        if carrier.position is None:
            return
        ox, oy = carrier.position
        tiles = set(carrier.range_shape.tiles) | set(carrier.range_shape.extended_tiles)
        strike_num = event.payload.get("strike_num", "?")
        for e in world.enemies():
            if not e.alive or e.position is None:
                continue
            if (round(e.position[0]) - round(ox), round(e.position[1]) - round(oy)) in tiles:
                dmg = e.take_physical(carrier.effective_atk)
                world.global_state.total_damage_dealt += dmg
                world.log(
                    f"SilverAsh S3 strike {strike_num}/{_STRIKE_COUNT} → {e.name}  "
                    f"dmg={dmg}  ({e.hp}/{e.max_hp})"
                )
    return _handler


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))

    strike_kind = f"silverash_s3_strike_{carrier.unit_id}"
    if strike_kind not in world.event_queue._handlers:
        world.event_queue.register(strike_kind, _make_strike_handler(carrier))

    now = world.global_state.elapsed
    for i in range(_STRIKE_COUNT):
        world.event_queue.schedule(
            now + i * _STRIKE_INTERVAL,
            strike_kind,
            strike_num=i + 1,
        )


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_silverash(slot: str = "S3") -> UnitState:
    """SilverAsh E2 max, trust 100. Talent: Silver Sword (+20% ATK to all deployed melee operators). S3 skill."""
    op = _base_stats()
    op.name = "SilverAsh"
    op.archetype = RoleArchetype.GUARD_LORD
    op.range_shape = GUARD_LORD_RANGE
    op.cost = 31
    op.talents = [TalentComponent(name="Silver Sword", behavior_tag=_TALENT_TAG)]
    if slot == "S3":
        op.skill = SkillComponent(
            name="Truesilver Slash",
            slot="S3",
            sp_cost=20,
            duration=15.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            behavior_tag=_S3_TAG,
        )
    return op
