"""Core Arknights enum primitives.

These are the vocabulary every state/component/system refers to. Names follow
the English terminology used by the wiki (Terra Wiki) so they map cleanly to
game data dumps from Kengxxiao/ArknightsGameData.
"""
from __future__ import annotations
from enum import Enum, auto


class AttackType(str, Enum):
    """伤害类型."""
    PHYSICAL = "physical"        # 物理伤害 — reduced by DEF
    ARTS = "arts"                # 法术伤害 — reduced by RES %
    HEAL = "heal"                # 治疗 — restores HP, bypasses DEF/RES
    TRUE = "true"                # 真实伤害 — bypasses DEF and RES (rare)
    ELEMENTAL = "elemental"      # 元素伤害 — separate elemental HP pool


class ElementType(str, Enum):
    """元素伤害子类型 (新系统，2023+)."""
    NECROSIS = "necrosis"        # 神经损伤
    EROSION = "erosion"          # 凋亡
    COMBUSTION = "combustion"    # 灼燃


# Elemental Injury system constants (Terra Wiki)
ELEMENTAL_PROC_THRESHOLD: float = 1000.0
ELEMENTAL_IMMUNITY_DURATION: float = 10.0   # seconds of immunity after a proc


class StatusKind(str, Enum):
    """可挂在 Unit 上的状态效果种类。

    源：PRTS 状态栏 + Terra Wiki StatusEffect 列表。完整覆盖 20+ 类。
    """
    # --- 控制类 ---
    STUN = "stun"                # 眩晕：不可攻击/移动/技能
    BIND = "bind"                # 束缚：不可移动/攻击 (可释放技能)
    SLEEP = "sleep"              # 睡眠：受击唤醒
    FREEZE = "freeze"            # 冻结：不可移动/攻击/被选中
    COLD = "cold"                # 冻伤：减速 + 叠加变冻结
    LEVITATE = "levitate"        # 浮空：不可攻击地面目标
    SILENCE = "silence"          # 沉默：不可用技能
    # --- 位移类 (event，不是持续状态) ---
    # 见 events/move_event.py
    # --- 减益 ---
    SLOW = "slow"                # 减速
    FRAGILE = "fragile"          # 脆弱：受到更多伤害 (multiplier > 1)
    DEF_DOWN = "def_down"
    RES_DOWN = "res_down"
    ATK_DOWN = "atk_down"
    # --- 增益 ---
    ATK_UP = "atk_up"
    DEF_UP = "def_up"
    ASPD_UP = "aspd_up"          # 攻速
    DAMAGE_IMMUNE = "damage_immune"  # 无敌 (Hoshiguma S2, Saria S3)
    CAMOUFLAGE = "camouflage"    # 潜行 (Manticore, RI)
    # --- 独立 ---
    REGEN = "regen"              # 持续回血
    DOT = "dot"                  # 持续扣血
    SHIELD = "shield"            # 护盾


class BuffAxis(str, Enum):
    """Buff 作用的数值轴。"""
    ATK = "atk"
    DEF = "def"
    MAX_HP = "max_hp"
    ASPD = "aspd"          # 攻速（会影响 atk_interval 的倒数）
    MOVE_SPEED = "move_speed"
    RES = "res"


class BuffStack(str, Enum):
    """Buff 叠加方式（Terra Wiki Buff 公式）。"""
    RATIO = "ratio"              # 加法：+% 与其他 ratio 相加
    MULTIPLIER = "multiplier"    # 乘法：与其他 multiplier 相乘
    FLAT = "flat"                # 定值加减（如潜能 +40 ATK）


class Faction(str, Enum):
    """阵营 — 决定谁攻击谁，也用于 buff 判定（如乌萨斯学生自治团双倍）。"""
    ALLY = "ally"                # 我方干员
    ENEMY = "enemy"              # 敌方
    NEUTRAL = "neutral"


class Mobility(str, Enum):
    """移动方式 — 决定能被哪些攻击命中。"""
    GROUND = "ground"
    AIRBORNE = "airborne"


class TileType(str, Enum):
    """地块类型 — 部署和路径寻路约束。"""
    GROUND = "ground"            # 地面：melee op 可部署，可被敌人踩
    ELEVATED = "elevated"        # 高台：ranged op 可部署，不可被敌人踩
    GOAL = "goal"                # 敌人终点：进入=扣命
    BLOCKED = "blocked"          # 不可通行不可部署
    HOLE = "hole"                # 沟壑：可位移推入但不能部署


class Profession(str, Enum):
    """干员职业大类 (8 大职业)."""
    VANGUARD = "vanguard"        # 先锋
    GUARD = "guard"              # 近卫
    DEFENDER = "defender"        # 重装
    SNIPER = "sniper"            # 狙击
    CASTER = "caster"            # 术师
    MEDIC = "medic"              # 医疗
    SUPPORTER = "supporter"      # 辅助
    SPECIALIST = "specialist"    # 特种


class RoleArchetype(str, Enum):
    """职业分支 — 决定范围模板、特性、可用潜能。见 PRTS 职业分支页。"""
    # Guard 近卫分支
    GUARD_LORD = "guard_lord"
    GUARD_DREADNOUGHT = "guard_dreadnought"
    GUARD_CRUSHER = "guard_crusher"              # 撼地者（怒潮凛冬）
    GUARD_INSTRUCTOR = "guard_instructor"
    GUARD_SWORDMASTER = "guard_swordmaster"
    GUARD_MUSHA = "guard_musha"                  # 武士
    GUARD_LIBERATOR = "guard_liberator"          # 解放者（Mountain）
    GUARD_EARTHSHAKER = "guard_earthshaker"      # 撼动者（Flint）: ATK×2 when not blocking
    GUARD_REAPER = "guard_reaper"                # 收割者（Surtr）
    GUARD_FIGHTER = "guard_fighter"
    GUARD_CENTURION = "guard_centurion"
    # Defender 重装分支
    DEF_PROTECTOR = "def_protector"              # 守护者（Hoshiguma）
    DEF_JUGGERNAUT = "def_juggernaut"            # 不屈者
    DEF_ARTS_PROTECTOR = "def_arts_protector"
    DEF_GUARDIAN = "def_guardian"
    DEF_SENTINEL = "def_sentinel"                # 哨兵（Liskarm）
    DEF_FORTRESS = "def_fortress"                # 堡垒（Horn/Ashlock）ranged AoE ↔ melee toggle
    # Sniper 狙击分支
    SNIPER_MARKSMAN = "sniper_marksman"          # 速射手（Exusiai）
    SNIPER_HEAVY = "sniper_heavy"
    SNIPER_ARTILLERY = "sniper_artillery"        # 重炮
    SNIPER_SIEGE = "sniper_siege"                # 重狙
    SNIPER_ANTI_AIR = "sniper_anti_air"          # 反器械
    SNIPER_DEADEYE = "sniper_deadeye"            # 神射手
    # Caster 术师分支
    CASTER_CORE = "caster_core"                  # 中距离（SilverAsh... wait he's guard）
    CASTER_SPLASH = "caster_splash"              # 溅射（Eyjafjalla）
    CASTER_CHAIN = "caster_chain"                # 连锁（Leizi）
    CASTER_BLAST = "caster_blast"                # 冲锋术师
    CASTER_PHALANX = "caster_phalanx"            # 阵法术师
    CASTER_MYSTIC = "caster_mystic"              # 秘术师（Mostima）
    # Medic 医疗分支
    MEDIC_ST = "medic_st"                        # 单奶
    MEDIC_MULTI = "medic_multi"                  # 群奶
    MEDIC_WANDERING = "medic_wandering"          # 行医
    MEDIC_THERAPIST = "medic_therapist"
    MEDIC_INCANTATION = "medic_incantation"      # 咒纹医师（Quercus）: attacks enemies + heals allies
    # Supporter 辅助分支
    SUP_DECEL = "sup_decel"                      # 减速辅助
    SUP_BARD = "sup_bard"                        # 诗人
    SUP_HEXER = "sup_hexer"                      # 凝滞师
    SUP_SUMMONER = "sup_summoner"                # 召唤师
    SUP_ABJURER = "sup_abjurer"                  # 驱逐师
    # Specialist 特种分支
    SPEC_PUSHER = "spec_pusher"                  # 推击手（Shaw）
    SPEC_HOOKMASTER = "spec_hookmaster"          # 钩锁（FEater）
    SPEC_EXECUTOR = "spec_executor"              # 处决者（Kafka）
    SPEC_MERCHANT = "spec_merchant"              # 行商
    SPEC_DOLLKEEPER = "spec_dollkeeper"          # 傀儡师（Kal'tsit）
    SPEC_GEEK = "spec_geek"                      # 怪杰
    SPEC_AMBUSHER = "spec_ambusher"              # 伏击手
    # Vanguard 先锋分支
    VAN_PIONEER = "van_pioneer"                  # 先驱
    VAN_CHARGER = "van_charger"                  # 冲锋手
    VAN_STANDARD_BEARER = "van_standard_bearer"  # 执旗手
    VAN_AGENT = "van_agent"                      # 夺路者
    VAN_TACTICIAN = "van_tactician"              # 战术家


class SPGainMode(str, Enum):
    """SP 回复模式."""
    AUTO_TIME = "auto_time"          # 每秒 +1
    AUTO_ATTACK = "auto_attack"      # 每次攻击 +1 (含治疗)
    AUTO_DEFENSIVE = "auto_defensive"  # 每次受击 +1 (含闪避/抗性)
    ON_DEPLOY = "on_deploy"          # 部署时一次性给 SP


class SkillTrigger(str, Enum):
    """技能触发方式."""
    AUTO = "auto"                # 满 SP 自动释放
    MANUAL = "manual"            # 玩家点击
    PASSIVE = "passive"          # 常驻 (无 SP 概念)


class TickPhase(str, Enum):
    """tick 内的子阶段，决定 System 跑的顺序。

    一个 tick 内部按 phase 分片是避免事件顺序歧义的标准做法。
    """
    SPAWN = "spawn"              # 新单位入场
    STATUS_DECAY = "status_decay"  # 状态计时（stun/bind 等倒数）
    MOVEMENT = "movement"        # 敌人前进 / 干员位移
    TARGETING = "targeting"      # 确定本帧每个 unit 的目标
    COMBAT = "combat"            # 攻击/伤害结算
    SKILL = "skill"              # SP 回复 + 技能触发/结束
    EVENT_QUEUE = "event_queue"  # 处理本 tick 到期的定时事件
    GOAL = "goal"                # 敌人到终点扣命
    CLEANUP = "cleanup"          # 清理死单位 / 归档日志


# Tick ordering — 修改此列表等同修改战斗结算语义，慎动。
TICK_PHASE_ORDER: tuple[TickPhase, ...] = (
    TickPhase.SPAWN,
    TickPhase.STATUS_DECAY,
    TickPhase.MOVEMENT,
    TickPhase.TARGETING,
    TickPhase.COMBAT,
    TickPhase.SKILL,
    TickPhase.EVENT_QUEUE,
    TickPhase.GOAL,
    TickPhase.CLEANUP,
)

TICK_RATE = 10              # 10 Hz — 1 tick = 0.1s game-time
DT = 1.0 / TICK_RATE

# SP lockout window after a skill ends — no SP can be gained during this period.
# Documented in Terra Wiki: brief recovery pause after skill duration expires.
SP_POST_SKILL_LOCKOUT: float = 0.5   # seconds
