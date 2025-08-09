---
inclusion: always
---

# Accessibility Standards for Heimdall

## Core Principles
- **User-First Design**: Every feature must be tested with actual visually impaired users
- **Clear Audio Feedback**: All system responses must be clear, concise, and informative
- **Error Recovery**: Graceful handling of misunderstood commands with helpful suggestions
- **Privacy Protection**: Never store sensitive user data without explicit consent

## Voice Interface Guidelines
- Use natural, conversational language
- Provide confirmation for destructive actions
- Offer multiple ways to accomplish tasks
- Include audio cues for system state changes

## Code Standards
- All user-facing strings must be externalized for localization
- Audio processing must handle background noise gracefully
- Screen analysis must work across different display configurations
- Response times should be under 2 seconds for basic commands

## Testing Requirements
- Unit tests for all core components
- Integration tests with real audio samples
- Accessibility compliance validation
- Performance benchmarks for response times