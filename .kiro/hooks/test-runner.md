# Automated Test Runner Hook

## Trigger
- **Event**: File Save
- **File Pattern**: `src/**/*.py`
- **Description**: Run relevant tests when core modules are modified

## Actions

### 1. Identify Related Tests
```python
# Map source files to test files
file_to_tests = {
    "src/core/voice_handler.py": ["tests/test_voice_handler.py"],
    "src/core/screen_analyzer.py": ["tests/test_screen_analyzer.py"],
    "src/core/intent_parser.py": ["tests/test_intent_parser.py"]
}
```

### 2. Run Unit Tests
```bash
pytest {related_test_files} -v --tb=short
```

### 3. Run Integration Tests (if core component)
```bash
pytest tests/integration/ -k {component_name} -v
```

### 4. Coverage Report
```bash
pytest {related_test_files} --cov={source_file} --cov-report=term-missing
```

## Success Actions
- Show test results in output panel
- Display coverage percentage
- Green status indicator

## Failure Actions
- Highlight failing tests
- Show detailed error messages
- Suggest debugging steps

## Configuration
```json
{
  "enabled": true,
  "run_integration_tests": true,
  "show_coverage": true,
  "auto_open_failures": true,
  "parallel_execution": true
}
```