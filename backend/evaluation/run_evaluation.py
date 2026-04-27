"""IVERI LLM — Credibility-Fixed Evaluation (Phases 1-9).
Independent ground truth, multi-dataset, trust formalization, latency breakdown.
"""
import asyncio, csv, json, os, sys, time, random, math
from pathlib import Path
from datetime import datetime
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.chdir(str(Path(__file__).resolve().parent.parent))

BASE = Path("evaluation")

# === GROUND TRUTH: manually mapped chunk IDs for doc_11c024ccf162 ===
GROUND_TRUTH = {
    "F01": ["c_7ecfd4d5f417","c_289a9189d17b","c_bbbcc3794f4b"],
    "F02": ["c_b380c1ac25e1","c_a9a432bcb4ed","c_a8f2b3df765f"],
    "F03": ["c_330946c99287","c_3e073f2e8068"],
    "F04": ["c_1885dd7ad9ed","c_f7f6a75df9ca","c_1786c6e7c6b5"],
    "F05": ["c_f98efd97da26","c_247b99b9f807","c_65afd418a661"],
    "F06": ["c_163bc99577a9","c_c04916c1c3b0","c_42b5d0777bac"],
    "F07": ["c_62d796bd0cac","c_c8588286ab34"],
    "F08": ["c_ec46c94c0ddd","c_be85e2e96ce0"],
    "F09": ["c_c8fc3127f857","c_04b548a90061","c_10e30c065703"],
    "F10": ["c_8a69e4135a24"],
    "F11": ["c_ada4f094fa36","c_b493bbcf8aa7","c_ba93f31ca99b","c_dc4c132ada07"],
    "F12": ["c_89f1194d0242","c_e8adb0cd837c","c_8b74381372c0"],
    "F13": ["c_c0549b0e58d7","c_4cbba995df38"],
    "F14": ["c_86ef97d2bbf3"],
    "F15": ["c_f745092d9032","c_46b68418ea0b"],
    "F16": ["c_45137df2249f","c_041eb6f37d44"],
    "F17": ["c_10e30c065703","c_04b548a90061","c_0c5ad41bf610","c_c8fc3127f857"],
    "F18": ["c_a8f2b3df765f","c_a9a432bcb4ed","c_b380c1ac25e1"],
    "F19": ["c_8f957d0fa5b8","c_1786c6e7c6b5"],
    "F20": ["c_81f45b6ad4f0"],
    "C01": ["c_cc85062c89c2","c_5c284b0d92ec","c_be7c85cde112"],
    "C02": ["c_330946c99287","c_a9a432bcb4ed"],
    "C03": ["c_6d7f19fba0d4","c_752e7bf0b413","c_9aada2bb5c3b"],
    "C04": ["c_c8fc3127f857","c_04b548a90061","c_a9f1b8d0eabd"],
    "C05": ["c_65afd418a661","c_601d5c3a7412","c_247b99b9f807"],
    "C06": ["c_ada4f094fa36","c_ba93f31ca99b","c_b493bbcf8aa7"],
    "C07": ["c_f7f6a75df9ca","c_1786c6e7c6b5"],
    "C08": ["c_c04916c1c3b0","c_42b5d0777bac"],
    "C09": ["c_8edfe7c26f68","c_54b5171e2ea6"],
    "C10": ["c_a9a432bcb4ed","c_a8f2b3df765f","c_330946c99287","c_b380c1ac25e1"],
    "C11": ["c_cc85062c89c2","c_5c284b0d92ec"],
    "C12": ["c_c0549b0e58d7","c_4cbba995df38"],
    "C13": ["c_89f1194d0242","c_e8adb0cd837c","c_8b74381372c0"],
    "C14": ["c_c8fc3127f857","c_a9f1b8d0eabd","c_0c5ad41bf610"],
    "C15": ["c_65afd418a661","c_247b99b9f807","c_f98efd97da26"],
    "C16": ["c_d154c587830d","c_70ee780b2762","c_2c071b5b9408"],
    "C17": ["c_6d7f19fba0d4","c_330946c99287","c_b380c1ac25e1"],
    "C18": ["c_55ff91cba487","c_b493bbcf8aa7","c_ba93f31ca99b","c_dc4c132ada07"],
    "C19": ["c_c8588286ab34","c_62d796bd0cac"],
    "C20": ["c_83e0c0bcd842","c_4d1cb3b03136"],
    "M01": ["c_752e7bf0b413","c_9aada2bb5c3b","c_330946c99287"],
    "M02": ["c_c8fc3127f857","c_04b548a90061","c_a8f2b3df765f"],
    "M03": ["c_54b5171e2ea6","c_8edfe7c26f68","c_247b99b9f807"],
    "M04": ["c_83e0c0bcd842","c_a8f2b3df765f","c_4d1cb3b03136"],
    "M05": ["c_1786c6e7c6b5","c_f7f6a75df9ca","c_330946c99287"],
    "M06": ["c_4cbba995df38","c_c0549b0e58d7","c_8edfe7c26f68","c_2c071b5b9408"],
    "M07": ["c_752e7bf0b413","c_6d7f19fba0d4","c_9aada2bb5c3b"],
    "M08": ["c_ada4f094fa36","c_e8adb0cd837c","c_cc85062c89c2"],
    "M09": ["c_c8588286ab34","c_62d796bd0cac"],
    "M10": ["c_45137df2249f","c_041eb6f37d44","c_a8f2b3df765f"],
}

async def evaluate_dataset(doc_id, dataset, gt_map, label):
    """Run evaluation on one dataset with independent ground truth."""
    from app.state import chunk_store, faiss_indexes, bm25_indexes
    from app.indexing.builder import load_indexes
    from app.indexing.bm25_index import load_bm25_index
    from app.retrieval.hybrid import hybrid_retrieve
    from app.indexing.vector_index import search_vector
    from app.rag.embedder import embed_single, get_model
    from app.evaluation.metrics import recall_at_k, mrr
    from sentence_transformers import util as st_util

    await load_indexes(doc_id)
    bm25 = load_bm25_index(doc_id)
    if bm25: bm25_indexes[doc_id] = bm25
    model = get_model()

    results = []
    b_r3, b_r5, b_mrrs = [], [], []
    h_r3, h_r5, h_mrrs = [], [], []
    lats_embed, lats_vec, lats_hyb = [], [], []

    for item in dataset:
        qid = item["id"]
        q = item["query"]
        expected = item["expected_answer"]
        is_adv = item["type"] == "adversarial"
        gold = gt_map.get(qid, [])

        t0 = time.time(); q_emb = embed_single(q); t_emb = time.time()-t0
        t0 = time.time(); bc = await search_vector(doc_id, q_emb, top_k=5); t_vec = time.time()-t0
        t0 = time.time(); hc = await hybrid_retrieve(doc_id, q, top_k=5); t_hyb = time.time()-t0

        lats_embed.append(t_emb*1000); lats_vec.append(t_vec*1000); lats_hyb.append(t_hyb*1000)

        b_ids = [c["chunk_id"] for c in bc]
        h_ids = [c["chunk_id"] for c in hc]

        # Semantic similarity
        if not is_adv and hc:
            best = hc[0].get("text","")
            sim = float(st_util.cos_sim(model.encode(best,convert_to_tensor=True), model.encode(expected,convert_to_tensor=True))[0][0])
        else:
            sim = 0.0

        # Key term coverage
        keys = item.get("key_terms",[])
        if keys and hc:
            all_t = " ".join(c.get("text","").lower() for c in hc[:3])
            cov = sum(1 for k in keys if k.lower() in all_t) / len(keys)
        else:
            cov = 0.0

        # Confidence (trust formula)
        top_vec = bc[0]["score"] if bc else 0
        top_rrf = hc[0].get("rrf_score",0) if hc else 0
        norm_vec = min(top_vec / 0.5, 1.0)
        norm_rrf = min(top_rrf / 0.1, 1.0)
        overlap = len(set(b_ids[:3]) & set(h_ids[:3])) / 3
        confidence = 0.4*norm_vec + 0.3*norm_rrf + 0.3*overlap
        conf_level = "high" if confidence>0.7 else ("medium" if confidence>0.4 else "low")

        # Not-found detection
        refused = top_vec < 0.25

        if not is_adv and gold:
            b_r3.append(recall_at_k(b_ids, gold, 3))
            b_r5.append(recall_at_k(b_ids, gold, 5))
            b_mrrs.append(mrr(b_ids, gold))
            h_r3.append(recall_at_k(h_ids, gold, 3))
            h_r5.append(recall_at_k(h_ids, gold, 5))
            h_mrrs.append(mrr(h_ids, gold))

        results.append({
            "id": qid, "query": q, "type": item["type"],
            "gold_chunks": gold[:3] if gold else [],
            "baseline_top5": b_ids, "hybrid_top5": h_ids,
            "baseline_recall3": recall_at_k(b_ids, gold, 3) if gold else None,
            "hybrid_recall3": recall_at_k(h_ids, gold, 3) if gold else None,
            "baseline_recall5": recall_at_k(b_ids, gold, 5) if gold else None,
            "hybrid_recall5": recall_at_k(h_ids, gold, 5) if gold else None,
            "semantic_similarity": round(sim, 4),
            "key_term_coverage": round(cov, 3),
            "top_vector_score": round(top_vec, 4),
            "confidence": round(confidence, 4),
            "confidence_level": conf_level,
            "is_adversarial": is_adv,
            "correctly_refused": is_adv and refused,
            "latency_embed_ms": round(t_emb*1000, 1),
            "latency_vector_ms": round(t_vec*1000, 1),
            "latency_hybrid_ms": round(t_hyb*1000, 1),
            "latency_total_ms": round((t_emb+t_hyb)*1000, 1),
            "top_chunk_text": hc[0].get("text","")[:120] if hc else "",
        })

    avg = lambda l: round(sum(l)/max(len(l),1), 4) if l else 0

    in_scope = [r for r in results if r["type"] != "adversarial"]
    adversarial = [r for r in results if r["type"] == "adversarial"]
    all_lats = [r["latency_total_ms"] for r in results]
    sl = sorted(all_lats)

    # Hallucination: low sim AND low coverage on non-adversarial
    hall = sum(1 for r in in_scope if r["semantic_similarity"]<0.3 and r["key_term_coverage"]<0.3)

    # Confidence calibration
    high_conf = [r for r in in_scope if r["confidence_level"]=="high"]
    high_conf_correct = sum(1 for r in high_conf if (r.get("hybrid_recall5") or 0)>0)
    low_conf = [r for r in in_scope if r["confidence_level"]=="low"]
    low_conf_incorrect = sum(1 for r in low_conf if (r.get("hybrid_recall5") or 0)==0)

    metrics = {
        "dataset": label,
        "doc_id": doc_id,
        "queries": len(dataset),
        "retrieval": {
            "baseline_recall3": avg(b_r3), "baseline_recall5": avg(b_r5), "baseline_mrr": avg(b_mrrs),
            "hybrid_recall3": avg(h_r3), "hybrid_recall5": avg(h_r5), "hybrid_mrr": avg(h_mrrs),
        },
        "quality": {
            "avg_semantic_similarity": avg([r["semantic_similarity"] for r in in_scope]),
            "factual_sim": avg([r["semantic_similarity"] for r in in_scope if r["type"]=="factual"]),
            "conceptual_sim": avg([r["semantic_similarity"] for r in in_scope if r["type"]=="conceptual"]),
            "multihop_sim": avg([r["semantic_similarity"] for r in in_scope if r["type"]=="multi-hop"]),
            "key_term_coverage": avg([r["key_term_coverage"] for r in in_scope]),
            "hallucination_rate": round(hall/max(len(in_scope),1)*100, 1),
        },
        "adversarial": {
            "total": len(adversarial),
            "correct_refusals": sum(1 for r in adversarial if r["correctly_refused"]),
            "accuracy": round(sum(1 for r in adversarial if r["correctly_refused"])/max(len(adversarial),1)*100, 1),
        },
        "confidence_calibration": {
            "high_conf_total": len(high_conf),
            "high_conf_correct": high_conf_correct,
            "high_conf_accuracy": round(high_conf_correct/max(len(high_conf),1)*100, 1),
            "low_conf_total": len(low_conf),
            "low_conf_incorrect": low_conf_incorrect,
        },
        "latency": {
            "avg_embed_ms": round(np.mean(lats_embed), 1),
            "avg_vector_ms": round(np.mean(lats_vec), 1),
            "avg_hybrid_ms": round(np.mean(lats_hyb), 1),
            "avg_total_ms": round(np.mean(all_lats), 1),
            "p50_ms": round(sl[len(sl)//2], 1) if sl else 0,
            "p95_ms": round(sl[int(len(sl)*0.95)], 1) if sl else 0,
            "note": "Excludes LLM generation (API-dependent). Retrieval-only pipeline."
        },
    }
    return metrics, results


async def main():
    from app.rag.embedder import warmup
    warmup()

    ds = json.load(open(BASE/"data/dataset.json"))
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"\n{'='*70}\n  CREDIBILITY-FIXED EVALUATION\n{'='*70}")

    # === Dataset A: Python textbook ===
    print(f"\n  [Dataset A] Python Textbook (doc_11c024ccf162)")
    ma, ra = await evaluate_dataset("doc_11c024ccf162", ds, GROUND_TRUTH, "Python Textbook")

    # === Dataset B: check for second doc ===
    # Find second largest chunk file
    chunks_dir = Path("storage/chunks")
    chunk_files = sorted(
        [f for f in chunks_dir.glob("*.json") if "_bm25" not in f.name and "11c024ccf162" not in f.name],
        key=lambda f: f.stat().st_size, reverse=True
    )

    mb = None
    rb = None
    if chunk_files:
        doc_b = chunk_files[0].stem
        print(f"\n  [Dataset B] Second Document ({doc_b})")
        # For dataset B, use same queries but NO ground truth (measure what we can)
        gt_b = {}  # No GT for second doc - honest about this
        mb, rb = await evaluate_dataset(doc_b, ds[:30], gt_b, f"Document B ({doc_b})")

    # === Print Results ===
    def print_metrics(m, label):
        r = m["retrieval"]; q = m["quality"]; a = m["adversarial"]; l = m["latency"]; cc = m["confidence_calibration"]
        print(f"\n  [{label}]")
        print(f"  Baseline Recall@3: {r['baseline_recall3']}  |  Recall@5: {r['baseline_recall5']}  |  MRR: {r['baseline_mrr']}")
        print(f"  Hybrid  Recall@3: {r['hybrid_recall3']}  |  Recall@5: {r['hybrid_recall5']}  |  MRR: {r['hybrid_mrr']}")
        imp3 = round((r['hybrid_recall3']-r['baseline_recall3'])/max(r['baseline_recall3'],0.001)*100,1)
        imp5 = round((r['hybrid_recall5']-r['baseline_recall5'])/max(r['baseline_recall5'],0.001)*100,1)
        print(f"  Improvement: Recall@3 {imp3:+.1f}%  |  Recall@5 {imp5:+.1f}%")
        print(f"  Semantic Sim: {q['avg_semantic_similarity']}  |  Coverage: {q['key_term_coverage']}  |  Hallucination: {q['hallucination_rate']}%")
        print(f"  Not-Found: {a['accuracy']}% ({a['correct_refusals']}/{a['total']})")
        print(f"  Confidence: high={cc['high_conf_total']} ({cc['high_conf_accuracy']}% correct)")
        print(f"  Latency: embed={l['avg_embed_ms']}ms  vector={l['avg_vector_ms']}ms  hybrid={l['avg_hybrid_ms']}ms  total={l['avg_total_ms']}ms")
        print(f"  p50={l['p50_ms']}ms  p95={l['p95_ms']}ms  [{l['note']}]")

    print_metrics(ma, "Dataset A: Python Textbook")
    if mb: print_metrics(mb, "Dataset B: Second Document")

    # === Save everything ===
    print(f"\n{'='*70}\n  SAVING OUTPUTS\n{'='*70}")

    combined = {"timestamp": ts, "datasets": [ma]}
    if mb: combined["datasets"].append(mb)

    # Average across datasets
    if mb:
        combined["cross_dataset_average"] = {
            "hybrid_recall3": round((ma["retrieval"]["hybrid_recall3"]+(mb["retrieval"]["hybrid_recall3"] or 0))/2, 4),
            "hybrid_recall5": round((ma["retrieval"]["hybrid_recall5"]+(mb["retrieval"]["hybrid_recall5"] or 0))/2, 4),
            "avg_latency_ms": round((ma["latency"]["avg_total_ms"]+mb["latency"]["avg_total_ms"])/2, 1),
        }

    with open(BASE/"reports/metrics.json","w") as f: json.dump(combined, f, indent=2)
    with open(BASE/"logs/run.json","w") as f: json.dump({"dataset_a": ra, "dataset_b": rb}, f, indent=2, default=str)

    # CSV
    with open(BASE/"reports/metrics.csv","w",newline="") as f:
        w = csv.writer(f); w.writerow(["Dataset","Metric","Value"])
        for ds_m in combined["datasets"]:
            lbl = ds_m["dataset"]
            for cat in ["retrieval","quality","adversarial","latency"]:
                for k,v in ds_m[cat].items():
                    w.writerow([lbl, f"{cat}.{k}", v])

    with open(BASE/"reports/comparison.json","w") as f:
        json.dump({
            "baseline": {"recall3": ma["retrieval"]["baseline_recall3"], "recall5": ma["retrieval"]["baseline_recall5"], "mrr": ma["retrieval"]["baseline_mrr"]},
            "hybrid": {"recall3": ma["retrieval"]["hybrid_recall3"], "recall5": ma["retrieval"]["hybrid_recall5"], "mrr": ma["retrieval"]["hybrid_mrr"]},
            "ground_truth": "independent_manual_chunk_mapping",
        }, f, indent=2)

    with open(BASE/"reports/comparison.csv","w",newline="") as f:
        w = csv.writer(f); w.writerow(["System","Recall@3","Recall@5","MRR"])
        w.writerow(["Baseline",ma["retrieval"]["baseline_recall3"],ma["retrieval"]["baseline_recall5"],ma["retrieval"]["baseline_mrr"]])
        w.writerow(["Hybrid",ma["retrieval"]["hybrid_recall3"],ma["retrieval"]["hybrid_recall5"],ma["retrieval"]["hybrid_mrr"]])

    # === Failure Analysis (expanded) ===
    failures = []
    for r in ra:
        if r["type"] == "adversarial":
            if not r["correctly_refused"]:
                failures.append({**r, "failure_category": "false_positive_retrieval", "reason": f"Adversarial query not rejected. Vector score {r['top_vector_score']} above threshold 0.25."})
        elif r.get("hybrid_recall5") is not None and r["hybrid_recall5"] == 0:
            failures.append({**r, "failure_category": "retrieval_failure", "reason": "No gold-standard chunk found in top-5 hybrid results."})
        elif r["semantic_similarity"] < 0.3 and r["key_term_coverage"] < 0.3:
            failures.append({**r, "failure_category": "hallucination_risk", "reason": f"Low semantic sim ({r['semantic_similarity']}) and low key term coverage ({r['key_term_coverage']})."})
        elif r["semantic_similarity"] < 0.35:
            failures.append({**r, "failure_category": "semantic_mismatch", "reason": f"Retrieved relevant chunks but semantic similarity to expected answer is low ({r['semantic_similarity']})."})
        elif r["confidence_level"] == "high" and r.get("hybrid_recall5",1) == 0:
            failures.append({**r, "failure_category": "overconfident_miss", "reason": "High confidence but no relevant chunk retrieved."})

    with open(BASE/"reports/failures.md","w") as f:
        f.write("# Failure Analysis Report\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')} | **Total Failures**: {len(failures)} / {len(ra)} queries\n\n")
        f.write("## Summary\n\n| Category | Count | Description |\n|:---|:---:|:---|\n")
        cats = {}
        for fl in failures: cats[fl["failure_category"]] = cats.get(fl["failure_category"],0)+1
        descs = {"retrieval_failure":"No gold chunk in top-5","semantic_mismatch":"Low sim to expected answer","hallucination_risk":"Low sim + low coverage","false_positive_retrieval":"Adversarial not rejected","overconfident_miss":"High confidence but wrong"}
        for c,n in cats.items(): f.write(f"| {c} | {n} | {descs.get(c,'')} |\n")
        f.write(f"\n## Detailed Examples ({min(len(failures),15)} shown)\n\n")
        for fl in failures[:15]:
            f.write(f"### {fl['id']}: {fl['query'][:70]}\n")
            f.write(f"- **Type**: {fl['type']} | **Category**: {fl['failure_category']}\n")
            f.write(f"- **Reason**: {fl['reason']}\n")
            f.write(f"- **Semantic Similarity**: {fl['semantic_similarity']} | **Coverage**: {fl['key_term_coverage']}\n")
            f.write(f"- **Confidence**: {fl['confidence']} ({fl['confidence_level']})\n")
            f.write(f"- **Top Chunk**: {fl['top_chunk_text'][:100]}...\n")
            f.write(f"- **Gold Chunks**: {fl.get('gold_chunks',['N/A'])}\n\n")

    # Trust formula doc
    with open(BASE/"reports/trust_formula.md","w") as f:
        f.write("# Trust Layer Formula\n\n")
        f.write("## Confidence Score Computation\n\n```\nconfidence = 0.4 * norm_vector_score + 0.3 * norm_rrf_score + 0.3 * agreement_overlap\n```\n\n")
        f.write("### Components\n\n| Signal | Weight | Normalization | Source |\n|:---|:---:|:---|:---|\n")
        f.write("| Vector similarity | 0.4 | `min(score / 0.5, 1.0)` | FAISS cosine similarity |\n")
        f.write("| RRF fusion score | 0.3 | `min(score / 0.1, 1.0)` | Reciprocal Rank Fusion |\n")
        f.write("| Agreement overlap | 0.3 | `overlap(vec_top3, hybrid_top3) / 3` | Cross-system agreement |\n\n")
        f.write("### Thresholds\n\n| Level | Range | Action |\n|:---|:---:|:---|\n")
        f.write("| High | > 0.7 | Return answer with sources |\n")
        f.write("| Medium | 0.4 - 0.7 | Return answer with lower confidence warning |\n")
        f.write("| Low | < 0.4 | Return 'Not enough information in document' |\n\n")
        f.write(f"### Calibration (Dataset A)\n\n")
        f.write(f"- High-confidence queries: {ma['confidence_calibration']['high_conf_total']} ({ma['confidence_calibration']['high_conf_accuracy']}% actually correct)\n")
        f.write(f"- Low-confidence queries: {ma['confidence_calibration']['low_conf_total']}\n")

    # Figures
    with open(BASE/"figures/summary_table.md","w") as f:
        f.write("# Evaluation Results (Independent Ground Truth)\n\n")
        f.write("> Ground truth: manually mapped chunk IDs, independent of system output\n\n")
        f.write("## Core Metrics (Dataset A)\n\n| Metric | Value |\n|:---|:---:|\n")
        r = ma["retrieval"]; q = ma["quality"]
        f.write(f"| Recall@3 | {r['hybrid_recall3']} |\n| Recall@5 | {r['hybrid_recall5']} |\n| MRR | {r['hybrid_mrr']} |\n")
        f.write(f"| Semantic Similarity | {q['avg_semantic_similarity']} |\n| Key Term Coverage | {q['key_term_coverage']} |\n")
        f.write(f"| Hallucination Rate | {q['hallucination_rate']}% |\n| Not-Found Accuracy | {ma['adversarial']['accuracy']}% |\n")

    print(f"  All outputs saved to evaluation/")
    print(f"\n{'='*70}\n  DONE\n{'='*70}")
    return combined

asyncio.run(main())
