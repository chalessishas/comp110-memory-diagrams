"""Root conftest: ensure project root is on sys.path before any test module
manipulates it, so both v1/ and v2 core/ imports resolve correctly."""
import sys
from pathlib import Path

ROOT = str(Path(__file__).parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
