#!/usr/bin/env python3
"""AAS-297: DanceBot Code Integration"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class DanceMove(Enum):
    """Available dance moves"""
    SPIN = "spin"
    HOP = "hop"
    SWAY = "sway"
    JUMP = "jump"
    MOONWALK = "moonwalk"
    GROOVE = "groove"


@dataclass
class Move:
    """Represents a single dance move"""
    type: DanceMove
    duration: float
    intensity: float


class DanceSequence:
    """Sequence of dance moves"""

    def __init__(self):
        """Initialize empty sequence"""
        self.moves: List[Move] = []

    def add_move(self, move_type: DanceMove,
                 duration: float, intensity: float = 1.0) -> None:
        """Add move to sequence"""
        move = Move(type=move_type, duration=duration,
                    intensity=intensity)
        self.moves.append(move)

    def get_duration(self) -> float:
        """Get total sequence duration"""
        return sum(m.duration for m in self.moves)

    def get_moves(self) -> List[Move]:
        """Get all moves"""
        return self.moves.copy()

    def clear(self) -> None:
        """Clear sequence"""
        self.moves.clear()


class DanceBot:
    """Main DanceBot control system"""

    def __init__(self):
        """Initialize DanceBot"""
        self.current_sequence: Optional[DanceSequence] = None
        self.is_dancing = False
        self.music_playing = False
        self.choreographies: Dict[str, DanceSequence] = {}

    def load_choreography(self, name: str,
                          sequence: DanceSequence) -> None:
        """Load a predefined choreography"""
        self.choreographies[name] = sequence

    def get_choreography(self, name: str) -> Optional[DanceSequence]:
        """Get choreography by name"""
        return self.choreographies.get(name)

    def start_music(self) -> bool:
        """Start background music"""
        self.music_playing = True
        return True

    def stop_music(self) -> bool:
        """Stop background music"""
        self.music_playing = False
        return True

    def dance(self, sequence: DanceSequence) -> bool:
        """Start dancing sequence"""
        if self.is_dancing:
            return False
        self.current_sequence = sequence
        self.is_dancing = True
        return True

    def stop_dance(self) -> bool:
        """Stop dancing"""
        self.is_dancing = False
        self.current_sequence = None
        return True

    def get_current_move(self) -> Optional[Move]:
        """Get current move being performed"""
        if self.current_sequence and self.is_dancing:
            moves = self.current_sequence.get_moves()
            return moves[0] if moves else None
        return None

    def list_choreographies(self) -> List[str]:
        """List all loaded choreographies"""
        return list(self.choreographies.keys())

    def create_sequence(self) -> DanceSequence:
        """Create new empty sequence"""
        return DanceSequence()

    def get_status(self) -> Dict[str, bool]:
        """Get DanceBot status"""
        return {
            'is_dancing': self.is_dancing,
            'music_playing': self.music_playing,
            'sequence_loaded': self.current_sequence is not None
        }

    def preset_waltz(self) -> DanceSequence:
        """Predefined waltz sequence"""
        seq = DanceSequence()
        seq.add_move(DanceMove.SWAY, 1.0, 0.8)
        seq.add_move(DanceMove.SWAY, 1.0, 0.8)
        seq.add_move(DanceMove.SPIN, 0.5, 0.9)
        return seq

    def preset_disco(self) -> DanceSequence:
        """Predefined disco sequence"""
        seq = DanceSequence()
        seq.add_move(DanceMove.GROOVE, 0.5, 1.0)
        seq.add_move(DanceMove.HOP, 0.5, 0.9)
        seq.add_move(DanceMove.JUMP, 0.3, 0.95)
        seq.add_move(DanceMove.SPIN, 0.5, 1.0)
        return seq

    def preset_moonwalk(self) -> DanceSequence:
        """Predefined moonwalk sequence"""
        seq = DanceSequence()
        seq.add_move(DanceMove.MOONWALK, 2.0, 1.0)
        seq.add_move(DanceMove.SPIN, 0.5, 0.8)
        return seq
