"""Exusiai (能天使) — alias for generated.angel (char_103_angel).

Both generated/angel.py and generated/exusiai.py derive from the same character.
This file re-exports make_exusiai so the 'angel' stem is covered.
"""
from data.characters.exusiai import make_exusiai as make_angel

__all__ = ["make_angel"]
