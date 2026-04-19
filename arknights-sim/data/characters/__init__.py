"""Operator factories.

Each operator has 3 skills (S1/S2/S3) in the real game; we expose named
factories parameterized by skill slot, e.g. make_silverash(slot='S3').

Stats here are placeholders marked as SOURCE=wiki_manual_e2l90 — they will be
replaced by the akgd ingest pipeline (data/ingest/akgd_fetcher.py) once that
pipeline lands. Any value here is a TODO against the canonical source.
"""
from .silverash import make_silverash
from .liskarm import make_liskarm
from .exusiai import make_exusiai

__all__ = ["make_silverash", "make_liskarm", "make_exusiai"]
