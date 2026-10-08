import numpy as np
import pandas as pd
import pytest

from analysis.model_interpretation import (
    ModelInterpretationError,
    extract_logistic_coefficients,
    top_directional_coefficients,
)
from analysis.model_training import (
    build_logistic_pipeline,
)
from analysis.modelling import (
    IDENTIFIER_COLUMNS,
    MODEL_FEATURE_COLUMNS,
    NUMERIC_FEATURE_COLUMNS,
)


def _training_features() -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for index in range(10):
        needs_support = index % 2 == 1
        historical_average = (
            45.0
            if needs_support
            else 78.0
        )

        rows.append(
            {
                "topic_name": (
                    "Fractions"
                    if needs_support
                    else "Algebra"
                ),
                "maximum_score": 20.0,
                "prior_assessment_count": index + 1,
                "prior_result_count": (index + 1) * 4,
                "prior_average_percentage": (
                    historical_average
                ),
                "prior_minimum_percentage": (
                    historical_average - 10.0
                ),
                "prior_maximum_percentage": (
                    historical_average + 10.0
                ),
                "prior_support_count": (
                    3
                    if needs_support
                    else 0
                ),
                "prior_support_rate": (
                    0.7
                    if needs_support
                    else 0.1
                ),
                "previous_assessment_average_percentage": (
                    historical_average
                ),
                "days_since_previous_assessment": 14,
                "prior_same_topic_count": index + 1,
                "prior_same_topic_average_percentage": (
                    historical_average
                ),
                "prior_same_topic_latest_percentage": (
                    historical_average - 2.0
                ),
                "prior_same_topic_support_count": (
                    2
                    if needs_support
                    else 0
                ),
                "prior_intervention_count": (
                    2
                    if needs_support
                    else 0
                ),
                "prior_same_topic_intervention_count": (
                    1
                    if needs_support
                    else 0
                ),
                "prior_completed_intervention_count": (
                    1
                    if needs_support
                    else 0
                ),
            }
        )

    return pd.DataFrame(
        rows,
        columns=MODEL_FEATURE_COLUMNS,
    )


def _training_target() -> pd.Series:
    return pd.Series(
        [
            0,
            1,
            0,
            1,
            0,
            1,
            0,
            1,
            0,
            1,
        ],
        name="needs_support",
        dtype="int8",
    )


def test_fitted_model_exposes_all_transformed_features() -> None:
    model = build_logistic_pipeline()
    model.fit(
        _training_features(),
        _training_target(),
    )

    coefficients = extract_logistic_coefficients(model)

    expected_feature_count = (
        len(NUMERIC_FEATURE_COLUMNS) + 2
    )

    assert len(coefficients) == expected_feature_count
    assert set(coefficients["feature_type"]) == {
        "numerical",
        "categorical",
    }


def test_odds_ratios_match_exponentiated_coefficients() -> None:
    model = build_logistic_pipeline()
    model.fit(
        _training_features(),
        _training_target(),
    )

    coefficients = extract_logistic_coefficients(model)

    expected_odds_ratios = np.exp(
        coefficients["coefficient"]
    )

    assert np.allclose(
        coefficients["odds_ratio"],
        expected_odds_ratios,
    )


def test_coefficient_directions_match_signs() -> None:
    model = build_logistic_pipeline()
    model.fit(
        _training_features(),
        _training_target(),
    )

    coefficients = extract_logistic_coefficients(model)

    positive = coefficients.loc[
        coefficients["coefficient"] > 0
    ]
    negative = coefficients.loc[
        coefficients["coefficient"] < 0
    ]

    assert (
        positive["direction"]
        == "higher_support_odds"
    ).all()
    assert (
        negative["direction"]
        == "lower_support_odds"
    ).all()


def test_identifiers_are_not_interpreted_as_features() -> None:
    model = build_logistic_pipeline()
    model.fit(
        _training_features(),
        _training_target(),
    )

    coefficients = extract_logistic_coefficients(model)

    assert not (
        set(coefficients["feature"])
        & set(IDENTIFIER_COLUMNS)
    )


def test_strongest_coefficients_are_ordered() -> None:
    coefficient_table = pd.DataFrame(
        {
            "feature": [
                "positive_small",
                "positive_large",
                "negative_small",
                "negative_large",
            ],
            "coefficient": [
                0.2,
                1.2,
                -0.3,
                -1.5,
            ],
            "absolute_coefficient": [
                0.2,
                1.2,
                0.3,
                1.5,
            ],
            "odds_ratio": np.exp(
                [
                    0.2,
                    1.2,
                    -0.3,
                    -1.5,
                ]
            ),
            "direction": [
                "higher_support_odds",
                "higher_support_odds",
                "lower_support_odds",
                "lower_support_odds",
            ],
            "feature_type": [
                "numerical",
                "numerical",
                "numerical",
                "numerical",
            ],
        }
    )

    positive, negative = top_directional_coefficients(
        coefficient_table,
        count=2,
    )

    assert positive["feature"].tolist() == [
        "positive_large",
        "positive_small",
    ]
    assert negative["feature"].tolist() == [
        "negative_large",
        "negative_small",
    ]


def test_unfitted_model_is_rejected() -> None:
    model = build_logistic_pipeline()

    with pytest.raises(
        ModelInterpretationError,
        match="must be fitted",
    ):
        extract_logistic_coefficients(model)