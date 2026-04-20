"""Mudrock (泥岩) — 6★ Defender (DEF_ARTS_PROTECTOR).

Trait: Deals Arts damage; when Blocking, reduces damage taken by 35% (DEF × 1.35, RES + 10).
  Note: generated base uses PHYSICAL; game-canonical arts mechanic simplified here as
  high-DEF physical blocker (trait bonus modelled via talent when blocking).

Talent "Rocksteady" (磐石之固):
  While HP > 50%, gain +_TALENT_DEF_BONUS flat DEF.
  Applied as a persistent buff; removed when HP drops to/below threshold.

S3 "Surge of Rocks" (骤石): 15s duration, sp_cost=30, AUTO_TIME, AUTO trigger
  Grants +100% ATK ratio buff on activation.
  Schedules _STRIKE_COUNT=5 physical AoE strikes via EventQueue, each _STRIKE_INTERVAL apart.
  Each strike:
    - Deals physical damage (effective_atk, boosted by S3 buff) to all enemies within radius
    - Generates _STRIKE_DP_PER_HIT DP on hit
  Buff removed on S3 end; pending strikes still fire if S3 expires early.

Base stats from ArknightsGameData (E2 max, trust 100, char_311_mudrok):
  HP=4428, ATK=882, DEF=662, RES=10, atk_interval=1.6, block=3.
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
from data.characters.generated.mudrok import make_mudrok as _base_stats


MELEE_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_TALENT_TAG = "mudrock_rocksteady"
_TALENT_DEF_BONUS = 300          # flat DEF when HP > threshold
_TALENT_DEF_BUFF_TAG = "mudrock_rocksteady_def"
_HP_THRESHOLD = 0.50             # must be strictly above 50%

_S3_TAG = "mudrock_s3_surge_of_rocks"
_S3_ATK_RATIO = 1.0              # +100% ATK (doubles effective_atk)
_S3_ATK_BUFF_TAG = "mudrock_s3_atk"
_S3_DURATION = 15.0
_STRIKE_COUNT = 5
_STRIKE_INTERVAL = 0.4           # seconds between each of the 5 hits
_STRIKE_AOE_RADIUS = 1.5         # tiles — covers adjacent + diagonal
_STRIKE_DP_PER_HIT = 2           # DP generated per strike (when at least one enemy hit)


# ---------------------------------------------------------------------------
# Talent: Rocksteady — conditional DEF buff
# ---------------------------------------------------------------------------

def _talent_on_tick(world, carrier: UnitState, dt: float) -> None:
    hp_pct = carrier.hp / carrier.max_hp if carrier.max_hp > 0 else 0.0
    existing = next((b for b in carrier.buffs if b.source_tag == _TALENT_DEF_BUFF_TAG), None)
    if hp_pct > _HP_THRESHOLD:
        if existing is None:
            carrier.buffs.append(Buff(
                axis=BuffAxis.DEF, stack=BuffStack.FLAT,
                value=_TALENT_DEF_BONUS, source_tag=_TALENT_DEF_BUFF_TAG,
                expires_at=float("inf"),
            ))
    else:
        carrier.buffs = [b for b in carrier.buffs if b.source_tag != _TALENT_DEF_BUFF_TAG]


# ---------------------------------------------------------------------------
# S3: Surge of Rocks — EventQueue multi-hit
# ---------------------------------------------------------------------------

def _rock_strike_handler_factory(carrier: UnitState):
    """Returns an EventQueue handler bound to this Mudrock instance."""
    def _handler(world, event) -> None:
        if not carrier.alive or not carrier.deployed:
            return
        if carrier.position is None:
            return
        cx, cy = carrier.position
        raw = carrier.effective_atk   # uses S3 ATK buff if still active
        hit_any = False
        for e in world.enemies():
            if not e.alive or e.position is None:
                continue
            ex, ey = e.position
            if (ex - cx) ** 2 + (ey - cy) ** 2 <= _STRIKE_AOE_RADIUS ** 2:
                dmg = e.take_physical(raw)
                world.global_state.total_damage_dealt += dmg
                hit_any = True
                world.log(
                    f"Mudrock S3 rock strike → {e.name}  "
                    f"dmg={dmg}  ({e.hp}/{e.max_hp})"
                )
        if hit_any:
            world.global_state.dp = min(
                world.global_state.dp + _STRIKE_DP_PER_HIT,
                world.global_state.dp_cap,
            )
    return _handler


def _mudrock_on_battle_start(world, carrier: UnitState) -> None:
    kind = f"mudrock_rock_strike_{carrier.unit_id}"
    world.event_queue.register(kind, _rock_strike_handler_factory(carrier))


register_talent(_TALENT_TAG, on_battle_start=_mudrock_on_battle_start, on_tick=_talent_on_tick)


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))
    kind = f"mudrock_rock_strike_{carrier.unit_id}"
    world.event_queue.schedule_repeating(
        first_at=world.global_state.elapsed + _STRIKE_INTERVAL,
        interval=_STRIKE_INTERVAL,
        count=_STRIKE_COUNT,
        kind=kind,
    )
    world.log(
        f"Mudrock S3: Surge of Rocks — "
        f"{_STRIKE_COUNT} strikes over {_STRIKE_COUNT * _STRIKE_INTERVAL:.1f}s scheduled"
    )


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_ATK_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def make_mudrock(slot: str = "S3") -> UnitState:
    """Mudrock E2 max. Rocksteady DEF buff + S3 5-hit AoE EventQueue burst."""
    op = _base_stats()
    op.name = "Mudrock"
    op.archetype = RoleArchetype.DEF_ARTS_PROTECTOR
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = True
    op.range_shape = MELEE_RANGE
    op.block = 3
    op.cost = 36

    op.talents = [TalentComponent(name="Rocksteady", behavior_tag=_TALENT_TAG)]

    if slot == "S3":
        op.skill = SkillComponent(
            name="Surge of Rocks",
            slot="S3",
            sp_cost=30,
            initial_sp=15,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
