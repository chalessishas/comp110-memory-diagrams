"""延迟事件队列 — 让"1.8s 后锤击"、"0.5s 后爆炸"这类机制可声明式表达。

EventQueue 是 World 的字段，按 fire_at (game time) 排序 min-heap。
每个 tick 的 EVENT_QUEUE phase 弹出所有到期事件并派发给对应 handler。
"""
from __future__ import annotations
from dataclasses import dataclass, field
from heapq import heappush, heappop
from typing import Any, Callable, Dict, Iterator, List, Tuple

# handler signature: (world, event_payload) -> None
# world 是 circular import，所以用 Any 占位；实际调用处做 type narrowing
EventHandler = Callable[[Any, "Event"], None]


@dataclass
class Event:
    """最小事件信封.

    kind 是字符串（不是 Enum）以便用户代码加新事件类型而无需改 core。
    payload 随意 —— 由 handler 自行解释。
    """
    fire_at: float                       # game time (seconds since battle start)
    kind: str                            # e.g. "hammer_strike" / "spawn" / "splash_damage"
    payload: Dict[str, Any] = field(default_factory=dict)
    _seq: int = 0                        # tie-breaker for stable ordering (set by queue)

    def __lt__(self, other: "Event") -> bool:
        # min-heap 按 (fire_at, _seq) 排序 — seq 保证同时刻事件 FIFO
        return (self.fire_at, self._seq) < (other.fire_at, other._seq)


class EventQueue:
    """Min-heap of scheduled events keyed by fire_at.

    Deterministic:
    - Ties broken by insertion order (_seq counter).
    - Handlers registered with register(kind, handler).
    - Multiple handlers per kind supported (called in registration order).
    """

    def __init__(self) -> None:
        self._heap: List[Event] = []
        self._seq_counter = 0
        self._handlers: Dict[str, List[EventHandler]] = {}

    # ---- scheduling -------------------------------------------------------

    def schedule(self, fire_at: float, kind: str, **payload: Any) -> Event:
        """Enqueue an event. Returns the created Event (useful for cancellation tests)."""
        self._seq_counter += 1
        ev = Event(fire_at=fire_at, kind=kind, payload=dict(payload), _seq=self._seq_counter)
        heappush(self._heap, ev)
        return ev

    def schedule_repeating(
        self,
        first_at: float,
        interval: float,
        count: int,
        kind: str,
        **payload: Any,
    ) -> List[Event]:
        """Fire the same event `count` times at `first_at, first_at+interval, ...`."""
        return [self.schedule(first_at + interval * i, kind, **payload) for i in range(count)]

    # ---- registration -----------------------------------------------------

    def register(self, kind: str, handler: EventHandler) -> None:
        self._handlers.setdefault(kind, []).append(handler)

    # ---- draining ---------------------------------------------------------

    def drain_due(self, now: float) -> Iterator[Event]:
        """Yield (and remove) every event with fire_at <= now, in order."""
        while self._heap and self._heap[0].fire_at <= now:
            yield heappop(self._heap)

    def dispatch_due(self, world: Any, now: float) -> int:
        """Drain and dispatch. Returns count dispatched."""
        count = 0
        for ev in self.drain_due(now):
            for handler in self._handlers.get(ev.kind, []):
                handler(world, ev)
            count += 1
        return count

    def __len__(self) -> int:
        return len(self._heap)

    def peek(self) -> Event | None:
        return self._heap[0] if self._heap else None

    def clear(self) -> None:
        self._heap.clear()
