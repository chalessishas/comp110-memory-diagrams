"""Status decay + per-tick status effects (DOT, REGEN)."""
from __future__ import annotations
from ..types import StatusKind


def status_decay_system(world, dt: float) -> None:
    now = world.global_state.elapsed
    for u in world.units:
        if not u.alive:
            continue
        # DOT: apply true damage each tick before expiry check
        for s in u.statuses:
            if s.kind == StatusKind.DOT and s.expires_at + 1e-9 >= now:
                dps = s.params.get("dps", 0.0)
                if dps > 0 and u.alive:
                    u.take_damage(max(1, int(dps * dt)))
        # REGEN: heal each tick before expiry check
        for s in u.statuses:
            if s.kind == StatusKind.REGEN and s.expires_at + 1e-9 >= now:
                hps = s.params.get("hps", 0.0)
                if hps > 0 and u.alive:
                    u.heal(max(1, int(hps * dt)))
        # keep while expires_at + epsilon >= now — guards floating-point accumulation
        # (e.g. 20 × 0.1 = 2.0000000000000004, not 2.0)
        u.statuses = [s for s in u.statuses if s.expires_at + 1e-9 >= now]
        u.buffs = [b for b in u.buffs if b.expires_at + 1e-9 >= now]
