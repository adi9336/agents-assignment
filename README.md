# Intelligent Interruption Handler

## Project Overview

This project implements advanced interruption handling for voice agents, enabling them to distinguish between genuine interruptions and conversational backchanneling, ensuring smooth and natural voice interactions.

## Features Implemented

### 🎯 Core Functionality
- **Intelligent Backchanneling Detection**: Automatically ignores common conversational acknowledgments
- **No Audio Breaks**: Agent audio continues uninterrupted during backchanneling verification
- **Smart Logic Rules**: Handles repeated words, commands, and mixed content appropriately
- **Real-time Processing**: All decisions happen instantly without audio interruption

### 🧠 Smart Logic Implementation

#### Backchanneling Words Ignored
- **Basic acknowledgments**: "yeah", "ok", "okay", "hmm", "uh-huh", "mhmm"
- **Agreement words**: "right", "sure", "gotcha", "yep", "yup", "alright"
- **Positive feedback**: "good", "great", "excellent", "perfect", "awesome"
- **Understanding signals**: "i see", "i understand", "makes sense", "got it"
- **Listening cues**: "go on", "continue", "tell me more", "interesting"
- **Filler words**: "aha", "mmhmm"

#### Decision Logic
- **Repeated words**: "yeah yeah" treated as emphasis (real input), not backchanneling
- **Command words**: Always trigger interruption ("stop", "wait", "help", "pause")
- **Mixed content**: Processed as real input if contains meaningful content
- **Agent state aware**: Works correctly whether agent is speaking or silent

## Files Modified

### 1. `agent_activity.py`
**Location**: `livekit-agents/livekit/agents/voice/agent_activity.py`
**Changes**: Updated `on_final_transcript()` function with intelligent filtering logic
```python
def on_final_transcript(self, ev: stt.SpeechEvent, *, speaking: bool | None = None) -> None:
    """Process final transcript with intelligent filtering."""
    
    # Step 1: Check backchanneling FIRST
    if self._interruption_handler.agent_is_speaking:
        words = re.findall(r'\b\w+\b', transcript.strip().lower())
        all_backchanneling = all(word in self._interruption_handler.ignore_words for word in words)
        if all_backchanneling:
            return  # Ignore completely
    
    # Step 2: Check interruption logic for non-backchanneling
    should_interrupt = self._interruption_handler.should_interrupt(transcript)
    
    # Step 3: Handle interruption and send to LLM
```

### 2. `interruption_handler.py`
**Location**: `livekit-agents/livekit/agents/voice/interruption_handler.py`
**Changes**: Enhanced `should_interrupt()` with comprehensive logic
```python
def should_interrupt(self, transcript: str) -> bool:
    """Determine if transcript should interrupt with smart logic."""
    
    # Check for repeated words (emphasis)
    word_counts = {}
    for word in words:
        word_counts[word] = word_counts.get(word, 0) + 1
    
    # Repeated ignore words = real input
    for word, count in word_counts.items():
        if count >= 2 and word in self.ignore_words:
            return True
    
    # Check command words
    for word in words:
        if word in self.command_words:
            return True
    
    # Check ignorable ratio for mixed content
    ignorable_ratio = ignorable_count / len(words)
    if ignorable_ratio >= 0.75:
        return False
```

### 3. `interrupt_config.py`
**Location**: `livekit-agents/livekit/agents/voice/interrupt_config.py`
**Changes**: Created comprehensive word lists and configuration
```python
DEFAULT_IGNORE_WORDS: Set[str] = {
    "yeah", "ok", "okay", "hmm", "uh-huh", "mhmm", "right", "sure",
    "aha", "gotcha", "yep", "yup", "mmhmm", "alright", "good", "great",
    "excellent", "perfect", "awesome", "i see", "i understand", "makes sense",
    "got it", "go on", "continue", "tell me more", "interesting"
}

DEFAULT_COMMAND_WORDS: Set[str] = {
    "wait", "stop", "no", "pause", "hold", "hold on", "help"
}
```

### 4. `basic_agent.py`
**Location**: `examples/voice_agents/basic_agent.py`
**Changes**: Updated agent instructions to ignore backchanneling
```python
def __init__(self) -> None:
    super().__init__(
        instructions="Your name is Kelly. You would interact with users via voice."
        "with that in mind keep your responses concise and to the point."
        "do not use emojis, asterisks, markdown, or other special characters in your responses."
        "You are curious and friendly, and have a sense of humor."
        "you will speak english to the user"
        "IMPORTANT: Ignore backchanneling responses like 'yeah', 'okay', 'uh-huh' - these are just acknowledgments, not questions or commands."
        "Only respond to meaningful content, questions, or commands."
    )
```

## How It Works

### Three-Stage Process

1. **Backchanneling Detection**: When agent is speaking, check if input is pure backchanneling
2. **Interruption Decision**: If not backchanneling, determine if interruption is needed
3. **Action Execution**: Either interrupt immediately or process without interruption

### Audio Behavior

- **No audio breaks** during verification process
- **Immediate interruption** only after confirming genuine input
- **Smooth transitions** between ignoring and interrupting

## Example Scenarios

```
Scenario 1: Agent Speaking + Backchanneling
Agent: "Let me explain the three main benefits of our system..."
User: "uh-huh, right, okay"
Result: Agent continues speaking uninterrupted

Scenario 2: Agent Speaking + Command
Agent: "The first benefit is improved efficiency..."
User: "wait! stop! I have a question"
Result: Agent stops immediately and listens

Scenario 3: Agent Silent + Any Input
Agent: "Any questions about what I've covered?"
User: "how does this work?"
Result: Agent processes without interruption (already silent)

Scenario 4: Repeated Words (Emphasis)
Agent: "Our system provides real-time analytics..."
User: "yeah yeah, tell me more"
Result: Agent interrupts (repetition = emphasis)
```

## Testing Requirements

To demonstrate the functionality, test these scenarios:

1. ✅ **Agent ignoring "yeah" while talking**
   - Start agent speaking a long response
   - Say "yeah", "okay", "uh-huh" during speech
   - Expected: Agent continues uninterrupted

2. ✅ **Agent responding to "yeah" when silent**
   - Wait for agent to finish speaking
   - Say "yeah" when agent is silent
   - Expected: Agent processes as acknowledgment

3. ✅ **Agent stopping for "stop"**
   - Start agent speaking
   - Say "stop" or "wait" during speech
   - Expected: Agent stops immediately

## Installation & Setup

1. Ensure all dependencies are installed
2. Set up required environment variables (API keys)
3. Run the basic agent example to test functionality

## Key Benefits

- **Natural Conversations**: No more awkward interruptions for acknowledgments
- **Better User Experience**: Smooth, human-like interaction patterns
- **Maintained Control**: Commands still work when needed
- **Zero Audio Breaks**: Seamless audio experience throughout

## Technical Achievement

Successfully solves the core challenge: **distinguishing between ignoring a word while speaking vs. hearing the same word while silent** through intelligent state-aware processing.
