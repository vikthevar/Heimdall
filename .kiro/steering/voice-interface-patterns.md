---
inclusion: always
---

# Voice Interface Patterns for Heimdall

## Command Structure Patterns
- **Action + Target**: "Click the submit button"
- **Query + Context**: "What's in the top right corner?"
- **Navigation + Direction**: "Scroll down three times"
- **State + Request**: "Read what's on my screen"

## Response Patterns
- **Confirmation**: "I found the blue button and clicked it"
- **Clarification**: "I see multiple buttons, which one would you like?"
- **Error**: "I couldn't find that element, let me describe what I see instead"
- **Status**: "Processing your request, this may take a moment"

## Context Management
- Maintain conversation history for follow-up commands
- Remember user preferences for similar tasks
- Track screen state changes between commands
- Provide context-aware suggestions

## Error Handling Patterns
```python
# Always provide helpful alternatives
if not found_element:
    return f"I couldn't find {target}. I can see {alternatives}. Would you like me to try one of those?"

# Graceful degradation
if ocr_confidence < 0.7:
    return "The text isn't clear. Let me try a different approach or take a new screenshot."
```