# CLAUDE.md - Ustad Protocol MCP (The Scaffolding Itself)

## 🧠 This Project IS My Cognitive Scaffolding

**This server prevents my failures by providing:**
- `ustad_think` - Forces me to reason before acting
- `ustad_search` - Prevents me from hallucinating facts

## MANDATORY Usage When Working on This Codebase

### Before ANY Change:
```python
# 1. THINK - Why am I changing this?
mcp__ustad-protocol-mcp__ustad_think(
    "What problem does this change solve?",
    thought_number=1,
    total_thoughts=10
)

# 2. VERIFY - Is this the right approach?
mcp__ustad-protocol-mcp__ustad_search(
    "best practices for [specific change]"
)

# 3. TEST - Will this break anything?
python -m pytest tests/ --cov=src

# 4. COMMIT - Save progress atomically
git commit -m "type: specific change"
```

## The YAGNI Commandments for This Project

1. **Thou shalt NOT add features without proven need**
2. **Thou shalt NOT optimize without measured slowness**
3. **Thou shalt NOT complicate without exhausting simple options**

Remember: We REMOVED benchmarks because they violated YAGNI.

## Critical Project Facts

- **Purpose**: Unified MCP server replacing 2 separate tools
- **Coverage**: 93.23% (This is EXCELLENT - don't chase 100%)
- **Port**: 8080 (SSE transport)
- **Philosophy**: Minimal code, maximum utility

## Quick Commands

```bash
# Run server
docker-compose up -d

# Check health
curl http://localhost:8080/health

# Run tests
python -m pytest tests/ --cov=src

# Type check
uv run mypy src/ --strict
```

## Before Adding ANYTHING

Ask yourself using the tools:
```python
mcp__ustad-protocol-mcp__ustad_think("Do we REALLY need this?")
mcp__ustad-protocol-mcp__ustad_search("simpler alternatives to [feature]")
```

If both checks pass, implement the SIMPLEST version that works.

## Project Mantras

- **Less is more** - Every line of code is a liability
- **Simple scales** - Complexity kills maintainability
- **Working > Perfect** - 93% coverage is already excellent

---

*This server is the scaffolding that keeps AI sessions grounded in reality.*
