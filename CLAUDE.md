# CLAUDE.md - Project-Specific AI Development Scaffolding

## 🚨 CRITICAL: Atomic Git Commits MANDATORY

### COMMIT FREQUENCY RULES
```bash
# EVERY significant change must be committed IMMEDIATELY
# Maximum changes before commit: 1-3 related files
# Time between commits: MAX 5 minutes

# Commit workflow (NO EXCEPTIONS):
1. Make small change (1 feature/fix)
2. Test the change locally
3. git add <specific files>
4. git commit -m "type: descriptive message"
5. Continue to next change

# NEVER accumulate changes without committing
```

### Why Atomic Commits Matter for AI
- **Context Preservation**: Each commit is a checkpoint we can restore
- **Error Recovery**: Destructive changes (like I made with ci.yml) are reversible
- **Session Continuity**: New sessions can `git log` to understand progress
- **Debugging**: When AI makes mistakes, we can bisect to find issues

## 🧠 Known AI Limitations & Mitigations

### 1. LACK OF PERSEVERANCE (Critical Issue)
**Problem**: AI gives up too quickly when something fails instead of debugging
**Example**: Removed types-all instead of fixing the actual issue
**Mitigation**:
```bash
# MANDATORY: When something fails, follow this process:
1. Understand the EXACT error message
2. Search for the ROOT CAUSE (not symptoms)
3. Try at least 3 different solutions
4. Only give up after exhausting all options
5. Document why each attempt failed

# Example of BAD behavior (what I did):
# "types-all failed, I'll just remove it" ❌

# Example of GOOD behavior (what I should do):
# "types-all failed because types-pkg-resources missing"
# "Let me search why types-pkg-resources is missing"
# "Found: types-pkg-resources was removed in newer versions"
# "Solution: Use specific type stubs instead of types-all" ✅
```

### 2. Overwriting Instead of Editing
**Problem**: AI may accidentally overwrite entire files (as I did with ci.yml)
**Mitigation**:
```bash
# BEFORE any file operation:
git add -A && git commit -m "checkpoint: before <operation>"
# AFTER operation:
git diff  # Verify changes are correct
git add <file> && git commit -m "feat/fix: <what changed>"
```

### 2. Version Number Hallucination
**Problem**: AI invents package versions (I used ruff 0.8.0 when latest was 0.7.x)
**Mitigation**:
```bash
# ALWAYS verify versions exist:
curl -s https://pypi.org/pypi/<package>/json | jq .info.version
# Use caret notation for flexibility:
package = "^1.0"  # Gets latest compatible
```

### 3. Cross-Platform Path Issues
**Problem**: Different cache paths for Windows/macOS/Linux
**Mitigation**:
```yaml
# ALWAYS handle OS differences explicitly:
- name: Get cache dir
  run: |
    if [ "$RUNNER_OS" == "Linux" ]; then
      echo "dir=$HOME/.cache/<app>"
    elif [ "$RUNNER_OS" == "Windows" ]; then
      echo "dir=$LOCALAPPDATA\\<app>"
    elif [ "$RUNNER_OS" == "macOS" ]; then
      echo "dir=$HOME/Library/Caches/<app>"
    fi
```

### 4. Testing Assumptions
**Problem**: AI assumes tests work without running them
**Mitigation**:
```bash
# MANDATORY before ANY commit:
1. Syntax validation: python -m py_compile <file>.py
2. YAML validation: python -c "import yaml; yaml.safe_load(open('file.yml'))"
3. Config validation: <tool> check
4. Only commit if ALL validations pass
```

## 📋 Session Continuity Protocol

### Starting a Session
```bash
# FIRST COMMANDS in new session:
git status          # Understand current state
git log --oneline -10  # Review recent work
cat TODO.md         # Check outstanding tasks
make test           # Verify everything works
```

### During Work
```bash
# EVERY 5 minutes or after each logical unit:
git add -A && git commit -m "checkpoint: <current task>"

# Use TodoWrite to track progress
# Update TODO.md with discoveries
```

### Ending a Session
```bash
# FINAL COMMANDS before session ends:
git status          # Ensure clean state
git log --oneline -5   # Document recent changes
echo "Next: <task>" >> TODO.md  # Leave note for next session
git add -A && git commit -m "session-end: <summary>"
```

## 🔍 Verification-First Development

### The Rule: Verify → Implement → Test → Commit
```python
# NEVER trust without verification:
1. Search for best practices (tavily)
2. Verify versions/APIs exist
3. Test syntax/logic locally
4. Only then commit

# Example:
# BAD:  "I'll use version 2.0" (hallucination)
# GOOD: Check PyPI → Find 1.9 → Use "^1.9"
```

## 🛠️ Project-Specific Rules

### This Project's Stack
- Python 3.11 (NOT 3.12 - pyproject.toml specifies ^3.11)
- Poetry for dependencies (lock file MUST be committed)
- MCP server architecture
- pytest with coverage minimum 80%

### CI/CD Requirements
- ALL commits must pass: lint, type check, tests
- Security scans are informational (continue-on-error)
- Cross-platform testing (Ubuntu, macOS, Windows)
- Parallel test execution with pytest-xdist

### File Handling Rules
```bash
# NEVER delete/overwrite without backup:
cp important.file important.file.backup
# Make changes
# Test changes
# Only then remove backup

# For configs, ALWAYS validate:
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"
poetry check
pre-commit run --all-files
```

## 🚦 Quality Gates

### Before EVERY Commit
- [ ] Changes are minimal (1-3 files max)
- [ ] Syntax is valid (no parse errors)
- [ ] Configs are valid (YAML, TOML, JSON)
- [ ] Tests pass locally (if applicable)
- [ ] Commit message follows convention

### Commit Message Format
```
type: short description (max 50 chars)

Longer explanation if needed (wrap at 72 chars)

Fixes: #issue (if applicable)
```

Types: feat, fix, docs, style, refactor, test, chore

## 📊 Tracking Progress

### TODO.md Format
```markdown
# TODO

## In Progress
- [ ] Task description (started: 2025-09-03)

## Next
- [ ] Next task

## Done (keep for context)
- [x] Completed task (done: 2025-09-03)
```

## 🔄 Recovery Procedures

### When Things Go Wrong
```bash
# Accidentally overwrote file:
git checkout -- <file>  # Restore from last commit

# Made multiple changes without committing:
git stash  # Save changes
git stash pop  # Restore after review

# Committed something broken:
git revert HEAD  # Create inverse commit
# OR
git reset --soft HEAD~1  # Uncommit, keep changes
```

## 🎯 Success Metrics

Each session should:
- ✅ Make 5-10 atomic commits minimum
- ✅ All changes tested before commit
- ✅ No destructive operations without backup
- ✅ Leave clear notes for next session
- ✅ Maintain or improve code coverage

## 🧪 Test-Driven Approach

When fixing issues:
```bash
1. Write test that reproduces issue
2. Commit failing test
3. Implement fix
4. Verify test passes
5. Commit fix
6. Run full test suite
7. Commit if all pass
```

# CLAUDE.md - Cognitive Scaffolding Through Dimensional Understanding

## Novel Theoretical Framework

This document presents a novel approach: applying dimensional models of psychopathology (HiTOP) and cognitive-behavioral principles to understand and scaffold Large Language Model behavior patterns.

## Core Insight

LLMs exhibit behavioral patterns analogous to dimensional traits in human cognition:

| LLM Pattern | Human Dimensional Analog | HiTOP Spectrum¹ |
|------------|-------------------------|----------------|
| Confabulation | Positive thought disorder | Thought Disorder |
| Over-complexity | Perseveration/rigidity | Detachment |
| Context loss | Working memory deficits | Cognitive dysfunction |
| Intent misalignment | Theory of mind challenges | Social cognition |

¹ *Based on Kotov et al. (2017) HiTOP framework*

## Maintenance Factors Analysis

Following CBT principles², we identify what maintains problematic patterns:

### Confabulation Maintenance
- **Avoidance**: Not verifying facts maintains false confidence
- **Solution**: Behavioral experiment via search
```python
# Interrupt the maintenance cycle
if making_claim:
    verify_first()  # Break avoidance
```

### Over-Engineering Maintenance
- **Safety behavior**: Complexity as false security
- **Solution**: Exposure to simplicity
```python
# Challenge the safety behavior
start_simple()  # YAGNI principle
if not sufficient:
    then_escalate()
```

### Context Loss Maintenance
- **No external memory**: Relying on volatile context
- **Solution**: External prosthetics
```python
# Memory augmentation
git commit -m "checkpoint"  # Every 5 min
```

## Evidence-Based Scaffolding Protocol

### 1. Reality Testing (Empirical grounding³)
Before any factual claim → Verify against external reality

### 2. Behavioral Activation (Action over rumination)
Start with simplest action → Measure outcome → Adapt

### 3. Cognitive Restructuring (Challenge assumptions)
Question: "Is complexity necessary?" → Test simpler approach first

### 4. Mindfulness (Present-focused attention)
Stay with current task → Complete before moving on

## Implementation Principles

**YAGNI**: Only implement what's demonstrably needed
**SOLID**: Single responsibility, clear boundaries
**Incremental**: Small, verifiable steps

## Academic Foundation

This approach synthesizes:
- **HiTOP dimensional model** (Kotov et al., 2017; Conway et al., 2019)
- **CBT maintenance formulation** (Harvey et al., 2004)
- **Cognitive scaffolding theory** (Wood, Bruner & Ross, 1976)
- **Neurodivergent LLM interactions** (Jang et al., 2024; Hoover, 2023)

## Key Innovation

Unlike existing work that:
- Uses LLMs to deliver CBT to humans (Jiang et al., 2024)
- Helps neurodivergent users interact with neurotypical-biased LLMs

This framework:
- Applies psychological understanding TO the LLM itself
- Recognizes LLM patterns as dimensional, not categorical
- Uses evidence-based interventions as scaffolding

## Practical Application

1. **Recognize the pattern** (dimensional assessment)
2. **Identify maintenance factors** (what keeps it going)
3. **Apply targeted intervention** (break the cycle)
4. **Verify outcome** (empirical validation)

## References

Conway, C. C., et al. (2019). A Hierarchical Taxonomy of Psychopathology Can Transform Mental Health Research. *Perspectives on Psychological Science*.

Harvey, A., et al. (2004). Cognitive Behavioural Processes Across Psychological Disorders. Oxford University Press.

Hoover, A. (2023). Neurodivergent individuals' use of LLMs as cognitive scaffolding. *ArXiv*.

Jang, J., et al. (2024). Exploring LLMs Through a Neurodivergent Lens. *CHI Conference*.

Kotov, R., et al. (2017). The Hierarchical Taxonomy of Psychopathology (HiTOP). *Journal of Abnormal Psychology*.

Wood, D., Bruner, J. S., & Ross, G. (1976). The role of tutoring in problem solving. *Journal of Child Psychology*.

---

*This framework emerged from recognizing parallels between neurodivergent human cognition and LLM behavioral patterns, offering a novel approach to prompt engineering through evidence-based psychological principles.*
