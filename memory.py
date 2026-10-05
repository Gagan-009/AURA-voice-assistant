import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ConversationTurn:
    """Represents a single conversational turn in memory."""
    role: str  # "user" or "agent"
    text: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "text": self.text,
            "timestamp": self.timestamp,
            "iso_time": datetime.fromtimestamp(self.timestamp).isoformat(),
        }


class SessionMemory:
    """Lightweight, in-memory conversation context for AURA.

    Preserves the turn-by-turn history and session metrics for the duration
    of the running application without disk or database persistence.
    """

    def __init__(self) -> None:
        self._turns: List[ConversationTurn] = []
        self._start_time: float = time.time()

    def add_turn(self, role: str, text: str) -> ConversationTurn:
        """Record a conversational turn."""
        turn = ConversationTurn(role=role, text=text.strip())
        self._turns.append(turn)
        return turn

    @property
    def turn_count(self) -> int:
        return len(self._turns)

    @property
    def session_duration_seconds(self) -> float:
        return time.time() - self._start_time

    def get_history(self) -> List[Dict[str, Any]]:
        """Return all turns recorded in this session."""
        return [turn.to_dict() for turn in self._turns]

    def get_last_turn(self) -> Optional[Dict[str, Any]]:
        """Return the most recent turn, or None if empty."""
        if not self._turns:
            return None
        return self._turns[-1].to_dict()

    def get_recent_context(self, max_turns: int = 5) -> str:
        """Return a formatted string of the most recent turns."""
        recent = self._turns[-max_turns:]
        lines = []
        for turn in recent:
            speaker = "You" if turn.role == "user" else "AURA"
            lines.append(f"{speaker}: {turn.text}")
        return "\n".join(lines)

    def clear(self) -> None:
        """Reset the session memory."""
        self._turns.clear()
        self._start_time = time.time()

    def get_session_summary(self) -> Dict[str, Any]:
        """Return high-level summary metrics of the current session."""
        user_turns = sum(1 for t in self._turns if t.role == "user")
        agent_turns = sum(1 for t in self._turns if t.role == "agent")
        return {
            "total_turns": self.turn_count,
            "user_turns": user_turns,
            "agent_turns": agent_turns,
            "duration_seconds": round(self.session_duration_seconds, 2),
        }
