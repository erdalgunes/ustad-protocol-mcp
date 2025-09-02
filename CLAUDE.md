# CLAUDE.md - Batch of Thought MCP Project

## Project Overview
Python-based MCP server implementing Batch of Thought (BoT) for chess analysis to beat Stockfish using the Quetiapine Protocol.

## Development Principles

### 1. Test-Driven Development (TDD)
- **Red**: Write failing test first
- **Green**: Write minimal code to pass
- **Refactor**: Improve code while keeping tests green
- **Commit**: After each cycle with descriptive message

### 2. Python Best Practices
- Use type hints everywhere
- Follow PEP 8
- Use dataclasses for data structures
- Async/await for MCP server
- Poetry for dependency management

### 3. Batch of Thought Implementation
- Generate multiple thought chains in parallel
- Evaluate thoughts using scoring functions
- Select best thought path
- Apply to chess position analysis

### 4. Testing Strategy
- pytest for test framework
- pytest-asyncio for async tests
- pytest-cov for coverage (aim for >90%)
- Mock external dependencies (Stockfish)

### 5. Git Commit Strategy
Each commit should follow this pattern:
```
feat|fix|test|refactor: brief description

- What was done
- Why it was done
- Test coverage status
```

### 6. Project Structure
```
batch-of-thought-mcp/
├── src/
│   └── bot_mcp/
│       ├── __init__.py
│       ├── bot_engine.py      # Batch of Thought core
│       ├── chess_analyzer.py  # Chess-specific logic
│       ├── mcp_server.py      # MCP server implementation
│       └── models.py          # Data models
├── tests/
│   ├── test_bot_engine.py
│   ├── test_chess_analyzer.py
│   └── test_mcp_server.py
├── pyproject.toml
└── README.md
```

### 7. BoT Algorithm for Chess
1. **Thought Generation**: Generate N diverse move sequences
2. **Parallel Evaluation**: Evaluate each thought chain
3. **Scoring**: Score based on:
   - Material advantage
   - Positional strength
   - King safety
   - Development
   - Control
4. **Selection**: Choose best scoring thought
5. **Verification**: Validate against Stockfish baseline

### 8. MCP Tools to Implement
- `analyze_position`: Analyze chess position with BoT
- `generate_thoughts`: Generate thought chains for position
- `evaluate_move`: Evaluate specific move with BoT
- `compare_engines`: Compare BoT vs Stockfish

### 9. Testing Checklist
- [ ] Unit tests for each function
- [ ] Integration tests for MCP server
- [ ] Performance tests for BoT generation
- [ ] Comparison tests against Stockfish

### 10. Performance Goals
- Generate 10+ thought chains in <100ms
- Beat Stockfish level 5 in 50% of positions
- Memory usage <100MB per analysis

## Commands
```bash
# Run tests
pytest -v

# Run with coverage
pytest --cov=bot_mcp --cov-report=term-missing

# Run specific test
pytest tests/test_bot_engine.py -k test_name

# Format code
black src tests
isort src tests

# Type check
mypy src
```

## Remember
- Every feature starts with a test
- Commit after each test-implementation cycle
- Keep functions small and focused
- Document complex algorithms
- Profile performance bottlenecks