# TODO

## Recent Updates (2025-09-03)

### ✅ Recently Fixed

- [x] **MyPy module name conflict** - Fixed with proper src layout configuration
  - Added mypy_path = "src" and packages = ["sequential_thinking"]
  - Verified with successful mypy --strict run
  - Committed atomically

### ✅ Project Uses uv (Not Poetry)

- [x] **uv.lock file** - Already present and maintained by uv
  - Project uses uv for dependency management (modern replacement for Poetry)
  - CI properly configured with uv commands
  - No poetry.lock needed - that was outdated information

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

## Next Session Opportunities

1. **Continue improvements**:

   ```bash
   # Run full test suite to verify all improvements
   uv run pytest tests/ -v --cov=. --cov-report=term-missing

   # Validate CI pipeline components
   python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"
   ```

1. **Optional enhancements** (following YAGNI):

   ```bash
   # Add performance benchmarks if needed
   # Enhance error handling patterns if gaps found
   # Consider additional security hardening if required
   ```

1. **Fix any remaining issues in cli_inspector.py**:

   - Complete the Pythonic refactoring
   - Add missing helper methods
   - Ensure all tests pass

## Known Limitations

### CI/CD Pipeline

- ✅ uv.lock is present and properly maintained
- ✅ Cross-platform testing configured (Ubuntu, macOS, Windows)
- ✅ Security tools properly configured and running

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
