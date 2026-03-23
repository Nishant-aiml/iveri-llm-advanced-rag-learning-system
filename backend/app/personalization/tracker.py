"""Personalization — SQLite-backed, real accuracy, trend tracking.
Survives server restarts. Connected to quiz generation.
"""
import logging
import time
from datetime import datetime, timezone
from collections import defaultdict
from app.database import SessionLocal, TopicScore

logger = logging.getLogger(__name__)

# In-memory cache (synced with SQLite)
_topic_cache: dict[str, dict[str, dict]] = defaultdict(
    lambda: defaultdict(lambda: {"correct": 0, "total": 0, "history": []})
)
_cache_loaded: set[str] = set()


def _load_from_db(user_id: str):
    """Load user's topic scores from SQLite into cache."""
    if user_id in _cache_loaded:
        return
    db = SessionLocal()
    try:
        rows = db.query(TopicScore).filter(TopicScore.user_id == user_id).all()
        for row in rows:
            _topic_cache[user_id][row.topic] = {
                "correct": row.correct,
                "total": row.total,
                "history": [],
            }
        _cache_loaded.add(user_id)
    except Exception as e:
        logger.error(f"Failed to load topic scores for {user_id}: {e}")
    finally:
        db.close()


def _save_to_db(user_id: str, topic: str, correct: int, total: int):
    """Upsert topic score to SQLite."""
    db = SessionLocal()
    try:
        row = db.query(TopicScore).filter(
            TopicScore.user_id == user_id,
            TopicScore.topic == topic
        ).first()
        if row:
            row.correct = correct
            row.total = total
            row.last_updated = datetime.now(timezone.utc)
        else:
            row = TopicScore(
                user_id=user_id,
                topic=topic,
                correct=correct,
                total=total,
            )
            db.add(row)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to save topic score: {e}")
        db.rollback()
    finally:
        db.close()


def record_topic_result(user_id: str, topic: str, correct: bool):
    """Record a quiz/question result for a specific topic."""
    _load_from_db(user_id)
    data = _topic_cache[user_id][topic]
    data["total"] += 1
    if correct:
        data["correct"] += 1
    data["history"].append({"timestamp": time.time(), "correct": correct})
    if len(data["history"]) > 50:
        data["history"] = data["history"][-50:]

    # Persist to SQLite
    _save_to_db(user_id, topic, data["correct"], data["total"])

    logger.debug(
        f"Topic result: user={user_id}, topic={topic}, correct={correct}, "
        f"accuracy={data['correct']}/{data['total']}"
    )


def record_quiz_results(user_id: str, quiz_details: list[dict]):
    """Record results from a quiz, mapping questions to topics."""
    for detail in quiz_details:
        # Use topic from quiz metadata (set by LLM) — fallback to extraction
        topic = detail.get("topic") or _extract_topic_from_question(detail.get("question", ""))
        record_topic_result(user_id, topic, detail.get("is_correct", False))


def get_weak_topics(user_id: str, threshold: float = 0.6) -> list[dict]:
    """Get topics where user accuracy is below threshold."""
    _load_from_db(user_id)
    if user_id not in _topic_cache:
        return []

    weak = []
    for topic, scores in _topic_cache[user_id].items():
        if scores["total"] < 2:
            continue
        topic_accuracy = scores["correct"] / scores["total"]
        if topic_accuracy < threshold:
            trend = _compute_trend(scores["history"])
            weak.append({
                "topic": topic,
                "accuracy": round(topic_accuracy, 2),
                "correct": scores["correct"],
                "total": scores["total"],
                "trend": trend,
                "recommendation": _get_recommendation(topic, topic_accuracy, trend),
            })

    weak.sort(key=lambda x: x["accuracy"])
    return weak


def get_all_topic_scores(user_id: str) -> list[dict]:
    """Get all topic scores for a user with trend tracking."""
    _load_from_db(user_id)
    if user_id not in _topic_cache:
        return []

    results = []
    for topic, scores in _topic_cache[user_id].items():
        topic_accuracy = scores["correct"] / max(scores["total"], 1)
        trend = _compute_trend(scores["history"])

        if topic_accuracy >= 0.8:
            status = "strong"
        elif topic_accuracy >= 0.6:
            status = "moderate"
        else:
            status = "weak"

        results.append({
            "topic": topic,
            "accuracy": round(topic_accuracy, 2),
            "correct": scores["correct"],
            "total": scores["total"],
            "trend": trend,
            "status": status,
        })

    results.sort(key=lambda x: x["accuracy"])
    return results


def get_weak_topics_for_quiz(user_id: str) -> list[str]:
    """Get weak topic names for adaptive quiz generation."""
    weak = get_weak_topics(user_id)
    return [w["topic"] for w in weak[:3]]


def _compute_trend(history: list[dict]) -> dict:
    """Compute improvement trend: improving | declining | stable."""
    if len(history) < 4:
        return {"direction": "stable", "improvement": 0.0}

    mid = len(history) // 2
    first_half = history[:mid]
    second_half = history[mid:]

    first_acc = sum(1 for h in first_half if h["correct"]) / max(len(first_half), 1)
    second_acc = sum(1 for h in second_half if h["correct"]) / max(len(second_half), 1)

    improvement = second_acc - first_acc

    if improvement > 0.1:
        direction = "improving"
    elif improvement < -0.1:
        direction = "declining"
    else:
        direction = "stable"

    return {"direction": direction, "improvement": round(improvement, 2)}


def _get_recommendation(topic: str, accuracy: float, trend: dict) -> str:
    """Generate study recommendation based on accuracy and trend."""
    direction = trend.get("direction", "stable")

    if accuracy < 0.3:
        if direction == "declining":
            return f"⚠️ '{topic}' needs urgent attention — use Mentor Mode for guided review."
        return f"Review '{topic}' fundamentals — use Mentor Mode for step-by-step learning."
    elif accuracy < 0.5:
        if direction == "improving":
            return f"📈 '{topic}' is improving — keep practicing with flashcards."
        return f"Practice more on '{topic}' — use flashcards and quizzes."
    else:
        if direction == "improving":
            return f"✅ Almost mastering '{topic}' — try harder questions."
        return f"Review '{topic}' — focus on subtopics you're missing."


def _extract_topic_from_question(question: str) -> str:
    """Extract topic from question text using keyword matching."""
    question_lower = question.lower()
    topic_keywords = {
        "neural network": "Neural Networks",
        "cnn": "Neural Networks",
        "convolutional": "Neural Networks",
        "gradient": "Optimization",
        "backpropagation": "Optimization",
        "learning rate": "Optimization",
        "overfitting": "Regularization",
        "regularization": "Regularization",
        "dropout": "Regularization",
        "supervised": "Learning Types",
        "unsupervised": "Learning Types",
        "reinforcement": "Learning Types",
        "classification": "Classification",
        "regression": "Regression",
        "clustering": "Clustering",
        "decision tree": "Tree Models",
        "random forest": "Tree Models",
        "activation": "Neural Networks",
        "loss function": "Optimization",
    }
    for keyword, topic in topic_keywords.items():
        if keyword in question_lower:
            return topic
    return "General"
