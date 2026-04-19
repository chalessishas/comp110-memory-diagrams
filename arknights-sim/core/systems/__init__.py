"""Systems — 每 tick 按 TickPhase 顺序跑的纯函数变换.

每个 System 读/写 World 状态，不持有状态自身。
"""
from .status_system import status_decay_system
from .movement_system import movement_system
from .targeting_system import targeting_system
from .combat_system import combat_system
from .skill_system import skill_system
from .passive_talent_system import passive_talent_system
from .goal_system import goal_system
from .cleanup_system import cleanup_system


def register_default_systems(world) -> None:
    """Convenience: register all built-in systems in the default phase order."""
    from ..types import TickPhase
    world.register_system(TickPhase.STATUS_DECAY, status_decay_system)
    world.register_system(TickPhase.MOVEMENT, movement_system)
    world.register_system(TickPhase.TARGETING, targeting_system)
    world.register_system(TickPhase.COMBAT, combat_system)
    world.register_system(TickPhase.SKILL, skill_system)
    world.register_system(TickPhase.SKILL, passive_talent_system)
    world.register_system(TickPhase.GOAL, goal_system)
    world.register_system(TickPhase.CLEANUP, cleanup_system)
