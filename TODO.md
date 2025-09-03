# TODO

## Critical Issues Found (2025-09-03)

### ❌ Missing (MUST HAVE)

- [ ] **poetry.lock file** - Required for reproducible builds
  - Run `poetry lock` locally
  - Commit the file
  - CI will fail without it

### ⚠️ Version Issues

- [x] Fixed: Ruff version in pyproject.toml (was 0.8.0, now ^0.7)
- [x] Fixed: pytest-xdist version (was 3.5.0, now ^3.6)
- [x] Fixed: Other package versions to use caret notation

### ✅ Completed

- [x] CI/CD pipeline with all checks (2025-09-03)
- [x] Pre-commit hooks configuration
- [x] Cross-platform testing (Ubuntu, macOS, Windows)
- [x] Security scanning (Bandit, pip-audit, safety)
- [x] Branch protection documentation
- [x] Dependabot configuration
- [x] Project-specific CLAUDE.md for AI scaffolding

### 🔧 Configuration Issues

- [x] Fixed: Poetry cache paths for different OS
- [x] Added: Concurrency control to cancel duplicate CI runs
- [x] Added: Timeout settings for all jobs
- [x] Added: Parallel test execution with pytest-xdist

## Next Session Should

1. **Generate real poetry.lock**:

   ```bash
   poetry lock --no-update
   git add poetry.lock
   git commit -m "chore: add poetry.lock for reproducible builds"
   ```

1. **Test the CI pipeline**:

   ```bash
   # Validate all YAML files
   python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"

   # Run pre-commit hooks
   pre-commit run --all-files

   # Test locally with act (if available)
   act -n  # Dry run
   ```

1. **Fix any remaining issues in cli_inspector.py**:

   - Complete the Pythonic refactoring
   - Add missing helper methods
   - Ensure all tests pass

## Known Limitations

### CI/CD Pipeline

- poetry.lock is missing (CI will fail)
- Tests might fail on Windows due to path issues
- Some security tools might need configuration

### Code Quality

- cli_inspector.py refactoring incomplete
- Missing some helper methods referenced in refactored code
- No actual tests written yet for the inspector

## Project Structure

```
.
├── .github/
│   ├── workflows/
│   │   ├── ci.yml          # Main CI pipeline
│   │   └── release.yml     # Release automation
│   ├── branch-protection.md # Protection rules
│   └── dependabot.yml      # Dependency updates
├── src/
│   └── cli_inspector.py    # Partially refactored
├── tests/
│   └── (various test files)
├── .gitignore              # Proper Python gitignore
├── .pre-commit-config.yaml # Pre-commit hooks
├── CLAUDE.md               # AI development guide
├── Makefile                # Dev commands
├── pyproject.toml          # Project config
├── SECURITY.md             # Security policy
└── TODO.md                 # This file
```

## Session Notes

### 2025-09-03 Session Discoveries

- Ruff latest version is 0.7.x, not 0.8.x
- Poetry cache paths differ by OS
- Windows needs special handling in CI
- Must commit atomically to prevent data loss
- AI can hallucinate package versions
- Always verify before implementing

## Commands for Quick Start

```bash
# Start new session with:
git status
git log --oneline -10
cat TODO.md
make lint  # If poetry is installed

# Before making changes:
git add -A && git commit -m "checkpoint: before changes"

# After session:
git add -A && git commit -m "session-end: <what was done>"
```
