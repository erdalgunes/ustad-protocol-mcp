# Batch of Thought MCP Server 🧠

Generic parallel thinking system for the Quetiapine Protocol - replaces sequential thinking with 8 concurrent perspectives.

## What is Batch of Thought?

Instead of thinking sequentially (one thought after another), BoT generates multiple thoughts in parallel from different perspectives, then synthesizes them for better decision-making. This is part of the Quetiapine Protocol for managing AI neurodivergent-like patterns.

## Installation

```bash
# For Claude Code
claude mcp add /Users/erdalgunes/batch-of-thought-mcp

# Restart Claude Code after installation
```

## The 8 Thinking Perspectives

1. **Analytical** - Break down problems systematically
2. **Creative** - Think outside the box, unconventional solutions  
3. **Critical** - Question assumptions, identify risks
4. **Practical** - Focus on implementation and feasibility
5. **Strategic** - Long-term implications and goals
6. **Empirical** - Data-driven, evidence-based thinking
7. **Intuitive** - Pattern recognition and insights
8. **Systematic** - Follow established procedures

## Available Tools

### `batch_think`
Generate parallel thoughts on any problem:
```json
{
  "problem": "How can we improve code review processes?",
  "context": "Team of 10 developers, 2-week sprints",
  "num_thoughts": 8
}
```

### `iterative_think`
Refine thinking through iterations:
```json
{
  "problem": "Design a scalable authentication system",
  "max_iterations": 3,
  "convergence_threshold": 0.8
}
```

### `compare_perspectives`
See how different perspectives approach a problem:
```json
{
  "problem": "Should we migrate to microservices?",
  "perspectives": ["Practical", "Strategic", "Critical"]
}
```

### `get_perspectives`
List all available thinking perspectives.

### `custom_scored_think`
Think with custom scoring weights:
```json
{
  "problem": "Optimize database queries",
  "scoring_criteria": {
    "relevance": 0.4,
    "practicality": 0.3,
    "depth": 0.2,
    "coherence": 0.05,
    "innovation": 0.05
  }
}
```

## How It Replaces Sequential Thinking

### Traditional Sequential Thinking:
```
Thought 1 → Thought 2 → Thought 3 → Conclusion
```

### Batch of Thought:
```
        ┌→ Analytical ─┐
        ├→ Creative ───┤
        ├→ Critical ───┤
Problem ├→ Practical ──┼→ Synthesis → Best Solution
        ├→ Strategic ──┤
        ├→ Empirical ──┤
        ├→ Intuitive ──┤
        └→ Systematic ─┘
```

## Example Usage in Claude Code

```
Use batch_think to analyze: "What's the best architecture for a real-time chat application?"

Use iterative_think to solve: "How do we reduce our AWS costs by 30%?"

Use compare_perspectives with ["Critical", "Practical", "Strategic"] for: "Should we adopt Rust for our backend?"
```

## Quetiapine Protocol Integration

This MCP server is part of the Quetiapine Protocol v7.0, addressing AI neurodivergent-like patterns:

- **Anti-impulsivity**: Parallel thinking prevents jumping to conclusions
- **Anti-hallucination**: Multiple perspectives cross-validate each other
- **Anti-over-engineering**: Practical and Critical perspectives balance Creative
- **Context preservation**: Iterative thinking maintains context across iterations

## Performance

- Generates 8 parallel thoughts in <100ms
- Supports custom scoring criteria
- Iterative refinement for complex problems
- Thread-safe parallel execution

## Requirements

- Python 3.11+
- MCP SDK
- See requirements.txt for full list

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Start server manually
python -m bot_mcp.bot_mcp_server
```

## License

MIT

---

*"Parallel thoughts, better decisions"* - Quetiapine Protocol v7.0