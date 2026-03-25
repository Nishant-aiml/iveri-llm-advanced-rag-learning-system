"""SQLAlchemy database models and engine setup."""
from datetime import datetime, timezone
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean,
    DateTime, Index, Text
)
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True, index=True)
    username = Column(String, unique=True, nullable=True, index=True)
    password_hash = Column(String, nullable=True)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    streak = Column(Integer, default=0)
    daily_xp = Column(Integer, default=0)
    last_active = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_users_daily_xp", "daily_xp"),
    )


class Document(Base):
    __tablename__ = "documents"

    doc_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    filename = Column(String, nullable=True)  # Original uploaded filename
    file_hash = Column(String, nullable=False, index=True)
    status = Column(String, default="processing")  # processing | ready | failed
    error_message = Column(Text, nullable=True)
    processing_stage = Column(String, default="uploaded")  # uploaded|parsed|structured|embedded|indexed
    processed_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_documents_doc_id", "doc_id"),
        Index("ix_documents_file_hash", "file_hash"),
    )


class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    doc_id = Column(String, nullable=False, index=True)
    quiz_type = Column(String, default="quiz")  # quiz | mock_test
    score = Column(Integer, default=0)
    total = Column(Integer, default=0)
    accuracy = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Leaderboard(Base):
    __tablename__ = "leaderboard"

    user_id = Column(String, primary_key=True)
    daily_xp = Column(Integer, default=0)
    last_reset = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_leaderboard_user_id", "user_id"),
    )


class TopicScore(Base):
    """Per-user per-topic accuracy tracking — persistent personalization."""
    __tablename__ = "topic_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    topic = Column(String, nullable=False)
    correct = Column(Integer, default=0)
    total = Column(Integer, default=0)
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_topic_scores_user_topic", "user_id", "topic", unique=True),
    )


class EvaluationReport(Base):
    """Persisted evaluation results for proof."""
    __tablename__ = "evaluation_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String, nullable=False, index=True)
    baseline_recall = Column(Float, default=0.0)
    hybrid_recall = Column(Float, default=0.0)
    reranked_recall = Column(Float, default=0.0)
    baseline_mrr = Column(Float, default=0.0)
    hybrid_mrr = Column(Float, default=0.0)
    reranked_mrr = Column(Float, default=0.0)
    not_found_accuracy = Column(Float, default=0.0)
    reranker_improvement_rate = Column(Float, default=0.0)
    chunk_quality_score = Column(Float, default=0.0)
    avg_retrieval_ms = Column(Float, default=0.0)
    avg_rerank_ms = Column(Float, default=0.0)
    avg_llm_ms = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class CourseNode(Base):
    """Unified hierarchical knowledge tree per document."""
    __tablename__ = "course_nodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String, nullable=False, index=True)
    node_id = Column(String, nullable=False)
    parent_node_id = Column(String, nullable=True, index=True)
    level = Column(String, nullable=False)  # subject | unit | topic | subtopic
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    page = Column(Integer, default=1)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_course_nodes_doc_node", "doc_id", "node_id", unique=True),
        Index("ix_course_nodes_doc_parent_order", "doc_id", "parent_node_id", "sort_order"),
    )


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
