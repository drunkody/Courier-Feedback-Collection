# Test Execution Guide

## Quick Start

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Test Categories

### Unit Tests
```bash
pytest -m unit -v
```

### Integration Tests
```bash
pytest -m integration -v
```

### Offline Tests
```bash
pytest -m offline -v
```

### Performance Tests
```bash
pytest -m performance -v
```

## Advanced Usage

### Parallel Execution
```bash
pytest -n auto # Use all CPU cores
pytest -n 4 # Use 4 workers
```

### Specific Test File
```bash
pytest tests/test_utils.py -v
```

### Specific Test Function
```bash
pytest tests/test_utils.py::TestQueueManager::test_add_to_empty_queue -v
```

### Failed Tests Only
```bash
pytest --lf # Last failed
pytest --ff # Failed first
```

### Verbose Output
```bash
pytest -vv # Very verbose
pytest -s # Show print statements
```

### Stop on First Failure
```bash
pytest -x
```

### Coverage Threshold
```bash
pytest --cov=app --cov-fail-under=80
```

## Test Markers

Available markers:
- `unit` - Unit tests
- `integration` - Integration tests
- `slow` - Slow running tests
- `offline` - Offline mode tests
- `database` - Database tests
- `api` - API endpoint tests
- `state` - State management tests
- `security` - Security tests
- `performance` - Performance tests

## Continuous Integration

Tests run automatically on:
- Push to main/develop
- Pull requests
- Python versions: 3.10, 3.11, 3.12

## Coverage Goals

- Overall: 80%+
- Critical paths: 95%+
- Utils: 90%+
- Services: 85%+
- API routes: 80%+

## Writing New Tests

### Test File Template

```python
"""Tests for [module]."""
import pytest

class Test[FeatureName]:
"""Tests for [feature]."""

def test_[specific_behavior](self, fixture):
"""Test that [behavior description]."""
# Arrange
data = {...}

# Act
result = function(data)

# Assert
assert result == expected
```

### Best Practices

1. **Arrange-Act-Assert** pattern
2. **One assertion per test** (when possible)
3. **Descriptive test names**
4. **Use fixtures** for setup
5. **Mock external dependencies**
6. **Test edge cases**
7. **Test error conditions**

## Troubleshooting

### Database Lock Errors
```bash
# Use separate test database
export DATABASE_URL="sqlite:///test.db"
pytest
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt -r requirements-test.txt
```

### Slow Tests
```bash
# Skip slow tests
pytest -m "not slow"
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Factory Boy](https://factoryboy.readthedocs.io/)
