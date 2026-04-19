"""Enemy factories.

Source: PRTS 敌人一览 standard stats. Verify against akgd enemy_table next pass.
"""
from .originium_slug import make_originium_slug
from .originium_drone import make_drone

__all__ = ["make_originium_slug", "make_drone"]
