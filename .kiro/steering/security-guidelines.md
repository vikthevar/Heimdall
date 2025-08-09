---
inclusion: always
---

# Security and Privacy Guidelines for Heimdall

## Data Protection Principles
- **Minimal Data Collection**: Only collect data necessary for functionality
- **Local Processing First**: Process audio and screenshots locally when possible
- **Encrypted Storage**: All cloud data must be encrypted at rest and in transit
- **User Consent**: Explicit consent for any data that leaves the device

## API Security
- Rate limiting for all external API calls
- API key rotation and secure storage
- Request/response logging for debugging (sanitized)
- Timeout handling for all network requests

## Screenshot Handling
```python
# Never store screenshots permanently without user consent
# Always blur sensitive information before cloud upload
# Implement automatic cleanup of temporary files
# Use secure deletion for sensitive image data
```

## Audio Processing Security
- Clear audio buffer after processing
- No persistent audio storage without consent
- Secure transmission to speech services
- Local fallback when possible

## AWS Integration Security
- Use IAM roles with minimal permissions
- Implement proper error handling for AWS failures
- Log all AWS operations for audit
- Regular security reviews of cloud resources

## Code Security Standards
- Input validation for all user commands
- Sanitize all data before external API calls
- Secure configuration management
- Regular dependency security updates