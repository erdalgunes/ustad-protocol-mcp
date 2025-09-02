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