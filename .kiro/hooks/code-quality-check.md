# Code Quality Check Hook

## Trigger
- **Event**: File Save
- **File Pattern**: `**/*.py`
- **Description**: Automatically run code quality checks when Python files are saved

## Actions

### 1. Linting with flake8
```bash
flake8 {file_path} --max-line-length=100 --ignore=E203,W503
```

### 2. Type Checking with mypy
```bash
mypy {file_path} --ignore-missing-imports
```

### 3. Import Sorting with isort
```bash
isort {file_path} --check-only --diff
```

### 4. Code Formatting Check with black
```bash
black {file_path} --check --diff
```

## Success Actions
- Display green checkmark in status bar
- Log successful quality check

## Failure Actions
- Show inline error highlights
- Display detailed error messages
- Suggest auto-fix options where available

## Configuration
```json
{
  "enabled": true,
  "auto_fix": false,
  "show_notifications": true,
  "exclude_patterns": ["**/tests/**", "**/migrations/**"]
}
```