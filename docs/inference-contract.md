# TutorPulse Model-Inference Contract

## Purpose

This document defines the governed model-inference contract for TutorPulse.

The inference API serves the logistic-regression pipeline selected during Stage 6. It converts validated, point-in-time learner-history features into a support-risk probability and a thresholded support flag.

The prediction is a decision-support signal for tutor review. It must not automatically create an intervention, label a learner or make an educational decision.

## Frozen model decision

The following Stage 6 decisions are fixed for Stage 7:

| Item | Value |
|---|---|
| Model | Logistic regression |
| Model metadata name | `logistic_regression` |
| Decision threshold | `0.38` |
| Academic support threshold | Result below `60%` |
| Artifact schema version | `1` |
| Feature count | `18` |
| Training data | Reproducible synthetic data |
| Intended user | A tutor reviewing possible support needs |
| Decision authority | Human tutor |

Stage 7 must not silently retrain the model, alter its feature contract or change its decision threshold.

Any future change to the model, feature set or threshold requires a separate evidence-backed modelling stage.

## Prediction endpoint

```http
POST /predictions/support-risk
```

The endpoint accepts one model-feature record and returns one support-risk prediction.

The request must not contain:

- learner names;
- learner identifiers;
- assessment identifiers;
- result identifiers;
- actual future result percentages;
- the `needs_support` target;
- intervention summaries;
- future information;
- information created on or after the target assessment date.

## Request body

The request contains the exact 18-feature Stage 6 contract.

```json
{
  "topic_name": "Algebra",
  "maximum_score": 20.0,
  "prior_assessment_count": 5,
  "prior_result_count": 18,
  "prior_average_percentage": 64.2,
  "prior_minimum_percentage": 42.0,
  "prior_maximum_percentage": 88.0,
  "prior_support_count": 6,
  "prior_support_rate": 0.3333,
  "previous_assessment_average_percentage": 61.5,
  "days_since_previous_assessment": 14,
  "prior_same_topic_count": 4,
  "prior_same_topic_average_percentage": 58.5,
  "prior_same_topic_latest_percentage": 62.0,
  "prior_same_topic_support_count": 2,
  "prior_intervention_count": 3,
  "prior_same_topic_intervention_count": 1,
  "prior_completed_intervention_count": 2
}
```

## Request-field definitions

| Field | Type | Validation |
|---|---|---|
| `topic_name` | string | Non-blank; maximum 100 characters |
| `maximum_score` | number | Greater than zero |
| `prior_assessment_count` | integer | Zero or greater |
| `prior_result_count` | integer | Zero or greater |
| `prior_average_percentage` | number or null | Between 0 and 100 |
| `prior_minimum_percentage` | number or null | Between 0 and 100 |
| `prior_maximum_percentage` | number or null | Between 0 and 100 |
| `prior_support_count` | integer | Zero or greater |
| `prior_support_rate` | number or null | Between 0 and 1 |
| `previous_assessment_average_percentage` | number or null | Between 0 and 100 |
| `days_since_previous_assessment` | integer or null | Zero or greater |
| `prior_same_topic_count` | integer | Zero or greater |
| `prior_same_topic_average_percentage` | number or null | Between 0 and 100 |
| `prior_same_topic_latest_percentage` | number or null | Between 0 and 100 |
| `prior_same_topic_support_count` | integer | Zero or greater |
| `prior_intervention_count` | integer | Zero or greater |
| `prior_same_topic_intervention_count` | integer | Zero or greater |
| `prior_completed_intervention_count` | integer | Zero or greater |

## Nullable historical values

Some percentage and time-gap fields may be `null` when no suitable earlier record exists.

The fitted pipeline contains its approved missing-value preprocessing. The API may pass valid missing historical values to the pipeline, but it must not invent replacement values inside the router.

Required count fields use zero when the count is genuinely zero.

## Cross-field validation

The request must reject internally inconsistent history.

The following conditions must hold:

- `prior_support_count` must not exceed `prior_result_count`.
- `prior_same_topic_count` must not exceed `prior_result_count`.
- `prior_same_topic_support_count` must not exceed `prior_same_topic_count`.
- `prior_same_topic_intervention_count` must not exceed `prior_intervention_count`.
- `prior_completed_intervention_count` must not exceed `prior_intervention_count`.
- When all three values exist, the prior average must be between the prior minimum and maximum.
- A same-topic average or latest percentage must not be supplied when `prior_same_topic_count` is zero.
- Unknown or extra request fields must be rejected.

These checks improve request consistency. They do not recreate training or feature engineering inside the API.

## Feature order

The model service must construct its pandas DataFrame in this exact order:

1. `topic_name`
2. `maximum_score`
3. `prior_assessment_count`
4. `prior_result_count`
5. `prior_average_percentage`
6. `prior_minimum_percentage`
7. `prior_maximum_percentage`
8. `prior_support_count`
9. `prior_support_rate`
10. `previous_assessment_average_percentage`
11. `days_since_previous_assessment`
12. `prior_same_topic_count`
13. `prior_same_topic_average_percentage`
14. `prior_same_topic_latest_percentage`
15. `prior_same_topic_support_count`
16. `prior_intervention_count`
17. `prior_same_topic_intervention_count`
18. `prior_completed_intervention_count`

The service must obtain this order from the shared model contract rather than maintaining an unrelated duplicate list.

The existing Stage 6 artifact validation remains the final safeguard against missing, unexpected or incorrectly ordered features.

## Successful response

A successful prediction uses HTTP status `200 OK`.

```json
{
  "support_probability": 0.7421,
  "predicted_needs_support": true,
  "decision_threshold": 0.38,
  "support_threshold": 60.0,
  "model_name": "logistic_regression",
  "artifact_schema_version": 1,
  "human_review_required": true
}
```

## Response-field definitions

| Field | Type | Meaning |
|---|---|---|
| `support_probability` | number | Estimated probability between 0 and 1 |
| `predicted_needs_support` | boolean | Whether the probability reaches the decision threshold |
| `decision_threshold` | number | Frozen probability threshold used for the binary flag |
| `support_threshold` | number | Academic percentage used to define the training target |
| `model_name` | string | Model name from validated artifact metadata |
| `artifact_schema_version` | integer | Version of the artifact contract |
| `human_review_required` | boolean | Always `true` |

The binary prediction must be calculated as:

```text
support_probability >= decision_threshold
```

The response must not imply that the prediction is a confirmed learner need.

## Model-artifact lifecycle

The model consists of:

```text
artifacts/models/tutorpulse_pipeline.joblib
artifacts/models/tutorpulse_metadata.json
```

The application must:

1. Attempt to load the trusted artifact once during FastAPI startup.
2. Validate the pipeline and metadata using the Stage 6 artifact code.
3. Store the validated model bundle in application state.
4. Reuse the loaded bundle across requests.
5. Avoid loading the joblib file for every request.
6. Avoid training or fitting a model during startup or inference.
7. Avoid modifying the saved artifact.

Only project-generated artifacts may be loaded.

Joblib uses Python pickle internally. Loading an untrusted joblib file can execute malicious code.

## Behaviour when the model is unavailable

The existing CRUD API should remain available when the model artifact is missing or invalid.

The application should retain a model-unavailable state and write a clear internal log message.

Requests to model-specific endpoints should return:

```http
503 Service Unavailable
```

Example:

```json
{
  "detail": "Model inference is unavailable"
}
```

The public response must not expose filesystem paths, stack traces or sensitive implementation information.

## Model-health endpoint

```http
GET /model/health
```

When the artifact is ready, return `200 OK`:

```json
{
  "status": "ready",
  "model_name": "logistic_regression",
  "artifact_schema_version": 1,
  "decision_threshold": 0.38
}
```

When the artifact is unavailable, return `503 Service Unavailable`:

```json
{
  "detail": "Model inference is unavailable"
}
```

The existing endpoint:

```http
GET /health
```

remains the basic application-process health check.

This separation distinguishes between:

- the FastAPI process being available; and
- the model being loaded and ready for inference.

## Error responses

| Situation | Status |
|---|---:|
| Valid prediction | `200 OK` |
| Model health while ready | `200 OK` |
| Invalid or missing request field | `422 Unprocessable Entity` |
| Unexpected request field | `422 Unprocessable Entity` |
| Inconsistent cross-field history | `422 Unprocessable Entity` |
| Missing or invalid model artifact | `503 Service Unavailable` |
| Unexpected inference failure | `500 Internal Server Error` |

Unexpected inference failures must be logged internally.

The public `500` response must use a generic message and must not expose stack traces or raw model input.

## Logging contract

Prediction logging exists for operational monitoring and debugging.

A prediction log may contain:

- event name;
- generated request identifier;
- model name;
- artifact schema version;
- decision threshold;
- predicted boolean outcome;
- rounded processing time;
- success or failure status.

Logs must not contain:

- learner names;
- learner identifiers;
- complete feature payloads;
- assessment-result values;
- intervention summaries;
- passwords;
- database connection strings;
- stack traces in public responses.

## Monitoring foundations

Stage 7 introduces monitoring foundations rather than claiming to provide full production monitoring.

The implementation and documentation should make it possible to monitor:

- application availability;
- model readiness;
- request counts;
- successful and failed predictions;
- prediction latency;
- predicted-positive rate;
- model and artifact versions;
- missing-value frequency;
- future input-distribution changes.

No production-monitoring claims should be made until TutorPulse is deployed to a real monitored environment.

## Testing requirements

Automated tests must verify:

- a valid request produces a probability between 0 and 1;
- the binary flag matches the frozen threshold;
- model metadata is returned;
- identical requests produce identical predictions;
- feature order follows the shared Stage 6 contract;
- missing fields are rejected;
- extra fields are rejected;
- invalid percentages, rates and counts are rejected;
- inconsistent count relationships are rejected;
- the model is not fitted during prediction;
- the ready model-health endpoint returns model information;
- a missing or invalid artifact produces `503`;
- the basic `/health` endpoint remains available;
- logging does not contain raw request payloads or learner identifiers;
- the endpoint appears in OpenAPI;
- Docker can generate and serve the trusted artifact;
- continuous integration verifies the inference workflow.

Tests should use dependency injection or controlled temporary artifacts. They must not rely on an untrusted external artifact.

## Responsible-use rules

TutorPulse inference must always be described as decision support.

The API must not:

- automatically create an intervention;
- decide that a learner definitely needs support;
- replace tutor judgement;
- make punitive decisions;
- claim that a feature caused the prediction;
- claim effectiveness with real learners;
- expose learner information through logs;
- use future or target information as input;
- silently change the threshold or model.

## Out of scope

The following work is outside Stage 7:

- public deployment;
- production hosting;
- real learner data;
- authentication and authorisation;
- automatic intervention creation;
- online retraining;
- changing the selected model;
- changing the decision threshold;
- a full production observability platform;
- claiming educational effectiveness.

## Definition of done

Stage 7 is complete when:

- the contract is implemented;
- the inference and model-health endpoints are tested;
- artifact loading is reproducible;
- privacy-aware logging exists;
- monitoring foundations are documented;
- a model card exists;
- Docker and CI verify the inference workflow;
- README and OpenAPI documentation are current;
- all automated tests pass;
- the pull request is merged.