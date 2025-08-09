# Security Guidelines for Heimdall

## 🔐 Environment Variables and API Keys

### Required API Keys
- **OpenAI API Key**: For Whisper speech-to-text and GPT-4o intent parsing
- **ElevenLabs API Key**: For text-to-speech voice output
- **AWS Credentials**: For cloud storage and logging (optional)

### Setup Instructions
1. Copy `.env.example` to `.env`
2. Fill in your actual API keys (never commit `.env` to version control)
3. Ensure `.env` is listed in `.gitignore`

### API Key Security Best Practices
- **Never commit API keys** to version control
- **Use environment variables** for all sensitive configuration
- **Rotate keys regularly** and monitor usage
- **Use least-privilege access** for AWS IAM roles
- **Enable API key restrictions** where possible (IP allowlists, etc.)

## 🛡️ Data Privacy

### Screenshot Handling
- Screenshots are processed locally by default
- Cloud upload requires explicit user consent
- All cloud storage uses encryption at rest
- Automatic cleanup of temporary files

### Audio Processing
- Audio buffers are cleared after processing
- No persistent audio storage without consent
- Secure transmission to speech services
- Local fallback processing when possible

### User Data Protection
- Minimal data collection principle
- Anonymized logging by default
- User consent for any cloud features
- Transparent data usage policies

## 🔒 Development Security

### Code Security
- Input validation for all user commands
- Sanitization before external API calls
- Secure configuration management
- Regular dependency security updates

### Testing Security
- Mock APIs for development testing
- Separate test environment configurations
- No real API keys in test suites
- Automated security scanning

## 🚨 Incident Response

### If API Keys Are Compromised
1. **Immediately revoke** the compromised keys
2. **Generate new keys** and update configuration
3. **Review logs** for unauthorized usage
4. **Monitor accounts** for suspicious activity

### Reporting Security Issues
- Email security issues to: [security@heimdall-project.com]
- Use encrypted communication for sensitive reports
- Provide detailed reproduction steps
- Allow reasonable time for response before disclosure

## 📋 Security Checklist

### Before First Run
- [ ] API keys configured in `.env`
- [ ] `.env` file is gitignored
- [ ] AWS IAM permissions are minimal
- [ ] Local processing preferences set

### Regular Security Maintenance
- [ ] Update dependencies monthly
- [ ] Rotate API keys quarterly
- [ ] Review access logs
- [ ] Test backup and recovery procedures

### Production Deployment
- [ ] Use production-grade secrets management
- [ ] Enable comprehensive logging
- [ ] Set up monitoring and alerting
- [ ] Implement rate limiting
- [ ] Configure firewall rules

## 🔧 Configuration Security

### Environment Variables
```bash
# Good: Specific, minimal permissions
AWS_REGION=us-east-1
ENCRYPT_SCREENSHOTS=true
LOCAL_PROCESSING_ONLY=false

# Bad: Overly permissive or insecure
DEBUG_MODE=true  # Don't use in production
MOCK_APIS=false  # Ensure real security in production
```

### AWS Security
- Use IAM roles instead of access keys when possible
- Enable CloudTrail for audit logging
- Set up billing alerts for unusual usage
- Use VPC endpoints for private communication

## 📚 Additional Resources
- [OpenAI API Security Best Practices](https://platform.openai.com/docs/guides/safety-best-practices)
- [AWS Security Best Practices](https://aws.amazon.com/architecture/security-identity-compliance/)
- [ElevenLabs API Documentation](https://docs.elevenlabs.io/)
- [OWASP Security Guidelines](https://owasp.org/www-project-top-ten/)