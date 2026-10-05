from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Identity,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Learner(Base):
    """An anonymised or fictional learner."""

    __tablename__ = "learners"
    __table_args__ = (
        CheckConstraint(
            "BTRIM(display_name) <> ''",
            name="learners_display_name_not_blank",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )

    assessment_results: Mapped[list["AssessmentResult"]] = relationship(
        back_populates="learner",
        passive_deletes=True,
    )
    interventions: Mapped[list["Intervention"]] = relationship(
        back_populates="learner",
        passive_deletes=True,
    )


class Assessment(Base):
    """An assessment completed by one or more learners."""

    __tablename__ = "assessments"
    __table_args__ = (
        CheckConstraint(
            "BTRIM(title) <> ''",
            name="assessments_title_not_blank",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    assessment_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )

    assessment_results: Mapped[list["AssessmentResult"]] = relationship(
        back_populates="assessment",
        passive_deletes=True,
    )


class Topic(Base):
    """A curriculum topic measured by assessments."""

    __tablename__ = "topics"
    __table_args__ = (
        CheckConstraint(
            "BTRIM(name) <> ''",
            name="topics_name_not_blank",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )

    assessment_results: Mapped[list["AssessmentResult"]] = relationship(
        back_populates="topic",
        passive_deletes=True,
    )
    interventions: Mapped[list["Intervention"]] = relationship(
        back_populates="topic",
        passive_deletes=True,
    )


class AssessmentResult(Base):
    """A learner's score for one topic in one assessment."""

    __tablename__ = "assessment_results"
    __table_args__ = (
        CheckConstraint(
            "score >= 0",
            name="assessment_results_score_nonnegative",
        ),
        CheckConstraint(
            "maximum_score > 0",
            name="assessment_results_maximum_positive",
        ),
        CheckConstraint(
            "score <= maximum_score",
            name="assessment_results_score_within_maximum",
        ),
        UniqueConstraint(
            "learner_id",
            "assessment_id",
            "topic_id",
            name="assessment_results_unique_entry",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )
    learner_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "learners.id",
            name="assessment_results_learner_fk",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    assessment_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "assessments.id",
            name="assessment_results_assessment_fk",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    topic_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "topics.id",
            name="assessment_results_topic_fk",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    score: Mapped[Decimal] = mapped_column(Numeric(7, 2), nullable=False)
    maximum_score: Mapped[Decimal] = mapped_column(
        Numeric(7, 2),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )

    learner: Mapped["Learner"] = relationship(
        back_populates="assessment_results",
    )
    assessment: Mapped["Assessment"] = relationship(
        back_populates="assessment_results",
    )
    topic: Mapped["Topic"] = relationship(
        back_populates="assessment_results",
    )


class Intervention(Base):
    """Support planned or delivered for a learner."""

    __tablename__ = "interventions"
    __table_args__ = (
        CheckConstraint(
            "BTRIM(summary) <> ''",
            name="interventions_summary_not_blank",
        ),
        CheckConstraint(
            "status IN ('planned', 'active', 'completed')",
            name="interventions_status_valid",
        ),
        CheckConstraint(
            """
            (status = 'completed' AND completed_at IS NOT NULL)
            OR
            (status <> 'completed' AND completed_at IS NULL)
            """,
            name="interventions_completion_consistent",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )
    learner_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "learners.id",
            name="interventions_learner_fk",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    topic_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "topics.id",
            name="interventions_topic_fk",
            ondelete="SET NULL",
        ),
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'planned'"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    learner: Mapped["Learner"] = relationship(
        back_populates="interventions",
    )
    topic: Mapped["Topic | None"] = relationship(
        back_populates="interventions",
    )