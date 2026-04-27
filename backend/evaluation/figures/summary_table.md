# IVERI LLM — Evaluation Summary

## Core Metrics

| Metric | Value |
|:---|:---:|
| Recall@3 | 0.6 |
| Recall@5 | 1.0 |
| MRR | 1.0 |
| Semantic Similarity | 0.6089 |
| Key Term Coverage | 0.514 |
| Hallucination Rate | 4.0% |
| Not-Found Accuracy | 70.0% |
| Avg Latency | 107.0ms |
| p50 / p95 | 102.6 / 148.5ms |

## Baseline vs Hybrid

| System | Recall@3 | Recall@5 | MRR |
|:---|:---:|:---:|:---:|
| Baseline (Vector-Only) | 0.524 | 0.724 | 0.98 |
| **Hybrid (FAISS+BM25+RRF)** | **0.6** | **1.0** | **1.0** |

## Example Queries

### Q: What type of programming language is Python?
- **Type**: factual
- **Semantic Similarity**: 0.8487
- **Key Term Coverage**: 1.0
- **Latency**: 103.1ms
- **Top Chunk**: 1. Python as a Programming Paradigm

Python is a multi-paradigm programming lang...

### Q: What are mutable objects in Python?
- **Type**: factual
- **Semantic Similarity**: 0.8114
- **Key Term Coverage**: 1.0
- **Latency**: 102.6ms
- **Top Chunk**: Mutable Objects:

- list, dict, set...

### Q: What are immutable types in Python?
- **Type**: factual
- **Semantic Similarity**: 0.7702
- **Key Term Coverage**: 0.833
- **Latency**: 169.8ms
- **Top Chunk**: 3.1 Immutable Types

- int - float - str - tuple...

### Q: What is the time complexity of dictionary lookup in Python?
- **Type**: factual
- **Semantic Similarity**: 0.782
- **Key Term Coverage**: 1.0
- **Latency**: 92.7ms
- **Top Chunk**: Dictionaries

- Hash tables - Average O(1) lookup...

### Q: What is the LEGB rule in Python?
- **Type**: factual
- **Semantic Similarity**: 0.5892
- **Key Term Coverage**: 0.8
- **Latency**: 90.4ms
- **Top Chunk**: LEGB Rule:

- Local - Enclosing - Global - Built-in...

