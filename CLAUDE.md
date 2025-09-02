# CLAUDE.md - Ustad MCP Project (Intent-First Protocol)

## THE NEW RULE: UNDERSTAND BEFORE REASONING

```python
# For EVERY request, follow this order:
Step 1: intent = mcp__sequential-thinking("What does user REALLY need?")
Step 2: if needs_facts: mcp__tavily-search("verify: [claim]")  
Step 3: if complex: mcp__ustad-start() → mcp__ustad-think()
Step 4: else: just_answer_simply()
```

## Core Principles (YAGNI + SOLID)

### YAGNI (You Aren't Gonna Need It)
- Don't use 8 perspectives for "What's 2+2?"
- Don't build features users didn't ask for
- Don't over-engineer simple solutions
- Start with the minimum that works

### SOLID Applied to AI Reasoning
- **S**ingle Responsibility: Each tool does ONE thing well
- **O**pen/Closed: Extend capabilities, don't modify core behavior  
- **L**iskov: Tools are interchangeable when appropriate
- **I**nterface Segregation: Use only the tools you need
- **D**ependency Inversion: Depend on intent, not implementation

## Project Overview
**Ustad** - The Master Teacher MCP implementing collaborative AI wisdom through multi-round dialogue where perspectives debate and reach consensus.

> "Ustad" means "master/teacher" in Turkish/Urdu. This MCP teaches through collaborative dialogue.

## The Intent-First Workflow

### Step 1: Understand Intent (ALWAYS FIRST)
```python
# Use sequential thinking to classify complexity
intent_type = mcp__sequential-thinking("""
    Classify this request:
    - SIMPLE: Direct answer, definition, basic command
    - RESEARCH: Needs fact-checking or verification  
    - COMPLEX: Needs multiple perspectives/debate
    - BUILD: Needs implementation/coding
""")
```

### Step 2: Apply YAGNI - Choose Minimal Tool
```
SIMPLE (90% of requests) → Direct answer
├── Examples: "What's 2+2?", "Run ls", "Fix typo"
├── Time: <1 second
└── Tools: Basic tools only (Read, Edit, Bash)

RESEARCH (5% of requests) → Verify first
├── Examples: "How does async work?", "Latest React features?"
├── Time: 2-5 seconds  
└── Tools: tavily_search → then answer

COMPLEX (4% of requests) → Collaborative reasoning
├── Examples: "Architecture decision", "Debug weird issue"
├── Time: 10-30 seconds
└── Tools: ustad_start → ustad_think

BUILD (1% of requests) → Systematic work
├── Examples: "Implement feature", "Refactor codebase"
├── Time: Ongoing
└── Tools: TodoWrite → implement → test → commit
```

## Core Architecture

### Collaborative Intelligence (Used Only When Needed)
- **Multi-Round Dialogue**: 3-8 perspectives based on complexity
- **Challenge & Response**: Ideas tested through disagreement
- **Consensus Building**: Synthesis emerges from dialogue
- **Adaptive Reasoning**: Complexity determines approach

### Technical Stack
- Python 3.11+ with async/await
- OpenAI GPT-3.5-turbo for efficiency
- MCP protocol for Claude Code integration  
- Cost-optimized: ~$0.008 per complex analysis

## Project Structure
```
ustad/
├── src/
│   └── ustad/
│       ├── __init__.py
│       ├── perfect_collaborative_bot.py  # Core collaborative engine
│       ├── perfect_mcp_server.py         # Main MCP server
│       └── simple_mcp_server.py          # Simplified server
├── tests/
│   └── test_*.py
├── pyproject.toml
└── README.md
```

## Real-World Examples (YAGNI in Action)

### Example 1: Simple Question
```
User: "What's the capital of France?"
❌ WRONG: ustad_think() with 8 perspectives
✅ RIGHT: "Paris"
```

### Example 2: Research Question
```
User: "Does Python 3.12 have pattern matching?"
❌ WRONG: ustad_think() speculating
✅ RIGHT: tavily_search("Python 3.12 pattern matching") → "Yes, since 3.10"
```

### Example 3: Complex Problem (Rare)
```
User: "Should we migrate to microservices?"
❌ WRONG: Jump to answer without analysis
✅ RIGHT: ustad_think() → perspectives debate → consensus
```

### The Master's Teaching Process (When Actually Needed)
1. **Intent Analysis**: Use sequential_thinking first
2. **Complexity Assessment**: Is this genuinely complex?
3. **Tool Selection**: Choose minimal sufficient tool
4. **Execution**: Use selected approach
5. **Validation**: Did we over-engineer?

## Development Commands
```bash
# Run tests
pytest -v

# Run with coverage
pytest --cov=ustad --cov-report=term-missing

# Run the MCP server
python -m ustad.simple_mcp_server
```

## Anti-Patterns to Avoid

### ❌ Premature Collaboration
```python
# User: "Fix this typo"
# WRONG: 8 perspectives debate typography
# RIGHT: Edit(fix_typo)
```

### ❌ Speculation Without Research
```python
# User: "What's new in React 19?"
# WRONG: "I think React 19 might..."
# RIGHT: tavily_search("React 19 features")
```

### ❌ Over-Engineering Simple Tasks
```python
# User: "Add a console.log"
# WRONG: ustad_systematic() with 10 todos
# RIGHT: Edit(add_console_log)
```

## Project-Specific Context (Ustad)
- **Core Files**: perfect_collaborative_bot.py, perfect_mcp_server.py
- **Cost Target**: <$0.01 per analysis using GPT-3.5
- **Performance**: <5 seconds for simple, <30 seconds for complex
- **Testing**: TruthfulQA benchmark for hallucination reduction

## Decision Framework (KISS)

Ask yourself:
1. **Can I answer in one line?** → Just answer
2. **Do I need to verify a fact?** → tavily_search first
3. **Is this GENUINELY complex?** → ustad_think (rare)
4. **Am I over-engineering?** → Stop and simplify

## Philosophy

**YAGNI**: Don't build what isn't needed. 90% of requests need basic tools.

**SOLID**: Each tool has ONE job. Don't chain unnecessarily.

**KISS**: The simplest working solution wins.

---
*"The apprentice seeks complexity, the master finds simplicity."*

**Token Budget: This file uses ~500 tokens. Keep it lean.**