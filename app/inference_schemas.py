"""Validation schemas for governed TutorPulse model inference."""

from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)


InferenceTopicName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=100,
    ),
]

PositiveNumber = Annotated[
    float,
    Field(gt=0),
]

NonNegativeInteger = Annotated[
    int,
    Field(ge=0),
]

PositiveInteger = Annotated[
    int,
    Field(gt=0),
]

Percentage = Annotated[
    float,
    Field(ge=0, le=100),
]

Probability = Annotated[
    float,
    Field(ge=0, le=1),
]


class SupportRiskRequest(BaseModel):
    """The frozen 18-feature Stage 6 inference contract."""

    model_config = ConfigDict(
        extra="forbid",
    )

    topic_name: InferenceTopicName
    maximum_score: PositiveNumber

    prior_assessment_count: NonNegativeInteger
    prior_result_count: NonNegativeInteger

    prior_average_percentage: Percentage | None = None
    prior_minimum_percentage: Percentage | None = None
    prior_maximum_percentage: Percentage | None = None

    prior_support_count: NonNegativeInteger
    prior_support_rate: Probability | None = None

    previous_assessment_average_percentage: (
        Percentage | None
    ) = None

    days_since_previous_assessment: (
        NonNegativeInteger | None
    ) = None

    prior_same_topic_count: NonNegativeInteger
    prior_same_topic_average_percentage: (
        Percentage | None
    ) = None
    prior_same_topic_latest_percentage: (
        Percentage | None
    ) = None
    prior_same_topic_support_count: NonNegativeInteger

    prior_intervention_count: NonNegativeInteger
    prior_same_topic_intervention_count: (
        NonNegativeInteger
    )
    prior_completed_intervention_count: (
        NonNegativeInteger
    )

    @model_validator(mode="after")
    def validate_history_consistency(self) -> Self:
        """Reject internally inconsistent history features."""

        if (
            self.prior_support_count
            > self.prior_result_count
        ):
            raise ValueError(
                "prior_support_count must not exceed "
                "prior_result_count"
            )

        if (
            self.prior_same_topic_count
            > self.prior_result_count
        ):
            raise ValueError(
                "prior_same_topic_count must not exceed "
                "prior_result_count"
            )

        if (
            self.prior_same_topic_support_count
            > self.prior_same_topic_count
        ):
            raise ValueError(
                "prior_same_topic_support_count must not "
                "exceed prior_same_topic_count"
            )

        if (
            self.prior_same_topic_intervention_count
            > self.prior_intervention_count
        ):
            raise ValueError(
                "prior_same_topic_intervention_count must "
                "not exceed prior_intervention_count"
            )

        if (
            self.prior_completed_intervention_count
            > self.prior_intervention_count
        ):
            raise ValueError(
                "prior_completed_intervention_count must "
                "not exceed prior_intervention_count"
            )

        minimum = self.prior_minimum_percentage
        average = self.prior_average_percentage
        maximum = self.prior_maximum_percentage

        if (
            minimum is not None
            and maximum is not None
            and minimum > maximum
        ):
            raise ValueError(
                "prior_minimum_percentage must not exceed "
                "prior_maximum_percentage"
            )

        if (
            minimum is not None
            and average is not None
            and average < minimum
        ):
            raise ValueError(
                "prior_average_percentage must not be below "
                "prior_minimum_percentage"
            )

        if (
            maximum is not None
            and average is not None
            and average > maximum
        ):
            raise ValueError(
                "prior_average_percentage must not exceed "
                "prior_maximum_percentage"
            )

        if self.prior_same_topic_count == 0:
            if (
                self.prior_same_topic_average_percentage
                is not None
            ):
                raise ValueError(
                    "prior_same_topic_average_percentage "
                    "requires prior_same_topic_count to be "
                    "greater than zero"
                )

            if (
                self.prior_same_topic_latest_percentage
                is not None
            ):
                raise ValueError(
                    "prior_same_topic_latest_percentage "
                    "requires prior_same_topic_count to be "
                    "greater than zero"
                )

        return self


class SupportRiskResponse(BaseModel):
    """A governed support-risk prediction response."""

    model_config = ConfigDict(
        extra="forbid",
    )

    support_probability: Probability
    predicted_needs_support: bool
    decision_threshold: Probability
    support_threshold: Percentage

    model_name: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=1,
        ),
    ]

    artifact_schema_version: PositiveInteger
    human_review_required: Literal[True] = True

    @model_validator(mode="after")
    def validate_threshold_decision(self) -> Self:
        """Ensure the flag agrees with the probability."""

        expected_decision = (
            self.support_probability
            >= self.decision_threshold
        )

        if (
            self.predicted_needs_support
            != expected_decision
        ):
            raise ValueError(
                "predicted_needs_support does not match "
                "support_probability and decision_threshold"
            )

        return self


class ModelHealthResponse(BaseModel):
    """Metadata returned when model inference is ready."""

    model_config = ConfigDict(
        extra="forbid",
    )

    status: Literal["ready"] = "ready"

    model_name: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=1,
        ),
    ]

    artifact_schema_version: PositiveInteger
    decision_threshold: Probability