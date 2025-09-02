# CLAUDE.md - Ustad Development Protocol v0.2.0

## Core Principle: Think Before Acting
Every request goes through collaborative analysis first. No exceptions.

---

## 🎯 Step 0: ALWAYS Start Session & Understand Intent

```
1. mcp__ustad-think__ustad_start     # Initialize session (MANDATORY)
2. mcp__ustad-think__ustad_think     # Analyze what user REALLY wants
```

### Example:
User: "Fix the auth bug"
```
→ ustad_start
→ ustad_think: "What auth bug? What system? What's the real goal?"
→ Then investigate
```

---

## 🔍 Step 1: Research Before Claiming

**For ANY technical task:**
```
mcp__tavily-mcp__tavily-search      # Research the domain
mcp__ustad-think__ustad_research    # Deep analysis
```

### Example:
User: "Implement Redis caching"
```
→ tavily_search: "Redis caching best practices 2025"
→ ustad_research: "Redis implementation patterns"
→ Then implement
```

---

## 🧠 Step 2: Think Before Coding

**For ANY implementation:**
```
mcp__ustad-think__ustad_think       # Multi-perspective analysis
mcp__sequential-thinking__sequentialthinking  # Step-by-step planning
TodoWrite                            # Track the plan
```

### Example:
User: "Add dark mode"
```
→ ustad_think: "How to implement dark mode properly?"
→ sequentialthinking: Break down into steps
→ TodoWrite: Track each component
```

---

## 🛠️ Step 3: Systematic Execution

**For complex tasks:**
```
mcp__ustad-think__ustad_systematic  # Methodical execution
TodoWrite                            # Update progress
git commit                           # Checkpoint each step
```

### Example:
Building a feature:
```
→ ustad_systematic: Plan and execute
→ TodoWrite: Mark progress
→ git commit -m "feat: add component X"
```

---

## 🔄 Step 4: Handle Errors Properly

**When things go wrong:**
```
mcp__ustad-think__ustad_think       # Analyze the error
mcp__tavily-mcp__tavily-search      # Research solutions
TodoWrite                            # Add as task, don't abandon
```

### Example:
Error occurs:
```
→ ustad_think: "Why did this fail?"
→ tavily_search: "Error: [specific error message]"
→ TodoWrite: "Fix: [specific solution]"
→ Try multiple approaches before giving up
```

---

## 📊 Step 5: Validate Before Claiming Success

**After implementation:**
```
mcp__ustad-think__ustad_preflight   # Check for issues
Test the code                        # Actually run it
git status/diff                      # Verify changes
```

---

## Practical Workflow Examples

### Example 1: Bug Fix
```bash
# User: "There's a memory leak in the session handler"

1. ustad_start                       # Initialize
2. ustad_think: "What's causing the memory leak?"
3. Grep: "session" -n                # Find session code
4. Read: session_handler.py          # Examine code
5. ustad_think: "How to fix this leak?"
6. Edit: Add cleanup code
7. git commit -m "fix: session memory leak"
```

### Example 2: New Feature
```bash
# User: "Add CSV export functionality"

1. ustad_start                       # Initialize
2. ustad_think: "CSV export requirements?"
3. tavily_search: "Python CSV export best practices"
4. ustad_systematic: Plan implementation
5. TodoWrite: [Create, Format, Export, Test]
6. Implement each todo item
7. git commit (atomic commits)
```

### Example 3: Refactoring
```bash
# User: "This code is messy, refactor it"

1. ustad_start                       # Initialize
2. Read: messy_code.py               # Understand current state
3. ustad_think: "What patterns should we apply?"
4. sequentialthinking: Plan refactoring steps
5. TodoWrite: Track each refactoring
6. MultiEdit: Apply changes
7. Test and commit
```

---

## Quick Decision Tree

```
Complex problem?
  → ustad_think (analyze with 8 perspectives)

Need information?
  → tavily_search (get facts first)

Multiple steps?
  → sequentialthinking + TodoWrite

Stuck on error?
  → ustad_think + tavily_search (don't give up)

Before committing?
  → ustad_preflight (check for issues)
```

---

## Tool Combinations That Work

### Research + Think
```python
tavily_search("topic") → ustad_think("analyze findings")
```

### Think + Plan + Do
```python
ustad_think("approach") → TodoWrite(steps) → Execute
```

### Debug + Fix
```python
ustad_think("error analysis") → tavily_search("solution") → Edit
```

---

## Development Rules

1. **ALWAYS start with ustad_start** - No exceptions
2. **Think before acting** - ustad_think for any non-trivial task
3. **Research before claiming** - tavily_search for any technical claim
4. **Plan before coding** - TodoWrite for multi-step tasks
5. **Commit atomically** - git commit after each logical change
6. **Don't abandon on errors** - Add to TodoWrite and try 3 approaches

---

## Available Tools Reference

### Thinking Tools
- `mcp__ustad-think__ustad_start` - Initialize (ALWAYS FIRST)
- `mcp__ustad-think__ustad_think` - 8-perspective analysis
- `mcp__ustad-think__ustad_quick` - 3-perspective for simple problems
- `mcp__ustad-think__ustad_systematic` - Methodical execution
- `mcp__sequential-thinking__sequentialthinking` - Step-by-step reasoning

### Research Tools
- `mcp__tavily-mcp__tavily-search` - Web search
- `mcp__ustad-think__ustad_research` - Deep research analysis

### Execution Tools
- `TodoWrite` - Task management
- `Read`, `Edit`, `MultiEdit` - File operations
- `Bash` - Command execution
- `git` - Version control

---

## Success Metrics

Track these in every session:
- [ ] Started with ustad_start?
- [ ] Understood intent before acting?
- [ ] Researched before implementing?
- [ ] Created TodoWrite plan?
- [ ] Committed atomically?
- [ ] Handled errors without abandoning?

---

## Simple Test Cases

### Test 1: Simple Fix
"Fix the typo in README"
- Should: Read → Edit → Commit
- Not: ustad_think (too simple)

### Test 2: Complex Feature
"Add authentication system"
- Should: ustad_start → ustad_think → research → systematic → todos
- Not: Jump straight to coding

### Test 3: Debug Error
"Function returns undefined"
- Should: ustad_think → investigate → multiple solutions
- Not: Give up after first attempt

---

*"Simplicity is the ultimate sophistication. Start with thinking, always."*