"""
Intelligent interruption handler for LiveKit voice agents.

This module provides context-aware interruption handling that distinguishes
between passive acknowledgments (backchanneling) and active commands based on
whether the agent is currently speaking.
"""

import logging
import re
from typing import Set

logger = logging.getLogger(__name__)


class InterruptionHandler:
    """
    Handles intelligent interruption decisions based on agent speaking state.
    
    Logic:
    - If agent is NOT speaking: All input is valid (don't interrupt)
    - If agent IS speaking:
        - Check if transcript contains command words → Interrupt
        - Check if all words are ignorable → Don't interrupt  
        - Otherwise → Interrupt
    """
    
    def __init__(
        self,
        ignore_words: Set[str],
        command_words: Set[str],
    ):
        """
        Initialize the interruption handler.
        
        Args:
            ignore_words: Set of words to ignore when agent is speaking
            command_words: Set of words that always trigger interruption
        """
        # Normalize all words to lowercase
        self.ignore_words = {w.lower().strip() for w in ignore_words}
        self.command_words = {w.lower().strip() for w in command_words}
        
        # Track agent state
        self._agent_is_speaking = False
        
        # Statistics for debugging
        self.stats = {
            "total_checks": 0,
            "interrupted": 0,
            "ignored": 0,
            "while_speaking": 0,
            "while_silent": 0,
        }
        
        logger.info(
            f"InterruptionHandler initialized: "
            f"{len(self.ignore_words)} ignore words, "
            f"{len(self.command_words)} command words"
        )
    
    @property
    def agent_is_speaking(self) -> bool:
        """Get current agent speaking state."""
        return self._agent_is_speaking
    
    def set_agent_speaking(self, is_speaking: bool) -> None:
        """
        Update agent speaking state.
        
        Args:
            is_speaking: True if agent is currently speaking
        """
        if self._agent_is_speaking != is_speaking:
            logger.debug(f"Agent speaking state: {is_speaking}")
            self._agent_is_speaking = is_speaking
    
    def should_interrupt(self, transcript: str) -> bool:
        """
        Determine if transcript should interrupt.
        
        NEW LOGIC: Ignore backchanneling words throughout conversation.
        Only interrupt for commands or real content (non-backchanneling).
        """
        self.stats["total_checks"] += 1
        
        # Normalize
        transcript_original = transcript
        transcript = transcript.strip().lower()
        
        if not transcript:
            return False
        
        # Extract words
        words = re.findall(r'\b\w+\b', transcript)
        
        if not words:
            return False
        
        logger.debug(
            f"Processing transcript: '{transcript_original}', "
            f"words: {words}"
        )
        
        # ===== RULE 1: Check for command words (ALWAYS interrupt) =====
        for word in words:
            if word in self.command_words:
                self.stats["interrupted"] += 1
                logger.info(f"INTERRUPT: Command '{word}' in '{transcript_original}'")
                return True
        
        # ===== RULE 2: Check for repeated words (emphasis) =====
        # If same word appears 2+ times, it's emphasis, not backchanneling
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # If any word repeated 2+ times, treat as real input (interrupt)
        for word, count in word_counts.items():
            if count >= 2:
                self.stats["interrupted"] += 1
                logger.info(
                    f"INTERRUPT: Repeated word '{word}' x{count} = emphasis: '{transcript_original}'"
                )
                return True
        
        # ===== RULE 3: Check if all words are backchanneling (ALWAYS ignore) =====
        all_backchanneling = all(word in self.ignore_words for word in words)
        
        if all_backchanneling:
            self.stats["ignored"] += 1
            logger.info(f"IGNORE: Pure backchanneling: '{transcript_original}'")
            return False
        
        # ===== RULE 4: Mixed content - check ratio =====
        ignorable_count = sum(1 for word in words if word in self.ignore_words)
        ignorable_ratio = ignorable_count / len(words)
        
        if ignorable_ratio >= 0.75:
            self.stats["ignored"] += 1
            logger.info(f"IGNORE: Mostly backchanneling ({ignorable_ratio:.0%}): '{transcript_original}'")
            return False
        
        # ===== RULE 5: Real content (interrupt) =====
        self.stats["interrupted"] += 1
        logger.info(f"INTERRUPT: Real input: '{transcript_original}'")
        return True
    
    def get_stats(self) -> dict:
        """Get handler statistics."""
        return self.stats.copy()
    
    def reset_stats(self) -> None:
        """Reset statistics."""
        self.stats = {
            "total_checks": 0,
            "interrupted": 0,
            "ignored": 0,
            "while_speaking": 0,
            "while_silent": 0,
        }

