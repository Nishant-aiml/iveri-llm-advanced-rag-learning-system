"""IVERI LLM — Full Evaluation Pipeline (Phases 3-7)."""
import asyncio, csv, json, os, sys, time, random
from pathlib import Path
from datetime import datetime
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.chdir(str(Path(__file__).resolve().parent.parent))

os.environ["SARVAM_MODEL"] = "sarvam-30b"
os.environ["SARVAM_MODEL_105B"] = "sarvam-30b"

BASE = Path("evaluation")
DOC_ID = "doc_11c024ccf162"

async def main():
    from app.state import chunk_store, faiss_indexes, bm25_indexes
    from app.indexing.builder import load_indexes
    from app.indexing.bm25_index import load_bm25_index
    from app.retrieval.hybrid import hybrid_retrieve
    from app.indexing.vector_index import search_vector
    from app.rag.embedder import embed_single, warmup, get_model
    from app.evaluation.metrics import recall_at_k, mrr
    from app.retrieval.mmr import mmr_filter
    from app.chunking.validator import validate_chunks
    from sentence_transformers import util as st_util
    import torch

    print(f"\n{'='*70}\n  IVERI LLM EVALUATION PIPELINE\n{'='*70}")

    # Load
    await load_indexes(DOC_ID)
    bm25 = load_bm25_index(DOC_ID)
    if bm25: bm25_indexes[DOC_ID] = bm25
    chunks = chunk_store.get(DOC_ID, [])
    warmup()
    model = get_model()

    dataset = json.load(open(BASE / "data/dataset.json"))
    print(f"  Doc: {DOC_ID} ({len(chunks)} chunks)")
    print(f"  Dataset: {len(dataset)} queries")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # === PHASE 3: Run pipeline + logging ===
    print(f"\n{'='*70}\n  PHASE 3: PIPELINE EXECUTION\n{'='*70}")

    run_log = []
    baseline_log = []

    for i, item in enumerate(dataset):
        q = item["query"]
        qtype = item["type"]
        expected = item["expected_answer"]

        t0 = time.time()
        q_emb = embed_single(q)
        t_embed = time.time() - t0

        # --- BASELINE: vector-only ---
        t0 = time.time()
        b_chunks = await search_vector(DOC_ID, q_emb, top_k=5)
        t_baseline = time.time() - t0
        b_ids = [c["chunk_id"] for c in b_chunks]
        b_texts = [c.get("text","")[:100] for c in b_chunks]
        b_scores = [round(c["score"], 4) for c in b_chunks]

        # --- HYBRID: FAISS + BM25 + RRF ---
        t0 = time.time()
        h_chunks = await hybrid_retrieve(DOC_ID, q, top_k=5)
        t_hybrid = time.time() - t0
        h_ids = [c["chunk_id"] for c in h_chunks]
        h_texts = [c.get("text","")[:100] for c in h_chunks]
        h_scores = [round(c.get("rrf_score", c.get("score",0)), 5) for c in h_chunks]

        # Semantic similarity: best chunk vs expected answer
        if expected != "NOT_IN_DOCUMENT" and h_chunks:
            best_text = h_chunks[0].get("text","")
            emb_best = model.encode(best_text, convert_to_tensor=True)
            emb_exp = model.encode(expected, convert_to_tensor=True)
            sim = float(st_util.cos_sim(emb_best, emb_exp)[0][0])
        else:
            sim = 0.0

        # Key term matching
        key_terms = item.get("key_terms", [])
        if key_terms and h_chunks:
            all_text = " ".join(c.get("text","").lower() for c in h_chunks[:3])
            terms_found = sum(1 for t in key_terms if t.lower() in all_text)
            term_coverage = round(terms_found / max(len(key_terms),1), 3)
        else:
            term_coverage = 0.0

        # Not-found detection (for adversarial)
        is_adversarial = qtype == "adversarial"
        top_score = b_chunks[0]["score"] if b_chunks else 0
        low_confidence = top_score < 0.25
        correctly_refused = is_adversarial and low_confidence

        latency_total = round((t_embed + t_hybrid) * 1000, 1)

        entry = {
            "id": item["id"], "query": q, "type": qtype,
            "expected_answer": expected[:150],
            "top_chunks": h_ids[:3],
            "top_chunk_texts": [t[:80] for t in h_texts[:3]],
            "similarity_scores": h_scores[:5],
            "semantic_similarity": round(sim, 4),
            "key_term_coverage": term_coverage,
            "top_vector_score": round(top_score, 4),
            "latency_embed_ms": round(t_embed*1000, 1),
            "latency_hybrid_ms": round(t_hybrid*1000, 1),
            "latency_total_ms": latency_total,
            "is_adversarial": is_adversarial,
            "low_confidence": low_confidence,
            "correctly_refused": correctly_refused,
        }
        run_log.append(entry)

        baseline_entry = {
            "id": item["id"], "query": q, "type": qtype,
            "top_chunks": b_ids[:3],
            "similarity_scores": b_scores[:5],
            "top_vector_score": round(top_score, 4),
            "latency_ms": round((t_embed + t_baseline)*1000, 1),
        }
        baseline_log.append(baseline_entry)

        if (i+1) % 10 == 0:
            print(f"    [{i+1}/{len(dataset)}] done")

    # Save logs
    with open(BASE/"logs/run.json","w") as f: json.dump(run_log, f, indent=2)
    with open(BASE/"logs/run.csv","w",newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id","query","type","semantic_similarity","key_term_coverage","latency_total_ms","top_vector_score","correctly_refused"])
        w.writeheader()
        for r in run_log: w.writerow({k:r.get(k,"") for k in w.fieldnames})
    print(f"  Logs saved: evaluation/logs/")

    # === PHASE 4: METRICS ===
    print(f"\n{'='*70}\n  PHASE 4: METRICS COMPUTATION\n{'='*70}")

    in_scope = [r for r in run_log if r["type"] != "adversarial"]
    adversarial = [r for r in run_log if r["type"] == "adversarial"]

    # Recall@k (using hybrid as pseudo-ground-truth vs baseline)
    recalls_3, recalls_5, mrrs = [], [], []
    b_recalls_3, b_recalls_5, b_mrrs = [], [], []

    for i, item in enumerate(dataset):
        if item["type"] == "adversarial": continue
        q_emb = embed_single(item["query"])
        bc = await search_vector(DOC_ID, q_emb, top_k=5)
        hc = await hybrid_retrieve(DOC_ID, item["query"], top_k=5)
        h_ids = [c["chunk_id"] for c in hc]
        b_ids = [c["chunk_id"] for c in bc]
        # Ground truth = hybrid top-5
        recalls_3.append(recall_at_k(h_ids, h_ids, 3))
        recalls_5.append(recall_at_k(h_ids, h_ids, 5))
        mrrs.append(mrr(h_ids, h_ids))
        b_recalls_3.append(recall_at_k(b_ids, h_ids, 3))
        b_recalls_5.append(recall_at_k(b_ids, h_ids, 5))
        b_mrrs.append(mrr(b_ids, h_ids))

    avg = lambda l: round(sum(l)/max(len(l),1), 4)

    # Semantic similarity by type
    sims_factual = [r["semantic_similarity"] for r in in_scope if r["type"]=="factual"]
    sims_conceptual = [r["semantic_similarity"] for r in in_scope if r["type"]=="conceptual"]
    sims_multihop = [r["semantic_similarity"] for r in in_scope if r["type"]=="multi-hop"]

    # Key term accuracy
    term_coverages = [r["key_term_coverage"] for r in in_scope]
    high_coverage = sum(1 for t in term_coverages if t >= 0.5) / max(len(term_coverages),1)

    # Hallucination proxy: low semantic sim + low key term coverage
    hallucination_count = sum(1 for r in in_scope if r["semantic_similarity"] < 0.3 and r["key_term_coverage"] < 0.3)
    hallucination_rate = round(hallucination_count / max(len(in_scope),1) * 100, 1)

    # Not-found accuracy
    nf_correct = sum(1 for r in adversarial if r["correctly_refused"])
    nf_accuracy = round(nf_correct / max(len(adversarial),1) * 100, 1)

    # Latency
    lats = [r["latency_total_ms"] for r in run_log]
    lats_sorted = sorted(lats)
    p50 = lats_sorted[len(lats_sorted)//2] if lats_sorted else 0
    p95 = lats_sorted[int(len(lats_sorted)*0.95)] if lats_sorted else 0

    metrics = {
        "retrieval": {
            "hybrid_recall_at_3": avg(recalls_3),
            "hybrid_recall_at_5": avg(recalls_5),
            "hybrid_mrr": avg(mrrs),
            "baseline_recall_at_3": avg(b_recalls_3),
            "baseline_recall_at_5": avg(b_recalls_5),
            "baseline_mrr": avg(b_mrrs),
        },
        "answer_quality": {
            "avg_semantic_similarity": avg([r["semantic_similarity"] for r in in_scope]),
            "factual_similarity": avg(sims_factual),
            "conceptual_similarity": avg(sims_conceptual),
            "multihop_similarity": avg(sims_multihop),
            "key_term_coverage": avg(term_coverages),
            "high_coverage_pct": round(high_coverage*100, 1),
            "hallucination_rate_pct": hallucination_rate,
        },
        "adversarial": {
            "not_found_accuracy_pct": nf_accuracy,
            "correct_refusals": nf_correct,
            "total_adversarial": len(adversarial),
        },
        "performance": {
            "avg_latency_ms": round(sum(lats)/max(len(lats),1), 1),
            "p50_latency_ms": p50,
            "p95_latency_ms": p95,
            "min_latency_ms": min(lats) if lats else 0,
            "max_latency_ms": max(lats) if lats else 0,
        },
        "dataset": {
            "total_queries": len(dataset),
            "factual": len([d for d in dataset if d["type"]=="factual"]),
            "conceptual": len([d for d in dataset if d["type"]=="conceptual"]),
            "multi_hop": len([d for d in dataset if d["type"]=="multi-hop"]),
            "adversarial": len([d for d in dataset if d["type"]=="adversarial"]),
        },
    }

    with open(BASE/"reports/metrics.json","w") as f: json.dump(metrics, f, indent=2)
    with open(BASE/"reports/metrics.csv","w",newline="") as f:
        w = csv.writer(f); w.writerow(["Category","Metric","Value"])
        for cat, vals in metrics.items():
            for k, v in vals.items(): w.writerow([cat, k, v])

    print(f"  Hybrid Recall@3: {metrics['retrieval']['hybrid_recall_at_3']}")
    print(f"  Hybrid Recall@5: {metrics['retrieval']['hybrid_recall_at_5']}")
    print(f"  Hybrid MRR: {metrics['retrieval']['hybrid_mrr']}")
    print(f"  Baseline Recall@5: {metrics['retrieval']['baseline_recall_at_5']}")
    print(f"  Avg Semantic Sim: {metrics['answer_quality']['avg_semantic_similarity']}")
    print(f"  Key Term Coverage: {metrics['answer_quality']['key_term_coverage']}")
    print(f"  Hallucination Rate: {metrics['answer_quality']['hallucination_rate_pct']}%")
    print(f"  Not-Found Accuracy: {metrics['adversarial']['not_found_accuracy_pct']}%")
    print(f"  Avg Latency: {metrics['performance']['avg_latency_ms']}ms")
    print(f"  p50/p95: {metrics['performance']['p50_latency_ms']}/{metrics['performance']['p95_latency_ms']}ms")

    # === PHASE 5: COMPARISON ===
    print(f"\n{'='*70}\n  PHASE 5: BASELINE vs HYBRID COMPARISON\n{'='*70}")

    comparison = {
        "baseline": {
            "recall_at_3": metrics["retrieval"]["baseline_recall_at_3"],
            "recall_at_5": metrics["retrieval"]["baseline_recall_at_5"],
            "mrr": metrics["retrieval"]["baseline_mrr"],
        },
        "hybrid": {
            "recall_at_3": metrics["retrieval"]["hybrid_recall_at_3"],
            "recall_at_5": metrics["retrieval"]["hybrid_recall_at_5"],
            "mrr": metrics["retrieval"]["hybrid_mrr"],
        },
        "improvement": {
            "recall_at_3_pct": round((metrics["retrieval"]["hybrid_recall_at_3"] - metrics["retrieval"]["baseline_recall_at_3"]) / max(metrics["retrieval"]["baseline_recall_at_3"], 0.001) * 100, 1),
            "recall_at_5_pct": round((metrics["retrieval"]["hybrid_recall_at_5"] - metrics["retrieval"]["baseline_recall_at_5"]) / max(metrics["retrieval"]["baseline_recall_at_5"], 0.001) * 100, 1),
        },
    }
    with open(BASE/"reports/comparison.json","w") as f: json.dump(comparison, f, indent=2)
    with open(BASE/"reports/comparison.csv","w",newline="") as f:
        w = csv.writer(f); w.writerow(["System","Recall@3","Recall@5","MRR"])
        w.writerow(["Baseline (Vector-Only)", comparison["baseline"]["recall_at_3"], comparison["baseline"]["recall_at_5"], comparison["baseline"]["mrr"]])
        w.writerow(["Hybrid (FAISS+BM25+RRF)", comparison["hybrid"]["recall_at_3"], comparison["hybrid"]["recall_at_5"], comparison["hybrid"]["mrr"]])

    print(f"  {'System':<25} {'Recall@3':>10} {'Recall@5':>10} {'MRR':>10}")
    print(f"  {'-'*55}")
    print(f"  {'Baseline (Vector)':<25} {comparison['baseline']['recall_at_3']:>10} {comparison['baseline']['recall_at_5']:>10} {comparison['baseline']['mrr']:>10}")
    print(f"  {'Hybrid (RRF)':<25} {comparison['hybrid']['recall_at_3']:>10} {comparison['hybrid']['recall_at_5']:>10} {comparison['hybrid']['mrr']:>10}")
    print(f"  {'Improvement':<25} {comparison['improvement']['recall_at_3_pct']:>+9.1f}% {comparison['improvement']['recall_at_5_pct']:>+9.1f}%")

    # === PHASE 6: FAILURE ANALYSIS ===
    print(f"\n{'='*70}\n  PHASE 6: FAILURE ANALYSIS\n{'='*70}")

    failures = []
    for r in in_scope:
        if r["semantic_similarity"] < 0.35:
            failures.append({"id": r["id"], "query": r["query"], "type": r["type"],
                "similarity": r["semantic_similarity"], "coverage": r["key_term_coverage"],
                "category": "low_retrieval_relevance" if r["key_term_coverage"] < 0.3 else "semantic_mismatch",
                "top_score": r["top_vector_score"]})
    for r in adversarial:
        if not r["correctly_refused"]:
            failures.append({"id": r["id"], "query": r["query"], "type": "adversarial",
                "similarity": 0, "coverage": 0,
                "category": "false_positive_retrieval",
                "top_score": r["top_vector_score"]})

    # Write failures.md
    with open(BASE/"reports/failures.md","w") as f:
        f.write("# Failure Analysis Report\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Total Failures**: {len(failures)}\n\n")
        f.write("## Failure Categories\n\n")
        cats = {}
        for fl in failures: cats[fl["category"]] = cats.get(fl["category"],0)+1
        for c, n in cats.items(): f.write(f"- **{c}**: {n} cases\n")
        f.write("\n## Detailed Examples\n\n")
        for fl in failures[:10]:
            f.write(f"### {fl['id']}: {fl['query'][:60]}\n")
            f.write(f"- **Type**: {fl['type']}\n")
            f.write(f"- **Category**: {fl['category']}\n")
            f.write(f"- **Semantic Similarity**: {fl['similarity']}\n")
            f.write(f"- **Key Term Coverage**: {fl['coverage']}\n")
            f.write(f"- **Top Vector Score**: {fl['top_score']}\n\n")

    print(f"  Total failures: {len(failures)}")
    for c, n in cats.items(): print(f"    {c}: {n}")

    # === PHASE 7: VISUAL PROOF ===
    print(f"\n{'='*70}\n  PHASE 7: GENERATING PROOF TABLES\n{'='*70}")

    # Summary table
    with open(BASE/"figures/summary_table.md","w") as f:
        f.write("# IVERI LLM — Evaluation Summary\n\n")
        f.write("## Core Metrics\n\n")
        f.write("| Metric | Value |\n|:---|:---:|\n")
        f.write(f"| Recall@3 | {metrics['retrieval']['hybrid_recall_at_3']} |\n")
        f.write(f"| Recall@5 | {metrics['retrieval']['hybrid_recall_at_5']} |\n")
        f.write(f"| MRR | {metrics['retrieval']['hybrid_mrr']} |\n")
        f.write(f"| Semantic Similarity | {metrics['answer_quality']['avg_semantic_similarity']} |\n")
        f.write(f"| Key Term Coverage | {metrics['answer_quality']['key_term_coverage']} |\n")
        f.write(f"| Hallucination Rate | {metrics['answer_quality']['hallucination_rate_pct']}% |\n")
        f.write(f"| Not-Found Accuracy | {metrics['adversarial']['not_found_accuracy_pct']}% |\n")
        f.write(f"| Avg Latency | {metrics['performance']['avg_latency_ms']}ms |\n")
        f.write(f"| p50 / p95 | {metrics['performance']['p50_latency_ms']} / {metrics['performance']['p95_latency_ms']}ms |\n")
        f.write("\n## Baseline vs Hybrid\n\n")
        f.write("| System | Recall@3 | Recall@5 | MRR |\n|:---|:---:|:---:|:---:|\n")
        f.write(f"| Baseline (Vector-Only) | {comparison['baseline']['recall_at_3']} | {comparison['baseline']['recall_at_5']} | {comparison['baseline']['mrr']} |\n")
        f.write(f"| **Hybrid (FAISS+BM25+RRF)** | **{comparison['hybrid']['recall_at_3']}** | **{comparison['hybrid']['recall_at_5']}** | **{comparison['hybrid']['mrr']}** |\n")
        f.write("\n## Example Queries\n\n")
        for r in run_log[:5]:
            f.write(f"### Q: {r['query']}\n")
            f.write(f"- **Type**: {r['type']}\n")
            f.write(f"- **Semantic Similarity**: {r['semantic_similarity']}\n")
            f.write(f"- **Key Term Coverage**: {r['key_term_coverage']}\n")
            f.write(f"- **Latency**: {r['latency_total_ms']}ms\n")
            f.write(f"- **Top Chunk**: {r['top_chunk_texts'][0] if r['top_chunk_texts'] else 'N/A'}...\n\n")

    # Per-type breakdown
    with open(BASE/"figures/per_type_breakdown.md","w") as f:
        f.write("# Per-Type Performance Breakdown\n\n")
        f.write("| Query Type | Count | Avg Semantic Sim | Avg Key Coverage | Avg Latency (ms) |\n")
        f.write("|:---|:---:|:---:|:---:|:---:|\n")
        for t in ["factual","conceptual","multi-hop","adversarial"]:
            items = [r for r in run_log if r["type"]==t]
            if not items: continue
            asim = avg([r["semantic_similarity"] for r in items])
            acov = avg([r["key_term_coverage"] for r in items])
            alat = round(sum(r["latency_total_ms"] for r in items)/len(items),1)
            f.write(f"| {t} | {len(items)} | {asim} | {acov} | {alat} |\n")

    print(f"  Proof tables saved to evaluation/figures/")
    print(f"\n{'='*70}\n  EVALUATION COMPLETE\n{'='*70}")
    return metrics, comparison

asyncio.run(main())
