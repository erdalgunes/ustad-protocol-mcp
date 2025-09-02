# Sequential Thinking Implementation

A Pythonic implementation of Anthropic's MCP Sequential Thinking pattern for structured problem-solving through chain-of-thought reasoning.

## Overview

Sequential Thinking provides a flexible thinking process that can adapt and evolve as understanding deepens. Each thought can build on, question, or revise previous insights.

## Features

- **Chain-of-thought reasoning**: Break down complex problems into manageable steps
- **Revision capability**: Question and revise previous thoughts as needed
- **Branching support**: Explore alternative approaches in parallel
- **Dynamic adjustment**: Adjust total thoughts estimate as complexity becomes clearer
- **Completion detection**: Know when the thinking process is complete
- **Full history tracking**: Maintain complete context of the reasoning process

## Installation

```bash
# Install dependencies
pip install mcp pytest pytest-asyncio

# Run tests
pytest tests/test_sequential_thinking.py tests/test_mcp_integration.py -v
```

## Usage

### Basic Usage

```python
from src.sequential_thinking import SequentialThinkingServer

# Initialize server
server = SequentialThinkingServer()

# Process first thought
thought1 = {
    "thought": "Breaking down the problem into components",
    "thoughtNumber": 1,
    "totalThoughts": 5,
    "nextThoughtNeeded": True
}
result = server.process_thought(thought1)

# Continue with next thought
thought2 = {
    "thought": "Analyzing the first component in detail",
    "thoughtNumber": 2,
    "totalThoughts": 5,
    "nextThoughtNeeded": True
}
result = server.process_thought(thought2)

# Get summary
summary = server.get_summary()
print(f"Total thoughts: {summary['total_thoughts']}")
print(f"Complete: {summary['is_complete']}")
```

### Advanced Features

#### Revising Previous Thoughts

```python
# Revise a previous thought
revision = {
    "thought": "Actually, reconsidering my approach to component 1",
    "thoughtNumber": 3,
    "totalThoughts": 5,
    "isRevision": True,
    "revisesThought": 1,
    "nextThoughtNeeded": True
}
server.process_thought(revision)
```

#### Branching

```python
# Create a branch to explore alternative approach
branch = {
    "thought": "Alternative approach using different methodology",
    "thoughtNumber": 4,
    "totalThoughts": 6,
    "branchFromThought": 2,
    "branchId": "alternative-1",
    "nextThoughtNeeded": True
}
server.process_thought(branch)
```

#### Dynamic Adjustment

```python
# Realize we need more thoughts than initially estimated
adjustment = {
    "thought": "This is more complex, extending analysis",
    "thoughtNumber": 5,
    "totalThoughts": 10,  # Increased from 5
    "needsMoreThoughts": True,
    "nextThoughtNeeded": True
}
server.process_thought(adjustment)
```

### MCP Server Usage

The MCP server provides four tools:

1. **sequential_thinking**: Process individual thoughts
2. **get_thinking_summary**: Get session summary and statistics
3. **reset_thinking_session**: Reset for a fresh start
4. **get_thought_history**: View complete thought history

#### Running the MCP Server

```bash
# Run the MCP server
python src/sequential_thinking_mcp_server.py
```

#### MCP Configuration for Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "python",
      "args": [
        "/path/to/sequential_thinking_mcp_server.py"
      ]
    }
  }
}
```

## Testing

Comprehensive test coverage with TDD approach:

```bash
# Run unit tests
pytest tests/test_sequential_thinking.py -v

# Run integration tests
pytest tests/test_mcp_integration.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

## Design Principles

This implementation follows:

- **YAGNI (You Aren't Gonna Need It)**: Simple implementation without over-engineering
- **SOLID Principles**: Single responsibility per class/method
- **TDD (Test-Driven Development)**: Tests written before implementation
- **Atomic Commits**: Each feature committed separately

## Architecture

```
src/
├── sequential_thinking.py           # Core implementation
└── sequential_thinking_mcp_server.py # MCP server integration

tests/
├── test_sequential_thinking.py      # Unit tests
└── test_mcp_integration.py          # Integration tests
```

### Core Components

- **ThoughtData**: Dataclass representing a single thought
- **SequentialThinkingServer**: Main server managing thought processing
- **MCP Tools**: Four tools for interacting with the thinking process

## Examples

### Problem Solving Example

```python
server = SequentialThinkingServer()

# Step 1: Understand the problem
server.process_thought({
    "thought": "Understanding the user's requirements",
    "thoughtNumber": 1,
    "totalThoughts": 4,
    "nextThoughtNeeded": True
})

# Step 2: Design solution
server.process_thought({
    "thought": "Designing the solution architecture",
    "thoughtNumber": 2,
    "totalThoughts": 4,
    "nextThoughtNeeded": True
})

# Step 3: Consider alternatives
server.process_thought({
    "thought": "Exploring alternative approaches",
    "thoughtNumber": 3,
    "totalThoughts": 4,
    "branchFromThought": 2,
    "branchId": "alt-design",
    "nextThoughtNeeded": True
})

# Step 4: Final decision
server.process_thought({
    "thought": "Selecting optimal approach based on analysis",
    "thoughtNumber": 4,
    "totalThoughts": 4,
    "nextThoughtNeeded": False
})

# Check completion
assert server.is_complete() == True
```

## Contributing

1. Follow TDD - write tests first
2. Make atomic commits with clear messages
3. Maintain YAGNI principle - don't add unnecessary features
4. Ensure all tests pass before committing

## License

MIT License - See LICENSE file for details