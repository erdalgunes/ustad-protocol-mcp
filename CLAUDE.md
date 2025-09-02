# CLAUDE.md - Ustad MCP Project

## Project Overview
**Ustad** - The Master Teacher MCP implementing collaborative AI wisdom through multi-round dialogue where perspectives debate and reach consensus.

> "Ustad" means "master/teacher" in Turkish/Urdu. This MCP teaches through collaborative dialogue.

## Core Architecture

### Collaborative Intelligence
- **Multi-Round Dialogue**: 8 AI perspectives engage in structured debate
- **Challenge & Response**: Ideas are tested through disagreement
- **Consensus Building**: True synthesis emerges from dialogue
- **Adaptive Reasoning**: Problem complexity determines round count

### Technical Stack
- Python 3.11+ with async/await
- OpenAI GPT-3.5-turbo for efficient multi-perspective generation
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

## Usage

### In Claude Code
```
Use ustad_think to analyze: "How should we architect this microservices system?"
```

### The Master's Teaching Process
1. **Problem Analysis**: Understand complexity and context
2. **Perspective Generation**: 8 diverse viewpoints emerge
3. **Dialectic Exchange**: Ideas challenge and refine each other
4. **Consensus Formation**: Wisdom emerges from synthesis

## Development Commands
```bash
# Run tests
pytest -v

# Run with coverage
pytest --cov=ustad --cov-report=term-missing

# Run the MCP server
python -m ustad.simple_mcp_server
```

## Philosophy
The master doesn't just provide answers - it teaches through the process of collective reasoning. Each perspective is a voice in the dialogue, and wisdom emerges from their interaction.

---
*"The apprentice asks, the master guides, wisdom emerges from dialogue."*