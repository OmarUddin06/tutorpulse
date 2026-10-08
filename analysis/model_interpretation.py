"""Interpret the fitted TutorPulse logistic-regression model.

Coefficients describe associations learned from synthetic training data.
They must not be interpreted as proof that a feature causes a learner
to need or not need support.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.exceptions import NotFittedError
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from analysis.model_data import (
    PreparedModelData,
    load_prepared_model_data,
)
from analysis.model_training import (
    build_logistic_pipeline,
)
from analysis.modelling import (
    IDENTIFIER_COLUMNS,
)


class ModelInterpretationError(ValueError):
    """Raised when a fitted model cannot be interpreted safely."""


def extract_logistic_coefficients(
    model: Pipeline,
) -> pd.DataFrame:
    """Return transformed feature names and logistic coefficients."""

    if "preprocessor" not in model.named_steps:
        raise ModelInterpretationError(
            "Model pipeline does not contain a preprocessor."
        )

    if "classifier" not in model.named_steps:
        raise ModelInterpretationError(
            "Model pipeline does not contain a classifier."
        )

    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["classifier"]

    if not isinstance(classifier, LogisticRegression):
        raise ModelInterpretationError(
            "Model classifier must be LogisticRegression."
        )

    try:
        feature_names = (
            preprocessor.get_feature_names_out()
        )
        coefficients = classifier.coef_
    except (AttributeError, NotFittedError) as error:
        raise ModelInterpretationError(
            "Model must be fitted before interpretation."
        ) from error

    if coefficients.shape[0] != 1:
        raise ModelInterpretationError(
            "Expected one binary logistic-regression coefficient row."
        )

    coefficient_values = coefficients[0]

    if len(feature_names) != len(coefficient_values):
        raise ModelInterpretationError(
            "Feature-name and coefficient counts do not match."
        )

    frame = pd.DataFrame(
        {
            "feature": feature_names,
            "coefficient": coefficient_values,
        }
    )

    frame["absolute_coefficient"] = (
        frame["coefficient"].abs()
    )
    frame["odds_ratio"] = np.exp(
        frame["coefficient"]
    )
    frame["direction"] = np.select(
        [
            frame["coefficient"] > 0,
            frame["coefficient"] < 0,
        ],
        [
            "higher_support_odds",
            "lower_support_odds",
        ],
        default="neutral",
    )
    frame["feature_type"] = np.where(
        frame["feature"].str.startswith(
            "topic_name_"
        ),
        "categorical",
        "numerical",
    )

    return frame.sort_values(
        by="absolute_coefficient",
        ascending=False,
        kind="stable",
    ).reset_index(drop=True)


def top_directional_coefficients(
    coefficient_table: pd.DataFrame,
    *,
    count: int = 10,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return the strongest positive and negative coefficients."""

    if count <= 0:
        raise ModelInterpretationError(
            "Coefficient count must be greater than zero."
        )

    required_columns = {
        "feature",
        "coefficient",
        "absolute_coefficient",
        "odds_ratio",
        "direction",
        "feature_type",
    }

    missing_columns = (
        required_columns
        - set(coefficient_table.columns)
    )

    if missing_columns:
        names = ", ".join(sorted(missing_columns))
        raise ModelInterpretationError(
            f"Coefficient table is missing columns: {names}"
        )

    positive = (
        coefficient_table.loc[
            coefficient_table["coefficient"] > 0
        ]
        .sort_values(
            by="coefficient",
            ascending=False,
            kind="stable",
        )
        .head(count)
        .reset_index(drop=True)
    )

    negative = (
        coefficient_table.loc[
            coefficient_table["coefficient"] < 0
        ]
        .sort_values(
            by="coefficient",
            ascending=True,
            kind="stable",
        )
        .head(count)
        .reset_index(drop=True)
    )

    return positive, negative


def fit_and_interpret(
    prepared_data: PreparedModelData,
) -> pd.DataFrame:
    """Fit the selected model and extract its coefficients."""

    model = build_logistic_pipeline()
    model.fit(
        prepared_data.train.features,
        prepared_data.train.target,
    )

    return extract_logistic_coefficients(model)


def _display_table(
    frame: pd.DataFrame,
) -> str:
    display = frame.loc[
        :,
        [
            "feature",
            "coefficient",
            "odds_ratio",
            "feature_type",
        ],
    ].copy()

    display["coefficient"] = (
        display["coefficient"].round(3)
    )
    display["odds_ratio"] = (
        display["odds_ratio"].round(3)
    )

    return display.to_string(index=False)


def main() -> None:
    """Print the strongest learned model associations."""

    prepared_data = load_prepared_model_data()
    coefficient_table = fit_and_interpret(
        prepared_data
    )

    prohibited_identifiers = (
        set(coefficient_table["feature"])
        & set(IDENTIFIER_COLUMNS)
    )

    if prohibited_identifiers:
        names = ", ".join(
            sorted(prohibited_identifiers)
        )
        raise ModelInterpretationError(
            "Identifier leakage detected in interpreted features: "
            f"{names}"
        )

    positive, negative = (
        top_directional_coefficients(
            coefficient_table,
            count=8,
        )
    )

    print(
        "Strongest associations with higher predicted "
        "support need"
    )
    print(_display_table(positive))
    print()
    print(
        "Strongest associations with lower predicted "
        "support need"
    )
    print(_display_table(negative))
    print()
    print(
        "Positive coefficients increase the model's predicted "
        "odds of needs_support=1. Negative coefficients decrease "
        "those predicted odds."
    )
    print(
        "Numerical features were standardised, so their "
        "coefficients approximately describe a one-standard-"
        "deviation change in the training data."
    )
    print(
        "These are associations learned from synthetic data, "
        "not evidence of causation."
    )


if __name__ == "__main__":
    main()