# Failure Analysis Report

**Date**: 2026-04-27 21:46 | **Total Failures**: 10 / 60 queries

## Summary

| Category | Count | Description |
|:---|:---:|:---|
| hallucination_risk | 1 | Low sim + low coverage |
| retrieval_failure | 3 | No gold chunk in top-5 |
| semantic_mismatch | 3 | Low sim to expected answer |
| false_positive_retrieval | 3 | Adversarial not rejected |

## Detailed Examples (10 shown)

### F07: What does MRO stand for in Python?
- **Type**: factual | **Category**: hallucination_risk
- **Reason**: Low semantic sim (0.2035) and low key term coverage (0.0).
- **Semantic Similarity**: 0.2035 | **Coverage**: 0.0
- **Confidence**: 0.6321 (medium)
- **Top Chunk**: 3. Python Memory Model and Object System

Python uses a private heap to store all objects and data s...
- **Gold Chunks**: ['c_62d796bd0cac', 'c_c8588286ab34']

### F08: What are the four core OOP concepts in Python?
- **Type**: factual | **Category**: retrieval_failure
- **Reason**: No gold-standard chunk found in top-5 hybrid results.
- **Semantic Similarity**: 0.2929 | **Coverage**: 0.25
- **Confidence**: 0.825 (high)
- **Top Chunk**: 1. Python as a Programming Paradigm

Python is a multi-paradigm programming language that supports p...
- **Gold Chunks**: ['c_ec46c94c0ddd', 'c_be85e2e96ce0']

### F11: What is a generator in Python?
- **Type**: factual | **Category**: semantic_mismatch
- **Reason**: Retrieved relevant chunks but semantic similarity to expected answer is low (0.1582).
- **Semantic Similarity**: 0.1582 | **Coverage**: 0.333
- **Confidence**: 0.6771 (medium)
- **Top Chunk**: Python programs do not execute directly as machine code. Instead, they follow a multi-stage executio...
- **Gold Chunks**: ['c_ada4f094fa36', 'c_b493bbcf8aa7', 'c_ba93f31ca99b']

### F13: What is a decorator in Python?
- **Type**: factual | **Category**: semantic_mismatch
- **Reason**: Retrieved relevant chunks but semantic similarity to expected answer is low (0.3432).
- **Semantic Similarity**: 0.3432 | **Coverage**: 0.5
- **Confidence**: 0.6937 (medium)
- **Top Chunk**: In Python:

- functions can be assigned to variables - passed as arguments - returned from other fun...
- **Gold Chunks**: ['c_c0549b0e58d7', 'c_4cbba995df38']

### F18: What happens when you append to a list that is referenced by two varia
- **Type**: factual | **Category**: retrieval_failure
- **Reason**: No gold-standard chunk found in top-5 hybrid results.
- **Semantic Similarity**: 0.4971 | **Coverage**: 0.25
- **Confidence**: 0.7404 (high)
- **Top Chunk**: Lists

- Dynamic arrays - Amortized O(1) append...
- **Gold Chunks**: ['c_a8f2b3df765f', 'c_a9a432bcb4ed', 'c_b380c1ac25e1']

### C01: Why is Python called an interpreted language?
- **Type**: conceptual | **Category**: retrieval_failure
- **Reason**: No gold-standard chunk found in top-5 hybrid results.
- **Semantic Similarity**: 0.6462 | **Coverage**: 0.667
- **Confidence**: 0.9727 (high)
- **Top Chunk**: 1. Introduction to Python

Python is a high-level, interpreted, dynamically typed programming langua...
- **Gold Chunks**: ['c_cc85062c89c2', 'c_5c284b0d92ec', 'c_be7c85cde112']

### C02: Why are strings immutable in Python?
- **Type**: conceptual | **Category**: semantic_mismatch
- **Reason**: Retrieved relevant chunks but semantic similarity to expected answer is low (0.3225).
- **Semantic Similarity**: 0.3225 | **Coverage**: 0.25
- **Confidence**: 0.7614 (high)
- **Top Chunk**: Immutable Objects:

- int, float, str, tuple...
- **Gold Chunks**: ['c_330946c99287', 'c_a9a432bcb4ed']

### A02: How does React handle state management?
- **Type**: adversarial | **Category**: false_positive_retrieval
- **Reason**: Adversarial query not rejected. Vector score 0.3166 above threshold 0.25.
- **Semantic Similarity**: 0.0 | **Coverage**: 0.0
- **Confidence**: 0.5968 (medium)
- **Top Chunk**: 21. Python Memory Management

- Reference counting - Garbage collection...
- **Gold Chunks**: []

### A04: Explain quantum computing error correction.
- **Type**: adversarial | **Category**: false_positive_retrieval
- **Reason**: Adversarial query not rejected. Vector score 0.3174 above threshold 0.25.
- **Semantic Similarity**: 0.0 | **Coverage**: 0.0
- **Confidence**: 0.4903 (medium)
- **Top Chunk**: Key Properties:

- Keys must be immutable - Hash collisions handled internally...
- **Gold Chunks**: []

### A09: How do you train a GPT model from scratch?
- **Type**: adversarial | **Category**: false_positive_retrieval
- **Reason**: Adversarial query not rejected. Vector score 0.2505 above threshold 0.25.
- **Semantic Similarity**: 0.0 | **Coverage**: 0.0
- **Confidence**: 0.5368 (medium)
- **Top Chunk**: 20. Advanced Topics

- Metaclasses - Context Managers - Async programming...
- **Gold Chunks**: []

