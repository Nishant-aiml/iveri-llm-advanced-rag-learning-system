"""Leaderboard — daily ranking with cache and reset."""
import logging
from datetime import datetime, timezone
from app.state import leaderboard_cache
from app.database import SessionLocal, Leaderboard, User

logger = logging.getLogger(__name__)


def load_leaderboard_cache():
    """Load leaderboard from DB into cache on startup."""
    db = SessionLocal()
    try:
        entries = db.query(Leaderboard).all()
        for entry in entries:
            leaderboard_cache[entry.user_id] = entry.daily_xp
        logger.info(f"Loaded {len(entries)} leaderboard entries into cache")
    finally:
        db.close()


def get_leaderboard(limit: int = 20) -> list[dict]:
    """Get sorted leaderboard from cache, with usernames."""
    sorted_entries = sorted(
        leaderboard_cache.items(),
        key=lambda x: x[1],
        reverse=True
    )[:limit]

    # Fetch usernames from DB
    db = SessionLocal()
    try:
        user_ids = [uid for uid, _ in sorted_entries]
        users = db.query(User).filter(User.id.in_(user_ids)).all()
        username_map = {u.id: u.username or u.id for u in users}
    finally:
        db.close()

    return [
        {
            "rank": i + 1,
            "user_id": uid,
            "username": username_map.get(uid, uid),
            "daily_xp": xp,
        }
        for i, (uid, xp) in enumerate(sorted_entries)
    ]


def reset_daily_leaderboard():
    """Reset all daily XP (called once per 24h)."""
    db = SessionLocal()
    try:
        db.query(Leaderboard).update({Leaderboard.daily_xp: 0})
        db.query(User).update({User.daily_xp: 0})
        db.commit()

        leaderboard_cache.clear()
        logger.info("Daily leaderboard reset complete")
    except Exception as e:
        logger.error(f"Leaderboard reset failed: {e}")
        db.rollback()
    finally:
        db.close()
