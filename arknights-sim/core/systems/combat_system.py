"""Combat — 攻击冷却倒数 + 命中目标 + 伤害结算."""
from __future__ import annotations
from ..types import AttackType, Faction, RoleArchetype
from ..state.unit_state import SPGainMode
from .talent_registry import fire_on_attack_hit, fire_on_hit_received, fire_on_kill

_BESIEGER_BLOCKED_MULT = 1.5   # Besieger Sniper trait: 1.5× ATK vs blocked enemies


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
        multi_targets = getattr(u, "__targets__", [])

        # Fortress Defender ranged mode: __targets__ is populated, __target__ is None
        if multi_targets:
            _apply_fortress_ranged(world, u, multi_targets)
            continue

        if target is None or not target.alive:
            continue

        # Damage / heal
        raw = u.effective_atk
        # Besieger Sniper trait: 1.5× ATK when target is blocked by an ally
        if u.archetype == RoleArchetype.SNIPER_SIEGE and target.blocked_by_unit_ids:
            raw = int(raw * _BESIEGER_BLOCKED_MULT)
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

        # AOE splash — splash_atk_multiplier lets 撼地者 do 50% splash while
        # standard splash casters (Eyjafjalla/Angelina) keep 100%.
        if u.splash_radius > 0.0 and u.attack_type != AttackType.HEAL:
            if target.position is not None:
                tx, ty = target.position
                splash_raw = int(raw * u.splash_atk_multiplier)
                splash_faction = Faction.ENEMY if u.faction == Faction.ALLY else Faction.ALLY
                for other in world.units:
                    if other is target or not other.alive or other.faction != splash_faction:
                        continue
                    if other.position is None:
                        continue
                    ox, oy = other.position
                    if (ox - tx) ** 2 + (oy - ty) ** 2 <= u.splash_radius ** 2:
                        if u.attack_type == AttackType.PHYSICAL:
                            s = other.take_physical(splash_raw)
                        elif u.attack_type == AttackType.ARTS:
                            s = other.take_arts(splash_raw)
                        else:
                            s = other.take_true(splash_raw)
                        world.global_state.total_damage_dealt += s
                        world.log(
                            f"{u.name} splash → {other.name}  "
                            f"dmg={s}  ({other.hp}/{other.max_hp})"
                        )

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

        # Talent hooks — fire for both damage and heals (callbacks filter by type)
        if u.attack_type != AttackType.HEAL:
            if target.talents:
                fire_on_hit_received(world, target, u, dealt)
            if not target.alive and u.talents:
                fire_on_kill(world, u, target)
        if u.talents:
            fire_on_attack_hit(world, u, target, dealt)


def _apply_fortress_ranged(world, u, targets) -> None:
    """Fortress Defender ranged mode: hit every enemy in targets list simultaneously."""
    alive_targets = [t for t in targets if t.alive]
    if not alive_targets:
        return
    raw = u.effective_atk
    for target in alive_targets:
        if u.attack_type == AttackType.PHYSICAL:
            dealt = target.take_physical(raw)
        elif u.attack_type == AttackType.ARTS:
            dealt = target.take_arts(raw)
        else:
            dealt = target.take_true(raw)
        world.global_state.total_damage_dealt += dealt
        world.log(f"{u.name} (ranged) → {target.name}  dmg={dealt}  ({target.hp}/{target.max_hp})")
        if u.talents:
            fire_on_attack_hit(world, u, target, dealt)
        if not target.alive and u.talents:
            fire_on_kill(world, u, target)
    u.atk_cd = u.current_atk_interval
    if u.skill is not None:
        if u.skill.sp_gain_mode == SPGainMode.AUTO_ATTACK and not u.skill.active_remaining > 0:
            u.skill.sp = min(u.skill.sp + 1.0, float(u.skill.sp_cost))
