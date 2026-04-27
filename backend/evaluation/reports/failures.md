# Failure Analysis Report

**Date**: 2026-04-27 21:31
**Total Failures**: 8

## Failure Categories

- **low_retrieval_relevance**: 4 cases
- **semantic_mismatch**: 1 cases
- **false_positive_retrieval**: 3 cases

## Detailed Examples

### F07: What does MRO stand for in Python?
- **Type**: factual
- **Category**: low_retrieval_relevance
- **Semantic Similarity**: 0.2035
- **Key Term Coverage**: 0.0
- **Top Vector Score**: 0.6078

### F08: What are the four core OOP concepts in Python?
- **Type**: factual
- **Category**: low_retrieval_relevance
- **Semantic Similarity**: 0.2929
- **Key Term Coverage**: 0.25
- **Top Vector Score**: 0.5964

### F11: What is a generator in Python?
- **Type**: factual
- **Category**: semantic_mismatch
- **Semantic Similarity**: 0.1582
- **Key Term Coverage**: 0.333
- **Top Vector Score**: 0.6651

### F13: What is a decorator in Python?
- **Type**: factual
- **Category**: low_retrieval_relevance
- **Semantic Similarity**: 0.3432
- **Key Term Coverage**: 0.25
- **Top Vector Score**: 0.7554

### C02: Why are strings immutable in Python?
- **Type**: conceptual
- **Category**: low_retrieval_relevance
- **Semantic Similarity**: 0.3225
- **Key Term Coverage**: 0.25
- **Top Vector Score**: 0.5023

### A02: How does React handle state management?
- **Type**: adversarial
- **Category**: false_positive_retrieval
- **Semantic Similarity**: 0
- **Key Term Coverage**: 0
- **Top Vector Score**: 0.3166

### A04: Explain quantum computing error correction.
- **Type**: adversarial
- **Category**: false_positive_retrieval
- **Semantic Similarity**: 0
- **Key Term Coverage**: 0
- **Top Vector Score**: 0.3174

### A09: How do you train a GPT model from scratch?
- **Type**: adversarial
- **Category**: false_positive_retrieval
- **Semantic Similarity**: 0
- **Key Term Coverage**: 0
- **Top Vector Score**: 0.2505

