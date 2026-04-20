"""UnitState — 干员和敌人的统一状态容器.

区别通过 `faction` 和挂载的 components 区分，而非继承。这与你提出的
"干员状态 + 敌人状态"相符——它们本质是同一种实体的两种配置。
"""
from __future__ import annotations
from dataclasses import dataclass, field
from itertools import count
from typing import Dict, List, Optional, Tuple

from ..types import (
    AttackType, BuffAxis, BuffStack, Faction, Mobility, Profession,
    RoleArchetype, SPGainMode, SkillTrigger, StatusKind,
)


_unit_id_counter = count(1)


@dataclass
class Buff:
    """一条可叠加的属性修饰. 命名尊重 Terra Wiki buff 公式."""
    axis: BuffAxis                       # 作用的数值轴
    stack: BuffStack                     # 叠加方式
    value: float                         # ratio 时是 +%（如 1.80 = +180%），mult 时是乘子（如 1.30），flat 时是绝对值
    source_tag: str = ""                 # 归属（方便移除时精确定位，避免 float == 陷阱）
    expires_at: float = float("inf")     # game time


@dataclass
class StatusEffect:
    """挂在 unit 上的控制/增益/减益效果."""
    kind: StatusKind
    source_tag: str = ""
    expires_at: float = float("inf")     # game time
    stacks: int = 1                      # 如 cold 可叠加
    params: Dict[str, float] = field(default_factory=dict)


@dataclass
class SkillComponent:
    """干员的技能组件. 一个干员可能有 3 个技能 (S1/S2/S3)，当前挂载哪个由
    `active_slot` 决定（战斗开始前玩家选的，战斗中不可换）.
    """
    name: str
    slot: str                            # "S1" | "S2" | "S3"
    sp_cost: int                         # 实际游戏是整数
    initial_sp: int = 0                  # 部署时预存 SP (如防御回复初始 SP)
    duration: float = 0.0                # 0 表示瞬发；>0 表示持续型
    sp_gain_mode: SPGainMode = SPGainMode.AUTO_TIME
    trigger: SkillTrigger = SkillTrigger.AUTO

    # Runtime state
    sp: float = 0.0
    active_remaining: float = 0.0        # 当前持续剩余
    locked_out: bool = False             # SP 满但无目标时锁 SP (Terra Wiki Lockout)
    fire_count: int = 0                  # 已释放次数

    # Behavior hooks (by tag name — resolved via Skill registry)
    behavior_tag: str = ""               # e.g. "silverash_s3" → maps to on_start/on_tick/on_end funcs
    requires_target: bool = True         # False = fires on SP full regardless of target (buff-only skills)


@dataclass
class TalentComponent:
    """天赋组件——条件触发的被动. 可能随潜能/模组强化."""
    name: str
    behavior_tag: str = ""
    # 条件与参数由 behavior 函数读取
    params: Dict[str, float] = field(default_factory=dict)


@dataclass
class ModuleComponent:
    """模组组件——精二后可选装. 提供额外属性 + 特性追加."""
    name: str
    stage: int = 0                       # 0/1/2/3 对应未装/一阶/二阶/三阶
    bonus_hp: int = 0
    bonus_atk: int = 0
    bonus_def: int = 0
    behavior_tag: str = ""               # 特性追加行为


@dataclass
class RangeShape:
    """攻击范围形状. 支持三种.

    tiles:   一组相对坐标 (dx, dy) 表示覆盖格子——game-internal 的标准表达
    radius:  欧氏半径（splash 用）
    extended_tiles: 开启技能后扩展的额外格子 (如怒潮凛冬 S2 range 扩大)
    """
    tiles: Tuple[Tuple[int, int], ...] = ()
    radius: float = 0.0
    extended_tiles: Tuple[Tuple[int, int], ...] = ()


@dataclass
class UnitState:
    """单位运行时状态——干员和敌人共用."""

    # 身份
    name: str
    faction: Faction
    unit_id: int = field(default_factory=lambda: next(_unit_id_counter))

    # 核心属性（基础值，buff 走 _buffs 列表）
    max_hp: int = 1
    atk: int = 0
    defence: int = 0
    res: float = 0.0                     # 法抗 % (0-100)
    atk_interval: float = 1.0            # 基础攻击间隔 (秒)

    # 分类
    profession: Optional[Profession] = None
    archetype: Optional[RoleArchetype] = None
    mobility: Mobility = Mobility.GROUND
    attack_type: AttackType = AttackType.PHYSICAL
    attack_range_melee: bool = True      # True = 能攻击所在格 + (可能)范围外，False 纯远程
    block: int = 0                       # 阻挡数 (0 表示不阻挡)
    range_shape: RangeShape = field(default_factory=RangeShape)
    splash_radius: float = 0.0           # 溅射半径（非零即 AOE）
    splash_atk_multiplier: float = 1.0   # 溅射伤害倍率（撼地者=0.5，法师=1.0）
    cost: int = 0                        # 部署费用
    redeploy_cd: float = 70.0            # 再部署冷却 (秒)

    # 运行时状态
    hp: int = 0
    alive: bool = True
    deployed: bool = False               # 干员：是否已部署；敌人：已入场=True
    counted_death: bool = False          # cleanup_system sets True to prevent double-counting
    position: Optional[Tuple[float, float]] = None  # 干员部署位置 / 敌人当前位置（浮点，插值）
    facing: Tuple[int, int] = (1, 0)     # 干员朝向 (dx, dy) — 影响 range_shape 旋转
    atk_cd: float = 0.0                  # 攻击冷却剩余
    deploy_time: float = -1.0            # 部署时刻；-1 表示未部署
    redeploy_available_at: float = 0.0   # 可再部署的游戏时间；0 = 立即可用

    # 敌人路径
    path: List[Tuple[int, int]] = field(default_factory=list)
    path_progress: float = 0.0           # tile 单位，允许非整数（插值）
    move_speed: float = 1.0              # tiles/s (敌人)
    weight: int = 1                      # 敌人重量 (0=轻, 1=标准, 2=重, 3=特重); 用于 Besieger 优先级
    blocked_by_unit_ids: List[int] = field(default_factory=list)  # 被谁阻挡着

    # 技能/天赋/模组
    skill: Optional[SkillComponent] = None
    talents: List[TalentComponent] = field(default_factory=list)
    module: Optional[ModuleComponent] = None

    # 状态效果 + Buff
    buffs: List[Buff] = field(default_factory=list)
    statuses: List[StatusEffect] = field(default_factory=list)
    undying_charges: int = 0    # 防死次数 (Specter/Chen 等)；>0 时致命伤改为留 1 HP

    def __post_init__(self) -> None:
        if self.hp == 0:
            self.hp = self.max_hp
        # Profession-aware default range for allies when factory didn't set one.
        # Enemies don't use range_shape (they attack their blocker directly).
        if (self.faction == Faction.ALLY
                and not self.range_shape.tiles
                and self.range_shape.radius == 0.0):
            self.range_shape = _default_range_for(
                melee=self.attack_range_melee,
                profession=self.profession,
                block=self.block,
            )

    # ---- stats pipeline ---------------------------------------------------

    def effective_stat(self, axis: BuffAxis, base: float | None = None) -> float:
        """Apply buff pipeline to any stat axis.

        Formula (Terra Wiki):
            intermediate = FLOOR(base * (1 + Σ ratio_buffs))
            final        = FLOOR(intermediate * Π mult_buffs) + Σ flat_buffs
        """
        if base is None:
            base = {
                BuffAxis.ATK: self.atk,
                BuffAxis.DEF: self.defence,
                BuffAxis.MAX_HP: self.max_hp,
                BuffAxis.ASPD: 100.0,           # base 攻速 = 100 (游戏内规约)
                BuffAxis.MOVE_SPEED: self.move_speed,
                BuffAxis.RES: self.res,
            }[axis]

        ratios = sum(b.value for b in self.buffs if b.axis == axis and b.stack == BuffStack.RATIO)
        mults = 1.0
        flats = 0.0
        for b in self.buffs:
            if b.axis != axis:
                continue
            if b.stack == BuffStack.MULTIPLIER:
                mults *= b.value
            elif b.stack == BuffStack.FLAT:
                flats += b.value

        # FLOOR only applies to integer stats; float stats (MOVE_SPEED, RES) use raw float arithmetic
        _int_axes = {BuffAxis.ATK, BuffAxis.DEF, BuffAxis.MAX_HP, BuffAxis.ASPD}
        if axis in _int_axes:
            from math import floor
            intermediate = floor(base * (1.0 + ratios))
            return floor(intermediate * mults) + flats
        else:
            return base * (1.0 + ratios) * mults + flats

    @property
    def effective_atk(self) -> int:
        return int(self.effective_stat(BuffAxis.ATK))

    @property
    def effective_def(self) -> int:
        return int(self.effective_stat(BuffAxis.DEF))

    @property
    def effective_aspd(self) -> float:
        """攻速，100 = 正常. 150 = 攻击间隔缩短为 100/150."""
        return self.effective_stat(BuffAxis.ASPD)

    @property
    def current_atk_interval(self) -> float:
        """考虑攻速 buff 后的实际攻击间隔. ASPD clamped to [20, 600] per wiki."""
        aspd = max(20.0, min(600.0, self.effective_aspd))
        return self.atk_interval * 100.0 / aspd

    # ---- status helpers ---------------------------------------------------

    def has_status(self, kind: StatusKind) -> bool:
        return any(s.kind == kind for s in self.statuses)

    def can_act(self) -> bool:
        """Stun/Bind/Freeze/Sleep 都阻止行动. Silence 只阻止技能."""
        blocking = {StatusKind.STUN, StatusKind.BIND, StatusKind.FREEZE, StatusKind.SLEEP}
        return not any(s.kind in blocking for s in self.statuses)

    def can_use_skill(self) -> bool:
        if not self.can_act():
            return False
        return not self.has_status(StatusKind.SILENCE)

    # ---- damage / heal ----------------------------------------------------

    def talent_damage_reduction(self) -> float:
        """Returns total passive damage reduction [0, 1) from talents (e.g. Hoshiguma)."""
        total = 0.0
        for t in self.talents:
            if t.behavior_tag == "hoshiguma_overweight":
                if self.max_hp > 0 and self.hp / self.max_hp > t.params.get("hp_threshold", 0.5):
                    total += t.params.get("reduction", 0.0)
        return min(total, 0.99)  # cap so at least 1% damage goes through

    def take_damage(self, amount: int) -> int:
        if self.has_status(StatusKind.DAMAGE_IMMUNE):
            return 0
        dr = self.talent_damage_reduction()
        actual = max(1, int(amount * (1.0 - dr)))
        # SHIELD absorbs damage before HP (largest shield pool used first)
        for s in sorted(self.statuses, key=lambda x: -x.params.get("amount", 0)):
            if s.kind != StatusKind.SHIELD:
                continue
            pool = s.params.get("amount", 0)
            absorbed = min(pool, actual)
            s.params["amount"] = pool - absorbed
            actual -= absorbed
            if s.params["amount"] <= 0:
                self.statuses = [x for x in self.statuses if x is not s]
            if actual == 0:
                return 0
        # SLEEP: unit wakes on any hit that deals damage
        if actual > 0:
            self.statuses = [s for s in self.statuses if s.kind != StatusKind.SLEEP]
        new_hp = self.hp - actual
        if new_hp <= 0 and self.undying_charges > 0:
            self.undying_charges -= 1
            self.hp = 1
            self._undying_just_triggered = True
            return actual
        self.hp = max(0, new_hp)
        if self.hp == 0:
            self.alive = False
        return actual

    def _fragile_mult(self) -> float:
        """Wiki rule: same source_tag → take max; different sources → multiply."""
        by_source: Dict[str, float] = {}
        for s in self.statuses:
            if s.kind != StatusKind.FRAGILE:
                continue
            amount = s.params.get("amount", 0.3)
            key = s.source_tag or "__default__"
            if key not in by_source or amount > by_source[key]:
                by_source[key] = amount
        mult = 1.0
        for amount in by_source.values():
            mult *= 1.0 + amount
        return mult

    def take_physical(self, raw_atk: int) -> int:
        effective_def = self.effective_def
        dmg = max(int(raw_atk * 0.05), raw_atk - effective_def)
        return self.take_damage(int(dmg * self._fragile_mult()))

    def take_arts(self, raw_atk: int) -> int:
        res = self.effective_stat(BuffAxis.RES, base=self.res)
        dmg = max(1, int(raw_atk * (1.0 - res / 100.0)))
        return self.take_damage(int(dmg * self._fragile_mult()))

    def take_true(self, raw_atk: int) -> int:
        return self.take_damage(raw_atk)

    def heal(self, amount: int) -> int:
        healed = min(int(amount), self.max_hp - self.hp)
        self.hp += healed
        return healed


def _default_range_for(*, melee: bool, profession, block: int) -> RangeShape:
    """Profession-level range templates for generated factories that don't set one."""
    from ..types import Profession
    if melee and block > 0:
        tiles = [(0, 0)]
        if profession == Profession.GUARD:
            tiles.append((1, 0))
        return RangeShape(tiles=tuple(tiles))
    if profession == Profession.SNIPER:
        return RangeShape(tiles=tuple(
            (dx, dy) for dx in range(-1, 4) for dy in range(-1, 2)
        ))
    if profession == Profession.CASTER:
        return RangeShape(tiles=tuple(
            (dx, dy) for dx in range(-1, 3) for dy in range(-1, 2)
        ))
    if profession == Profession.MEDIC:
        return RangeShape(tiles=tuple(
            (dx, dy) for dx in range(-1, 2) for dy in range(-1, 2)
        ))
    if profession == Profession.SUPPORTER:
        return RangeShape(tiles=tuple(
            (dx, dy) for dx in range(-1, 3) for dy in range(-1, 2)
        ))
    if profession == Profession.SPECIALIST:
        return RangeShape(tiles=((0, 0), (1, 0)))
    if profession == Profession.VANGUARD:
        return RangeShape(tiles=((0, 0), (1, 0)))
    return RangeShape(tiles=((0, 0),))
