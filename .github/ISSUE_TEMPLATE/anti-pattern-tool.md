---
name: Anti-Pattern Detection Tool
about: Template for creating new anti-pattern detection tools
title: '🛠️ [Tool Name] Anti-Pattern Detection Tool'
labels: enhancement, anti-patterns
assignees: ''
---

## Problem
**What AI failure pattern does this tool address?**
<!-- Describe the specific pattern of AI behavior that leads to poor outcomes -->

## Solution
**How will this tool detect and prevent the pattern?**
<!-- High-level approach to detection and intervention -->

- **Detection method**: How the tool identifies the pattern
- **Prevention strategy**: How it intervenes to prevent the pattern
- **User guidance**: What actionable advice it provides
- **Integration approach**: How it fits with existing tools

## Technical Requirements
**Implementation specifications:**
- [ ] Pattern detection algorithm/heuristics
- [ ] Real-time analysis capabilities  
- [ ] MCP tool integration (SSE transport compatible)
- [ ] Response time requirements (<2s for real-time)
- [ ] Accuracy targets (specify %)
- [ ] Integration with collaborative reasoning tools

## Acceptance Criteria
**Definition of done:**
- [ ] Detects target pattern with specified accuracy
- [ ] Provides actionable intervention recommendations
- [ ] Integrates seamlessly with existing MCP architecture
- [ ] Meets performance requirements
- [ ] Includes comprehensive tests
- [ ] Documentation and usage examples provided

## Priority
<!-- High/Medium/Low with justification -->

## Pattern Examples
**Specific examples of the anti-pattern this tool should catch:**
<!-- Provide concrete examples to guide development and testing -->

## Integration Points
**How this tool works with existing Ustad Protocol tools:**
- [ ] Works with `ustad_think` for complex analysis
- [ ] Integrates with `ustad_research` for fact-checking
- [ ] Compatible with `ustad_preflight` for prevention
- [ ] Supports session isolation and SSE transport

## Testing Strategy
**How to validate the tool works correctly:**
- [ ] Unit tests for detection logic
- [ ] Integration tests with MCP server
- [ ] Performance benchmarks
- [ ] User acceptance testing scenarios

## Success Metrics
**How to measure tool effectiveness:**
- Detection accuracy: __%
- Response time: __ms
- User satisfaction: qualitative feedback
- Pattern reduction: measurable improvement