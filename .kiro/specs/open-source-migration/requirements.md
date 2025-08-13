# Requirements Document

## Introduction

This specification outlines the migration of the Heimdall AI voice assistant from paid API services to free, open-source alternatives while maintaining AWS S3 and DynamoDB for storage and database functionality. The goal is to create a fully functional, offline-capable system that reduces operational costs and eliminates API key dependencies while preserving all core accessibility features for visually impaired users.

## Requirements

### Requirement 1

**User Story:** As a visually impaired user, I want the system to understand my voice commands using free speech-to-text technology, so that I can control my computer without relying on paid services.

#### Acceptance Criteria

1. WHEN a user speaks a command THEN the system SHALL transcribe speech using either Whisper.cpp or Vosk
2. WHEN the user configures STT preferences THEN the system SHALL allow choosing between Whisper.cpp (better accuracy) and Vosk (lighter resource usage)
3. WHEN processing short voice commands THEN the system SHALL provide real-time transcription with latency under 3 seconds
4. WHEN the system is offline THEN speech-to-text SHALL continue to function without internet connectivity
5. WHEN audio quality is poor THEN the system SHALL provide confidence scores and request clarification

### Requirement 2

**User Story:** As a system administrator, I want automated screenshot capture using open-source tools, so that the system can analyze screen content without paid image processing services.

#### Acceptance Criteria

1. WHEN the system starts THEN it SHALL automatically capture screenshots every 30 seconds using Pillow and MSS
2. WHEN a user requests immediate screen analysis THEN the system SHALL capture a screenshot on-demand
3. WHEN multiple monitors are present THEN the system SHALL support capturing from all displays
4. WHEN screenshots are captured THEN they SHALL be stored locally and optionally uploaded to AWS S3
5. WHEN storage space is limited THEN the system SHALL implement automatic cleanup of old screenshots

### Requirement 3

**User Story:** As a visually impaired user, I want the system to read and understand screen content using free OCR and computer vision, so that I can navigate applications without expensive AI services.

#### Acceptance Criteria

1. WHEN a screenshot is captured THEN the system SHALL extract text using Tesseract OCR
2. WHEN analyzing UI elements THEN the system SHALL detect buttons, forms, and interactive elements using YOLOv8
3. WHEN screen analysis is complete THEN the system SHALL output a structured JSON with element types, text content, and coordinates
4. WHEN text is unclear or confidence is low THEN the system SHALL flag uncertain elements for user confirmation
5. WHEN processing complex layouts THEN the system SHALL maintain spatial relationships between elements

### Requirement 4

**User Story:** As a user, I want natural language understanding powered by free AI models, so that my commands are processed effectively without expensive API costs.

#### Acceptance Criteria

1. WHEN the system receives transcribed text THEN it SHALL process commands using Google Gemini free API
2. WHEN parsing user intent THEN the system SHALL match commands with detected screen elements
3. WHEN the Gemini API is unavailable THEN the system SHALL provide fallback intent parsing using rule-based matching
4. WHEN commands are ambiguous THEN the system SHALL ask clarifying questions through voice output
5. WHEN API rate limits are reached THEN the system SHALL gracefully fall back to local rule-based parsing

### Requirement 5

**User Story:** As a visually impaired user, I want clear voice feedback using open-source text-to-speech, so that I can receive system responses without relying on paid TTS services.

#### Acceptance Criteria

1. WHEN the system needs to provide feedback THEN it SHALL use either Coqui TTS or espeak-ng for voice synthesis
2. WHEN configuring voice preferences THEN users SHALL be able to choose between available TTS engines
3. WHEN generating speech THEN the system SHALL support different voice models and speaking rates
4. WHEN TTS processing fails THEN the system SHALL fall back to alternative output methods
5. WHEN the system is offline THEN voice output SHALL continue to function without internet connectivity

### Requirement 6

**User Story:** As a user, I want reliable screen control automation using open-source tools, so that voice commands can accurately interact with my computer interface.

#### Acceptance Criteria

1. WHEN executing click commands THEN the system SHALL use PyAutoGUI for mouse automation
2. WHEN performing keyboard actions THEN the system SHALL support text input and keyboard shortcuts
3. WHEN OS accessibility APIs are available THEN the system SHALL integrate them for more reliable element interaction
4. WHEN screen coordinates change THEN the system SHALL adapt to different screen resolutions and scaling
5. WHEN automation fails THEN the system SHALL provide error feedback and suggest alternative approaches

### Requirement 7

**User Story:** As a system administrator, I want AWS integration for data storage while using free processing tools, so that user preferences and logs are securely stored in the cloud.

#### Acceptance Criteria

1. WHEN screenshots are captured THEN they SHALL be stored in AWS S3 using the free tier
2. WHEN user preferences are modified THEN they SHALL be saved to AWS DynamoDB
3. WHEN commands are executed THEN action history SHALL be logged to DynamoDB for analysis
4. WHEN accessibility events occur THEN they SHALL be recorded for system improvement
5. WHEN AWS services are unavailable THEN the system SHALL continue operating with local storage fallback

### Requirement 8

**User Story:** As a developer, I want a configuration system that uses only free API services, so that the system can be deployed with minimal external service costs.

#### Acceptance Criteria

1. WHEN installing the system THEN all dependencies SHALL be installable via pip without paid subscriptions
2. WHEN configuring the system THEN only free API keys SHALL be required (Gemini API, AWS credentials)
3. WHEN API services are unavailable THEN the system SHALL function with local fallback processing
4. WHEN switching between models THEN users SHALL be able to configure STT, TTS, and AI model preferences via config.yaml
5. WHEN deploying the system THEN only free-tier API keys SHALL be required for full functionality

### Requirement 9

**User Story:** As a visually impaired user, I want the complete voice-to-action pipeline to work seamlessly with open-source tools, so that I can control my computer effectively without paid services.

#### Acceptance Criteria

1. WHEN I speak a command THEN the system SHALL process it through the complete pipeline: Voice Input → STT → OCR/CV → LLM Parsing → TTS → Screen Control → AWS Storage
2. WHEN the pipeline executes THEN each step SHALL complete within acceptable time limits (total < 5 seconds for simple commands)
3. WHEN any component fails THEN the system SHALL provide graceful degradation and error recovery
4. WHEN processing complex commands THEN the system SHALL maintain context across multiple interaction steps
5. WHEN the system encounters errors THEN it SHALL provide clear voice feedback about what went wrong and how to proceed