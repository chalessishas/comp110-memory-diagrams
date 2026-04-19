"""Combat — 攻击冷却倒数 + 命中目标 + 伤害结算."""
from __future__ import annotations
from ..types import AttackType, Faction
from ..state.unit_state import SPGainMode
from .talent_registry import fire_on_attack_hit, fire_on_hit_received


def combat_system(world, dt: float) -> None:
    for u in world.units:
        if not u.alive or not u.deployed:
            continue
        if not u.can_act():
            u.atk_cd = max(0.0, u.atk_cd - dt)
            continue

        u.atk_cd = max(0.0, u.atk_cd - dt)
        if u.atk_cd > 0.0:
            continue

        target = getattr(u, "__target__", None)
        if target is None or not target.alive:
            continue

        # Damage / heal
        raw = u.effective_atk
        if u.attack_type == AttackType.PHYSICAL:
            dealt = target.take_physical(raw)
        elif u.attack_type == AttackType.ARTS:
            dealt = target.take_arts(raw)
        elif u.attack_type == AttackType.HEAL:
            dealt = target.heal(raw)
            world.global_state.total_healing_done += dealt
        else:
            dealt = target.take_true(raw)

        if u.attack_type != AttackType.HEAL:
            world.global_state.total_damage_dealt += dealt

        world.log(
            f"{u.name} → {target.name}  "
            f"{'heal' if u.attack_type == AttackType.HEAL else 'dmg'}={dealt}  "
            f"({target.hp}/{target.max_hp})"
        )

        # AOE splash
        if u.splash_radius > 0.0 and u.attack_type != AttackType.HEAL:
            if target.position is not None:
                tx, ty = target.position
                splash_faction = Faction.ENEMY if u.faction == Faction.ALLY else Faction.ALLY
                for other in world.units:
                    if other is target or not other.alive or other.faction != splash_faction:
                        continue
                    if other.position is None:
                        continue
                    ox, oy = other.position
                    if (ox - tx) ** 2 + (oy - ty) ** 2 <= u.splash_radius ** 2:
                        if u.attack_type == AttackType.PHYSICAL:
                            s = other.take_physical(raw)
                        elif u.attack_type == AttackType.ARTS:
                            s = other.take_arts(raw)
                        else:
                            s = other.take_true(raw)
                        world.global_state.total_damage_dealt += s

        u.atk_cd = u.current_atk_interval

        # SP on attack
        if u.skill is not None:
            if u.skill.sp_gain_mode == SPGainMode.AUTO_ATTACK and not u.skill.active_remaining > 0:
                u.skill.sp = min(u.skill.sp + 1.0, float(u.skill.sp_cost))

        # SP on being hit (AUTO_DEFENSIVE): charge target's SP when it takes damage
        if u.attack_type != AttackType.HEAL and target.alive:
            sk_t = getattr(target, "skill", None)
            if sk_t is not None and sk_t.sp_gain_mode == SPGainMode.AUTO_DEFENSIVE:
                if not sk_t.active_remaining > 0:
                    sk_t.sp = min(sk_t.sp + 1.0, float(sk_t.sp_cost))

        # Talent hooks
        if u.attack_type != AttackType.HEAL:
            if target.talents:
                fire_on_hit_received(world, target, u, dealt)
            if u.talents:
                fire_on_attack_hit(world, u, target, dealt)
