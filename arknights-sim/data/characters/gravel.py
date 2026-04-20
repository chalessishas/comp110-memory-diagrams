"""砾 (Gravel) — 4* Specialist (SPEC_AMBUSHER, fast-redeploy archetype).

Fast Redeploy trait: redeploy cooldown is 18s (vs 70s normal).
  Cost 8 DP, block=1 — disposable frontline anchor.

Talent "Tactical Concealment" (E2):
  For the first 10s after each deployment, takes 80% reduced damage (damage_taken × 0.20).
  Activated via on_deploy hook (fires on every world.deploy() call, including re-deploys).
  An EventQueue event at deploy_time + 10s marks the shield inactive.
  on_battle_start is kept to handle the pattern where a unit is added pre-deployed.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, TalentComponent, RangeShape
from core.types import RoleArchetype
from core.systems.talent_registry import register_talent
from data.characters.generated.gravel import make_gravel as _base_stats


_TALENT_TAG = "gravel_tactical_concealment"
_TALENT_REDUCE = 0.80           # 80% damage reduction while shield is active
_TALENT_DURATION = 10.0         # seconds after each deploy
_TALENT_EXPIRE_PREFIX = "gravel_shield_expire_"

AMBUSHER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))


def _find_talent(carrier: UnitState) -> TalentComponent | None:
    for t in carrier.talents:
        if t.behavior_tag == _TALENT_TAG:
            return t
    return None


def _activate_shield(world, carrier: UnitState) -> None:
    """Activate deploy shield and schedule its expiry. Called on every deploy."""
    t = _find_talent(carrier)
    if t is None:
        return
    t.params["deploy_shield"] = {"active": True, "reduction": _TALENT_REDUCE}

    expire_kind = f"{_TALENT_EXPIRE_PREFIX}{carrier.unit_id}"
    if expire_kind not in world.event_queue._handlers:
        def _on_expire(w, ev) -> None:
            c = w.unit_by_id(ev.payload["carrier_id"])
            if c is None:
                return
            talent = _find_talent(c)
            if talent is not None:
                talent.params["deploy_shield"] = {"active": False, "reduction": 0.0}
        world.event_queue.register(expire_kind, _on_expire)

    now = world.global_state.elapsed
    world.event_queue.schedule(
        now + _TALENT_DURATION,
        expire_kind,
        carrier_id=carrier.unit_id,
    )


def _talent_on_battle_start(world, carrier: UnitState) -> None:
    """Initial add to world — if already deployed (test setup), activate shield."""
    if carrier.deployed:
        _activate_shield(world, carrier)


def _talent_on_deploy(world, carrier: UnitState) -> None:
    """Every world.deploy() call — activate/refresh the shield."""
    _activate_shield(world, carrier)


register_talent(
    _TALENT_TAG,
    on_battle_start=_talent_on_battle_start,
    on_deploy=_talent_on_deploy,
)


def make_gravel() -> UnitState:
    """砾 E2 max. SPEC_AMBUSHER: 18s redeploy, 80% dmg reduction for 10s on each deploy."""
    op = _base_stats()
    op.name = "Gravel"
    op.archetype = RoleArchetype.SPEC_AMBUSHER
    op.range_shape = AMBUSHER_RANGE
    op.block = 1
    op.cost = 8
    op.redeploy_cd = 18.0
    op.talents = [
        TalentComponent(
            name="Tactical Concealment",
            behavior_tag=_TALENT_TAG,
            params={},
        )
    ]
    return op
