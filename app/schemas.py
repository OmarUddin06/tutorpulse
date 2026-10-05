from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)


DisplayName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=100),
]

AssessmentTitle = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=200),
]

TopicName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=100),
]

InterventionSummary = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
]

PositiveId = Annotated[int, Field(gt=0)]

NonNegativeScore = Annotated[
    Decimal,
    Field(ge=0, max_digits=7, decimal_places=2),
]

PositiveMaximumScore = Annotated[
    Decimal,
    Field(gt=0, max_digits=7, decimal_places=2),
]

InterventionStatus = Literal["planned", "active", "completed"]


class LearnerCreate(BaseModel):
    display_name: DisplayName


class LearnerUpdate(BaseModel):
    display_name: DisplayName


class LearnerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    display_name: str
    created_at: datetime


class AssessmentCreate(BaseModel):
    title: AssessmentTitle
    assessment_date: date


class AssessmentUpdate(BaseModel):
    title: AssessmentTitle | None = None
    assessment_date: date | None = None


class AssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    assessment_date: date
    created_at: datetime


class TopicCreate(BaseModel):
    name: TopicName
    description: str | None = None


class TopicUpdate(BaseModel):
    name: TopicName | None = None
    description: str | None = None


class TopicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    created_at: datetime


class AssessmentResultCreate(BaseModel):
    learner_id: PositiveId
    assessment_id: PositiveId
    topic_id: PositiveId
    score: NonNegativeScore
    maximum_score: PositiveMaximumScore

    @model_validator(mode="after")
    def check_score_does_not_exceed_maximum(self) -> Self:
        if self.score > self.maximum_score:
            raise ValueError("score must not exceed maximum_score")

        return self


class AssessmentResultUpdate(BaseModel):
    score: NonNegativeScore | None = None
    maximum_score: PositiveMaximumScore | None = None

    @model_validator(mode="after")
    def check_supplied_scores(self) -> Self:
        if (
            self.score is not None
            and self.maximum_score is not None
            and self.score > self.maximum_score
        ):
            raise ValueError("score must not exceed maximum_score")

        return self


class AssessmentResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    learner_id: int
    assessment_id: int
    topic_id: int
    score: Decimal
    maximum_score: Decimal
    created_at: datetime


class InterventionCreate(BaseModel):
    learner_id: PositiveId
    topic_id: PositiveId | None = None
    summary: InterventionSummary
    status: InterventionStatus = "planned"
    completed_at: datetime | None = None

    @model_validator(mode="after")
    def check_completion_is_consistent(self) -> Self:
        if self.status == "completed" and self.completed_at is None:
            raise ValueError(
                "completed_at is required when status is completed"
            )

        if self.status != "completed" and self.completed_at is not None:
            raise ValueError(
                "completed_at must be empty unless status is completed"
            )

        return self


class InterventionUpdate(BaseModel):
    topic_id: PositiveId | None = None
    summary: InterventionSummary | None = None
    status: InterventionStatus | None = None
    completed_at: datetime | None = None


class InterventionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    learner_id: int
    topic_id: int | None
    summary: str
    status: InterventionStatus
    created_at: datetime
    completed_at: datetime | None