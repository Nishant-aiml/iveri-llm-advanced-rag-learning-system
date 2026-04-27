# Trust Layer Formula

## Confidence Score Computation

```
confidence = 0.4 * norm_vector_score + 0.3 * norm_rrf_score + 0.3 * agreement_overlap
```

### Components

| Signal | Weight | Normalization | Source |
|:---|:---:|:---|:---|
| Vector similarity | 0.4 | `min(score / 0.5, 1.0)` | FAISS cosine similarity |
| RRF fusion score | 0.3 | `min(score / 0.1, 1.0)` | Reciprocal Rank Fusion |
| Agreement overlap | 0.3 | `overlap(vec_top3, hybrid_top3) / 3` | Cross-system agreement |

### Thresholds

| Level | Range | Action |
|:---|:---:|:---|
| High | > 0.7 | Return answer with sources |
| Medium | 0.4 - 0.7 | Return answer with lower confidence warning |
| Low | < 0.4 | Return 'Not enough information in document' |

### Calibration (Dataset A)

- High-confidence queries: 47 (93.6% actually correct)
- Low-confidence queries: 0
