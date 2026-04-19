from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Literal, Optional

SPGainMode = Literal["auto_time", "auto_attack"]


@dataclass
class Skill:
    name: str
    sp_cost: float
    duration: float
    sp_gain_mode: SPGainMode = "auto_time"
    on_start: Optional[Callable[["Operator"], None]] = None  # type: ignore[name-defined]
    on_end: Optional[Callable[["Operator"], None]] = None    # type: ignore[name-defined]

    def is_instant(self) -> bool:
        return self.duration <= 0
