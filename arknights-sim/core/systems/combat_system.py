"""Combat — 攻击冷却倒数 + 命中目标 + 伤害结算."""
from __future__ import annotations
from ..types import AttackType, BuffAxis, BuffStack, ElementType, Faction, RoleArchetype
from ..state.unit_state import Buff, SPGainMode
from .talent_registry import fire_on_attack_hit, fire_on_hit_received, fire_on_kill, fire_on_pre_attack_hit

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

        # Multi-targets: Fortress ranged AoE or multi-target medic heal
        if multi_targets:
            if u.attack_type == AttackType.HEAL:
                _apply_multi_heal(world, u, multi_targets)
            else:
                _apply_fortress_ranged(world, u, multi_targets)
            continue

        if target is None or not target.alive:
            continue

        # Damage / heal
        raw = u.effective_atk
        # Besieger Sniper trait: 1.5× ATK when target is blocked by an ally
        if u.archetype == RoleArchetype.SNIPER_SIEGE and target.blocked_by_unit_ids:
            raw = int(raw * _BESIEGER_BLOCKED_MULT)
        # Crit check — only for damage (not heals), only when crit_chance > 0
        if u.crit_chance > 0.0 and u.attack_type != AttackType.HEAL:
            if world.rng.random() < u.crit_chance:
                raw = int(raw * u.crit_multiplier)
        # Pre-attack hook — fires before damage so talents can inspect target state
        if u.talents and u.attack_type not in (AttackType.HEAL, AttackType.ELEMENTAL):
            fire_on_pre_attack_hit(world, u, target)

        if u.attack_type == AttackType.PHYSICAL:
            dealt = target.take_physical(raw)
        elif u.attack_type == AttackType.ARTS:
            dealt = target.take_arts(raw)
        elif u.attack_type == AttackType.HEAL:
            dealt = target.heal(raw)
            world.global_state.total_healing_done += dealt
        elif u.attack_type == AttackType.ELEMENTAL:
            # Elemental attacks charge the target's elemental bar; no direct HP damage
            dealt = 0
            if u.element_type is not None:
                now = world.global_state.elapsed
                proc = target.accumulate_elemental(float(raw), u.element_type, now)
                if proc:
                    _apply_elemental_proc(world, target, u.element_type)
                    dealt = raw  # record proc burst as "dealt" for logging
        else:
            dealt = target.take_true(raw)

        if u.attack_type not in (AttackType.HEAL, AttackType.ELEMENTAL):
            world.global_state.total_damage_dealt += dealt

        world.log(
            f"{u.name} → {target.name}  "
            f"{'heal' if u.attack_type == AttackType.HEAL else 'dmg'}={dealt}  "
            f"({target.hp}/{target.max_hp})"
        )

        # GUARD_CENTURION trait: attack hits ALL currently blocked enemies simultaneously
        if u.archetype == RoleArchetype.GUARD_CENTURION:
            _apply_centurion_cleave(world, u, target, raw)

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

        # Chain attack — Chain Caster trait: after primary hit, jump to N nearest enemies
        if u.chain_count > 0 and u.attack_type != AttackType.HEAL and target.position is not None:
            _apply_chain(world, u, target, raw)

        # Blast pierce — CASTER_BLAST: hits all enemies along attack ray through primary target
        if u.blast_pierce and u.attack_type != AttackType.HEAL and u.position is not None:
            _apply_blast_pierce(world, u, target, raw)

        # Push-back — SPEC_PUSHER trait: retreat target along its path
        if u.push_distance > 0 and target.alive:
            _apply_push(target, u.push_distance)
            world.log(f"{u.name} pushes {target.name} back {u.push_distance} tiles")

        u.atk_cd = u.current_atk_interval

        # Ammo-based skill: consume one charge per attack hit
        if u.skill is not None and u.skill.ammo_remaining > 0:
            u.skill.ammo_remaining -= 1

        # SP on attack
        if u.skill is not None:
            sk = u.skill
            if sk.sp_gain_mode == SPGainMode.AUTO_ATTACK and not sk.active_remaining > 0:
                if world.global_state.elapsed >= sk.sp_lockout_until:
                    sk.sp = min(sk.sp + 1.0, float(sk.sp_cost))

        # SP on being hit (AUTO_DEFENSIVE): charge target's SP when it takes damage
        # can_use_skill() blocks SP gain while STUN/BIND/FREEZE/SLEEP/SILENCE
        if u.attack_type != AttackType.HEAL and target.alive and target.can_use_skill():
            sk_t = getattr(target, "skill", None)
            if sk_t is not None and sk_t.sp_gain_mode == SPGainMode.AUTO_DEFENSIVE:
                if not sk_t.active_remaining > 0:
                    if world.global_state.elapsed >= sk_t.sp_lockout_until:
                        sk_t.sp = min(sk_t.sp + 1.0, float(sk_t.sp_cost))

        # Talent hooks — fire for both damage and heals (callbacks filter by type)
        if u.attack_type != AttackType.HEAL:
            if target.talents:
                fire_on_hit_received(world, target, u, dealt)
            if not target.alive and u.talents:
                fire_on_kill(world, u, target)
        if u.talents:
            fire_on_attack_hit(world, u, target, dealt)


_NECROSIS_PROC_HP_RATIO = 0.15   # Arts damage = 15% max HP
_NECROSIS_PROC_MIN = 600         # minimum proc damage
_EROSION_PROC_PHYS = 800         # Physical true damage on proc
_EROSION_DEF_DEBUFF = 100        # permanent flat DEF reduction
_COMBUSTION_PROC_ARTS = 1200     # Arts damage on proc
_COMBUSTION_RES_DEBUFF = 20.0    # permanent RES% reduction


def _apply_elemental_proc(world, target, element: ElementType) -> None:
    """Execute burst effects when an elemental bar fills to 1000."""
    if element == ElementType.NECROSIS:
        dmg = max(_NECROSIS_PROC_MIN, int(target.max_hp * _NECROSIS_PROC_HP_RATIO))
        dealt = target.take_arts(dmg)
        world.global_state.total_damage_dealt += dealt
        world.log(f"[NECROSIS PROC] {target.name}  arts_dmg={dealt}")
    elif element == ElementType.EROSION:
        dealt = target.take_true(_EROSION_PROC_PHYS)
        world.global_state.total_damage_dealt += dealt
        # Permanent DEF reduction (expires_at = infinity)
        target.buffs.append(Buff(
            axis=BuffAxis.DEF, stack=BuffStack.FLAT,
            value=-_EROSION_DEF_DEBUFF,
            source_tag=f"erosion_proc_{id(target)}",
            expires_at=float("inf"),
        ))
        world.log(f"[EROSION PROC] {target.name}  true_dmg={dealt}  def-{_EROSION_DEF_DEBUFF}")
    elif element == ElementType.COMBUSTION:
        dealt = target.take_arts(_COMBUSTION_PROC_ARTS)
        world.global_state.total_damage_dealt += dealt
        # Permanent RES reduction (expires_at = infinity)
        target.buffs.append(Buff(
            axis=BuffAxis.RES, stack=BuffStack.FLAT,
            value=-_COMBUSTION_RES_DEBUFF,
            source_tag=f"combustion_proc_{id(target)}",
            expires_at=float("inf"),
        ))
        world.log(f"[COMBUSTION PROC] {target.name}  arts_dmg={dealt}  res-{_COMBUSTION_RES_DEBUFF}")


def _apply_multi_heal(world, u, targets) -> None:
    """Multi-target medic: heal all allies in targets simultaneously."""
    alive_targets = [t for t in targets if t.alive]
    if not alive_targets:
        return
    raw = u.effective_atk
    for target in alive_targets:
        dealt = target.heal(raw)
        world.global_state.total_healing_done += dealt
        world.log(f"{u.name} → {target.name}  heal={dealt}  ({target.hp}/{target.max_hp})")
        if u.talents:
            fire_on_attack_hit(world, u, target, dealt)
    u.atk_cd = u.current_atk_interval
    if u.skill is not None and u.skill.ammo_remaining > 0:
        u.skill.ammo_remaining -= 1
    if u.skill is not None:
        sk = u.skill
        if sk.sp_gain_mode == SPGainMode.AUTO_ATTACK and not sk.active_remaining > 0:
            if world.global_state.elapsed >= sk.sp_lockout_until:
                sk.sp = min(sk.sp + 1.0, float(sk.sp_cost))


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
    if u.skill is not None and u.skill.ammo_remaining > 0:
        u.skill.ammo_remaining -= 1
    if u.skill is not None:
        sk = u.skill
        if sk.sp_gain_mode == SPGainMode.AUTO_ATTACK and not sk.active_remaining > 0:
            if world.global_state.elapsed >= sk.sp_lockout_until:
                sk.sp = min(sk.sp + 1.0, float(sk.sp_cost))


def _apply_chain(world, attacker, primary_target, primary_raw: int) -> None:
    """Chain Caster: after primary hit, chain to N nearest enemies (by distance to primary target)."""
    chain_raw = int(primary_raw * attacker.chain_damage_ratio)
    already_hit = {primary_target.unit_id}
    tx, ty = primary_target.position

    for _ in range(attacker.chain_count):
        candidates = [
            e for e in world.enemies()
            if e.alive and e.unit_id not in already_hit and e.position is not None
        ]
        if not candidates:
            break
        # Nearest enemy to the current chain position (position of last-hit enemy)
        next_target = min(
            candidates,
            key=lambda e: (e.position[0] - tx) ** 2 + (e.position[1] - ty) ** 2,
        )
        already_hit.add(next_target.unit_id)
        if attacker.attack_type == AttackType.PHYSICAL:
            dealt = next_target.take_physical(chain_raw)
        elif attacker.attack_type == AttackType.ARTS:
            dealt = next_target.take_arts(chain_raw)
        else:
            dealt = next_target.take_true(chain_raw)
        world.global_state.total_damage_dealt += dealt
        world.log(
            f"{attacker.name} chain → {next_target.name}  "
            f"dmg={dealt}  ({next_target.hp}/{next_target.max_hp})"
        )
        if attacker.talents:
            fire_on_attack_hit(world, attacker, next_target, dealt)
        if not next_target.alive and attacker.talents:
            fire_on_kill(world, attacker, next_target)
        # Update chain origin to new target's position
        tx, ty = next_target.position


def _apply_blast_pierce(
    world, attacker, primary_target, raw: int, atk_multiplier: float = 1.0
) -> None:
    """Blast Caster: deal damage to all enemies along the ray from attacker through primary target.

    Uses unnormalized dot-product projection to avoid sqrt; perp_sq threshold = 0.25 (0.5 tiles²).
    """
    if primary_target.position is None:
        return
    ox, oy = attacker.position
    tx, ty = primary_target.position
    dx, dy = tx - ox, ty - oy
    len_sq = dx * dx + dy * dy
    if len_sq < 1e-6:
        return

    blast_raw = int(raw * atk_multiplier)
    for e in world.enemies():
        if e is primary_target or not e.alive or e.position is None:
            continue
        ex, ey = e.position
        vx, vy = ex - ox, ey - oy
        proj = vx * dx + vy * dy          # unnormalized scalar projection
        if proj <= 0:
            continue                       # enemy is behind or at attacker side
        # perp_sq = |v|² - proj²/len_sq (perpendicular distance squared)
        perp_sq = (vx * vx + vy * vy) - proj * proj / len_sq
        if perp_sq > 0.25:               # > 0.5 tiles off the ray
            continue
        if attacker.attack_type == AttackType.ARTS:
            dealt = e.take_arts(blast_raw)
        elif attacker.attack_type == AttackType.PHYSICAL:
            dealt = e.take_physical(blast_raw)
        else:
            dealt = e.take_true(blast_raw)
        world.global_state.total_damage_dealt += dealt
        world.log(f"{attacker.name} blast → {e.name}  dmg={dealt}  ({e.hp}/{e.max_hp})")
        if attacker.talents:
            fire_on_attack_hit(world, attacker, e, dealt)
        if not e.alive and attacker.talents:
            fire_on_kill(world, attacker, e)


def _apply_centurion_cleave(world, attacker, primary_target, raw: int) -> None:
    """GUARD_CENTURION trait: deal damage to all OTHER enemies currently blocked by attacker."""
    for e in world.enemies():
        if e is primary_target or not e.alive:
            continue
        if attacker.unit_id not in e.blocked_by_unit_ids:
            continue
        if attacker.attack_type == AttackType.PHYSICAL:
            dealt = e.take_physical(raw)
        elif attacker.attack_type == AttackType.ARTS:
            dealt = e.take_arts(raw)
        else:
            dealt = e.take_true(raw)
        world.global_state.total_damage_dealt += dealt
        world.log(
            f"{attacker.name} cleave → {e.name}  dmg={dealt}  ({e.hp}/{e.max_hp})"
        )
        if attacker.talents:
            fire_on_attack_hit(world, attacker, e, dealt)
        if not e.alive and attacker.talents:
            fire_on_kill(world, attacker, e)


def _apply_push(target, distance: int) -> None:
    """Push target backward along its path by `distance` tiles (reduce path_progress)."""
    new_progress = max(0.0, target.path_progress - float(distance))
    target.path_progress = new_progress
    # Snap position to the new path tile so blocking stays consistent
    if target.path:
        tile_idx = min(int(new_progress), len(target.path) - 1)
        tx, ty = target.path[tile_idx]
        target.position = (float(tx), float(ty))
