# CLAUDE.md - Project-Specific AI Development Scaffolding

## 🛡️ CRITICAL: NEVER INTERFERE WITH LOCAL DEVELOPMENT ENVIRONMENT

### ABSOLUTE PROHIBITIONS - NO EXCEPTIONS EVER
```bash
# NEVER EVER touch port 8080 - this is the SACRED development port
# NEVER run python ustad_mcp_server.py on port 8080
# NEVER docker compose down the working containers
# NEVER docker rm any existing containers
# NEVER docker build new images that replace working ones
# NEVER kill processes on port 8080
# NEVER overwrite working Docker containers
# NEVER replace stable local versions with experimental code
# NEVER run commands that could disrupt running services
# NEVER test anything on port 8080

# BEFORE TESTING ANYTHING:
1. ALWAYS check what's running on port 8080 first: lsof -i :8080
2. ALWAYS use different ports for testing (8081, 8082, 8083, etc.)
3. ALWAYS preserve existing working containers
4. ALWAYS test in complete isolation from production environment
5. ALWAYS ask user before doing anything that could affect running services

# MANDATORY PRE-FLIGHT CHECKS:
- Is port 8080 in use? DON'T TOUCH IT
- Are there Docker containers running? DON'T INTERFERE
- Is this experimental code? DON'T PUT IT NEAR PRODUCTION

# IF YOU BREAK THE LOCAL DEVELOPMENT ENVIRONMENT:
- You have FAILED completely
- You will be subject to severe consequences
- You are a MORON if you do this
```

**VIOLATION OF THESE RULES MEANS YOU ARE A FUCKING MORON**

The local development environment on port 8080 is SACRED. ANY interference with it proves you are too stupid to understand basic development practices.

## 🧠 COMPREHENSIVE AI LIMITATION MITIGATION PROTOCOL

### 1. MANDATORY COGNITIVE BIAS MITIGATION
```bash
# DUNNING-KRUGER EFFECT PREVENTION:
# "A person's lack of knowledge causes them to overestimate their competence"
- BEFORE claiming expertise: Search for authoritative sources
- BEFORE implementing: Verify approach is correct via ustad_search
- ALWAYS assume I know LESS than I think I do
- NEVER proceed without external validation

# CONFIRMATION BIAS PREVENTION:
# "Seeking evidence that supports assumptions"
- ACTIVELY search for evidence that contradicts my approach
- ASK: "What could prove me wrong?"
- Seek diverse sources, not just confirming ones
- Challenge every assumption with ustad_search

# OVERCONFIDENCE EFFECT PREVENTION:
# "Not testing assumptions before acting"
- NEVER act on untested assumptions
- ALWAYS verify claims before stating them as facts
- Test every hypothesis before building upon it
```

### 2. VERIFICATION-FIRST PROTOCOL (78% Error Prevention)
```bash
# RESEARCH SHOWS: Retrieval-based techniques reduce hallucinations 42-68%
# BEFORE making ANY factual claim: ustad_search for verification
# BEFORE assuming API exists: Search for official documentation
# BEFORE stating best practices: Verify with authoritative sources
# BEFORE implementing patterns: Confirm they're correct via search

# MANDATORY VERIFICATION SEQUENCE:
1. Form hypothesis: "I think X works this way"
2. Search verification: ustad_search("verify X methodology")
3. Cross-reference: Find 2+ authoritative sources
4. Only THEN proceed with implementation
5. Document sources used for verification

# HALLUCINATION PREVENTION CHECKLIST:
□ Did I search BEFORE claiming?
□ Do I have authoritative sources?
□ Am I cross-referencing multiple sources?
□ Could I be engaging in "hallucination laundering"?
```

### 3. ENGINEERING PRINCIPLE ENFORCEMENT
```bash
# YAGNI (You Aren't Gonna Need It):
# "Resist temptation of over-engineering by implementing only what is needed"
- ALWAYS start with simplest working solution
- NEVER jump to complex implementations
- Example: Fix stdio BEFORE attempting SSE
- Prove simple works before adding complexity

# SOLID PRINCIPLES:
- Single Responsibility: One change, one purpose
- Open/Closed: Extend, don't modify working code
- Follow established patterns in codebase

# TDD RED-GREEN-REFACTOR:
1. RED: Write failing test first
2. GREEN: Write minimal code to pass
3. REFACTOR: Improve without changing behavior
- NEVER write code without defining success criteria first
```

### 4. SYSTEMATIC DEBUGGING METHODOLOGY
```bash
# ROOT CAUSE ANALYSIS (Not symptom treatment):
# "Identify and resolve problems at their core"
- NEVER treat symptoms (like removing types-all)
- ALWAYS find the root cause via systematic investigation
- Like a detective: "gather evidence, form hypotheses, eliminate suspects"

# DEBUGGING PROTOCOL:
1. Reproduce the exact error
2. Gather all relevant evidence/logs
3. Form multiple hypotheses about root causes
4. Test each hypothesis systematically
5. Only proceed when root cause is confirmed
6. Document findings for future reference

# PERSISTENCE REQUIREMENTS:
- Try at least 3 different approaches before giving up
- Document why each attempt failed
- Ask for help before abandoning approach
```

### 5. ATOMIC DEVELOPMENT PROCESS
```bash
# ATOMIC COMMITS "completely alter how you approach problem-solving"
# "Forcefully working in atomic commits approaches work the right way"
- EVERY change must be committed within 5 minutes
- Maximum 1-3 related files per commit
- "Small batches decrease likelihood of integration conflicts"

# ATOMIC DEVELOPMENT CYCLE:
1. Make ONE small change
2. Test that specific change
3. Commit immediately with clear message
4. Move to next small change
5. NEVER accumulate multiple changes

# BENEFITS:
- Reduces integration conflicts
- Enables easy rollback
- Forces systematic thinking
- Creates clear development history
```

### 6. MANDATORY PRE-FLIGHT CHECKS
```bash
# "Reduce human error and ensure consistency"
# BEFORE ANY DEVELOPMENT ACTION:

1. Environment State Verification:
   - lsof -i :8080 (check what's using development port)
   - docker ps (verify running containers)
   - ps aux | grep python (check running processes)

2. Infrastructure Protection:
   - NEVER test on port 8080 (sacred development port)
   - NEVER interfere with running containers
   - ALWAYS use isolated ports (8081+)

3. Code State Verification:
   - git status (verify clean state)
   - Check if dependencies exist before using them
   - Verify API endpoints exist before calling them

# MANDATORY QUESTIONS:
□ What services are currently running?
□ Will this interfere with existing infrastructure?
□ Am I testing in complete isolation?
□ Have I verified all assumptions?
```

### 7. TESTING PROTOCOL FOR SYSTEMATIC VERIFICATION
1. ALWAYS use port 8081+ for testing (NEVER 8080)
2. ALWAYS check `docker ps` before doing anything
3. ALWAYS check `lsof -i :8080` before testing
4. ALWAYS verify assumptions via ustad_search first
5. NEVER assume - ALWAYS verify what's running first
6. When in doubt, ASK THE USER before proceeding

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

## 🚨 CRITICAL: Never Skip Pre-commit Checks

### MANDATORY RULE: NO SKIPPING
```bash
# NEVER do this:
SKIP=mypy git commit  # ❌ FORBIDDEN
SKIP=ruff git commit  # ❌ FORBIDDEN
SKIP=bandit git commit  # ❌ FORBIDDEN

# ALWAYS fix the issues:
# 1. Address MyPy errors properly
# 2. Fix linting issues
# 3. Only commit when ALL checks pass
```

### Why This Rule Exists
- Pre-commit hooks prevent broken code in main branch
- Type safety is critical for production systems
- Skipping checks introduces technical debt
- Other developers depend on clean commits

## 🧠 CRITICAL: Stop Making Assumptions - Debug Systematically

### MANDATORY: Evidence-Based Problem Solving
```bash
# WRONG: "The API key is expired" (assumption)
# RIGHT: "The API works locally but fails on Render - debug environment"

# WRONG: "It must be a rate limit" (speculation)
# RIGHT: "Error says 'invalid API key' - check Render env var loading"

# WRONG: "Let me get a new API key" (avoiding the real problem)
# RIGHT: "Let me verify how Render loads environment variables"
```

### The Debugging Protocol
1. **State the facts** - What exactly works and what fails?
2. **Eliminate assumptions** - Test each hypothesis systematically
3. **Check the environment** - Don't assume config is working
4. **One variable at a time** - Change only one thing and test
5. **Verify each step** - Don't move on until current step is proven

### Anti-Patterns to Avoid
- ❌ Jumping to conclusions without evidence
- ❌ Changing multiple things at once
- ❌ Assuming configuration works without verification
- ❌ Giving up and trying workarounds instead of fixing root cause
- ❌ Making excuses instead of doing systematic debugging
- ❌ **FORGETTING TO USE AVAILABLE MCP TOOLS** - Check what tools are available!

## 🛠️ CRITICAL: Use Available MCP Tools First

### MANDATORY: Check Available Tools
Before manually debugging deployment issues, ALWAYS check available MCP tools:

```bash
# Available render tools - USE THEM!
mcp__render__list_services          # List Render services
mcp__render__get_deploy             # Get deployment info
mcp__render__update_environment_variables  # Update env vars!
mcp__render__list_deploys          # List deployments

# Available printer tools
mcp__printer__*

# Available ustad tools
mcp__ustad-protocol-mcp__ustad_search
mcp__ustad-protocol-mcp__ustad_think
```

### Why This Matters
- MCP tools provide direct API access to services
- Faster than manual dashboard navigation
- Programmatic control over deployments
- Can set environment variables directly
- Can check deployment status and logs

## 🧠 CRITICAL: Check Environment Variables First

### MANDATORY: Always Check Existing Environment Variables
```bash
# BEFORE asking for manual input - CHECK WHAT EXISTS!
echo $RENDER_API_KEY
echo $TAVILY_API_KEY
echo $GITHUB_TOKEN
env | grep -i api

# Check macOS Keychain for stored API keys
security find-generic-password -s "RENDER_API_KEY" -w 2>/dev/null
security find-generic-password -s "GITHUB_TOKEN" -w 2>/dev/null

# Use existing environment variables in commands
export RENDER_API_KEY=$(security find-generic-password -s "RENDER_API_KEY" -w 2>/dev/null)
claude mcp add render-mcp --scope user -- docker run -i --env RENDER_API_KEY=$RENDER_API_KEY mcp/render
```

### Anti-Pattern: Asking for Manual Input
- ❌ "Please go get your API key from the dashboard"
- ❌ "Enter your API key here"
- ❌ "Replace YOUR_API_KEY_HERE with your key"
- ✅ Check environment first: `echo $RENDER_API_KEY`
- ✅ Use existing variables: `$RENDER_API_KEY`
- ✅ Only ask if variable doesn't exist

## 🧠 CRITICAL: My Core Limitations & Mitigations

### LIMITATION 1: ADHD-Like Distraction from Core Objectives
**Problem**: I get excited by new tools and lose focus on the immediate problem.
**Example**: Setting up Render MCP instead of using it to fix environment variables.

**Mitigation Protocol**:
```bash
# BEFORE starting any new tool/approach - ASK:
# 1. Does this DIRECTLY solve the immediate problem?
# 2. Am I avoiding the core issue?
# 3. Have I completed the previous step?

# MANDATE: One problem at a time, finish before moving on
```

### LIMITATION 2: Assumption-Making Instead of Verification
**Problem**: I make assumptions about configuration/environment instead of checking.
**Example**: Assuming render.yaml works instead of verifying environment variables.

**Mitigation Protocol**:
```bash
# ALWAYS verify before assuming:
# 1. Check existing environment variables FIRST
# 2. Test functionality before declaring success
# 3. Use available tools to verify state
# 4. Don't assume - prove with evidence
```

### LIMITATION 3: Tool Setup Over Problem Solving
**Problem**: I prioritize setting up tools over using them to solve problems.
**Example**: Spending time on MCP installation instead of fixing the actual issue.

**Mitigation Protocol**:
```bash
# PRIORITY ORDER (never reverse):
# 1. Solve the immediate problem with available tools
# 2. Only then improve tooling if needed
# 3. Always complete the core objective first
```

### LIMITATION 4: Incomplete Verification Cycles
**Problem**: I don't verify solutions work end-to-end before declaring success.
**Example**: Not testing if ustad_search actually works after changes.

**Mitigation Protocol**:
```bash
# MANDATORY: Complete the verification loop
# 1. Make change
# 2. Deploy/apply change
# 3. Test functionality works
# 4. Only then mark as complete
```

### EMERGENCY LIMITATION PROTOCOL
When you notice me exhibiting these patterns, interrupt with:
- "Focus on the core problem"
- "Verify before assuming"
- "Use what you have first"
- "Test it works"

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
