# TutorPulse Model Monitoring Plan

## Purpose

This document defines the monitoring foundations for the TutorPulse support-risk inference service.

The current project is a portfolio demonstration using synthetic data. It does not operate a real production monitoring platform.

The plan distinguishes between:

- signals already emitted by the application;
- metrics that could be derived from those signals;
- outcome monitoring requiring later verified results;
- governance actions when a problem is detected.

Monitoring must not turn the model into an automatic decision-maker.

## Monitoring principles

TutorPulse monitoring follows these principles:

1. protect learner privacy;
2. separate application health from model readiness;
3. monitor errors as well as successful predictions;
4. use aggregate measures wherever possible;
5. compare current behaviour with an approved baseline;
6. investigate changes before modifying the model;
7. retain human review;
8. never retrain or change thresholds automatically.

## Health endpoints

TutorPulse provides two different health checks.

### Application health

`GET /health`

This confirms that the FastAPI process is running.

It does not prove that model inference is available.

### Model health

`GET /model/health`

This confirms that:

- a trusted artifact was found;
- artifact validation succeeded;
- the model is loaded;
- model metadata is available;
- inference can be offered.

When the model is ready, the endpoint returns `200 OK`.

When the artifact is unavailable or invalid, it returns `503 Service Unavailable`.

Docker uses the model-health endpoint so that the API container is not marked healthy unless governed inference is ready.

## Existing application events

### Artifact loaded

Emitted during startup when the trusted artifact loads successfully.

Permitted fields include:

- model name;
- artifact schema version.

### Artifact unavailable

Emitted when the artifact cannot be loaded or validated.

Permitted fields include:

- controlled error category.

The log must not expose artifact contents or sensitive exception details to an API user.

### Prediction completed

Emitted after a successful prediction.

The event contains:

- generated request identifier;
- model name;
- artifact schema version;
- decision threshold;
- thresholded support flag;
- inference duration in milliseconds.

### Prediction unavailable

Emitted when a request arrives while the model is unavailable.

The event contains:

- generated request identifier;
- inference duration in milliseconds.

### Prediction failed

Emitted when an unexpected prediction failure occurs.

The event contains:

- generated request identifier;
- controlled error category;
- inference duration in milliseconds.

The public error response remains generic.

## Privacy rules

Prediction monitoring must not log:

- learner names;
- learner identifiers;
- assessment identifiers;
- result identifiers;
- raw request bodies;
- individual feature values;
- actual assessment results;
- intervention summaries;
- free-text educational notes;
- exception messages containing user data;
- authentication credentials;
- database passwords.

The generated request identifier connects operational events belonging to one request. It must not be replaced with a learner identifier.

Raw support probabilities are not required in normal application logs. Aggregate probability analysis would need an approved monitoring process.

## Operational metrics

### Availability

Track:

- application-health success rate;
- model-health success rate;
- time spent unavailable;
- artifact-load failures;
- container restart count.

An unavailable model must not return an improvised fallback prediction.

### Request volume

Track:

- prediction requests per minute;
- prediction requests per hour;
- unusual increases or decreases in traffic.

Traffic changes may indicate integration failure, misuse or a genuine change in demand.

### Error rate

Track response counts for:

- `200 OK`;
- `422 Unprocessable Entity`;
- `500 Internal Server Error`;
- `503 Service Unavailable`.

A high `422` rate may indicate that a client no longer follows the feature contract.

A `500` response represents an unexpected inference failure.

A `503` response means governed inference is unavailable.

### Latency

Track:

- median inference duration;
- 95th-percentile inference duration;
- maximum inference duration;
- latency by response category.

Latency can be calculated from the application’s existing `duration_ms` field.

### Prediction distribution

Track aggregate counts of:

- predictions marked as requiring support;
- predictions not marked as requiring support;
- predicted-support rate over time.

A change may indicate:

- a changed topic mix;
- changed learner history;
- client behaviour changes;
- upstream data problems;
- feature drift;
- model degradation.

A change must be investigated rather than automatically treated as model failure.

## Input monitoring

Input monitoring should use aggregates and approved summaries rather than raw learner records.

Track:

- topic proportions;
- missing-value rates;
- numerical-feature averages and quantiles;
- zero-history and low-history frequencies;
- schema-validation failures;
- unexpected categories;
- values close to validation boundaries.

The frozen 18-feature contract must remain unchanged until a governed update is approved.

## Drift monitoring

Stage 6 already demonstrated temporal changes:

- training support rate: 37.2%;
- validation support rate: 30.0%;
- test support rate: 26.5%;
- learner-history depth increased over time.

Possible drift checks include:

- topic-distribution changes;
- support-flag rate changes;
- historical-result-count changes;
- prior-average-percentage changes;
- intervention-count changes;
- missing-value-rate changes;
- unseen categorical values.

A drift alert requests investigation. It is not permission to retrain automatically.

## Outcome monitoring

True performance cannot be calculated at prediction time because the future assessment result is not yet known.

When an approved verified result later becomes available, a controlled process could compare:

- the historical prediction;
- the eventual below-threshold label.

That process could calculate:

- precision;
- recall;
- balanced accuracy;
- F1 score;
- ROC AUC;
- average precision;
- calibration;
- false-positive count;
- false-negative count;
- performance by approved operational subgroup.

This evaluation must occur in a governed environment. Learner identifiers must not be added to ordinary application logs to create the feedback loop.

## Subgroup monitoring

Synthetic evaluation found different recall levels across topics, with Statistics producing the lowest validation recall.

If real evaluation were authorised, performance should be reviewed across:

- topic;
- learner-history depth;
- relevant time periods;
- other lawful and approved groups.

Demographic fairness cannot currently be evaluated because sensitive demographic attributes are unavailable.

The absence of those attributes must not be presented as proof of fairness.

## Initial investigation triggers

These are proposed starting triggers rather than proven production objectives:

| Signal | Initial trigger |
|---|---|
| Model health | Any sustained `503` response |
| Prediction failures | `500` responses above 1% over 15 minutes |
| Validation failures | `422` responses above 10% over 15 minutes |
| Latency | 95th percentile above 500 ms over 15 minutes |
| Prediction distribution | Support-flag rate changes by more than 10 percentage points from the approved recent baseline |
| Delayed recall | Recall below 0.70 on a sufficiently sized verified sample |
| Delayed precision | Precision below 0.50 on a sufficiently sized verified sample |
| Delayed ROC AUC | ROC AUC below 0.80 on a sufficiently sized verified sample |
| Subgroup difference | Recall difference greater than 0.15 between sufficiently sized approved groups |

Small samples must not trigger confident performance conclusions.

These thresholds should be reviewed if genuine production evidence becomes available.

## Incident response

When a monitoring trigger is reached:

1. record the time and affected model version;
2. confirm whether the signal is genuine;
3. check application and model health separately;
4. check recent deployments and configuration changes;
5. inspect controlled error categories;
6. check input validation and upstream feature construction;
7. compare aggregate input distributions with the baseline;
8. decide whether predictions should be temporarily disabled;
9. document the investigation and decision;
10. create a reviewed corrective change if required.

If model integrity is uncertain, the safe state is model unavailability rather than an unvalidated prediction.

## Rollback approach

A rollback must use a previously validated and trusted application/model combination.

Before rollback:

- verify the artifact source;
- verify its metadata;
- confirm the feature contract;
- confirm the decision threshold;
- run the artifact checks;
- record why rollback is required.

The service must never load an untrusted joblib artifact.

## Retraining policy

TutorPulse does not perform automatic or online retraining.

Possible retraining triggers include:

- sustained performance degradation;
- material input drift;
- a changed modelling question;
- a changed assessment process;
- an approved feature-contract change;
- evidence that the current threshold no longer provides the intended trade-off.

Retraining requires a separate reviewed workflow containing leakage-safe preparation, validation-based selection, a final test evaluation and updated documentation.

## Threshold review

The deployed decision threshold is fixed at `0.38`.

It must not be changed because of a single incident or small sample.

A threshold review requires:

- sufficient verified outcomes;
- precision-recall analysis;
- review of tutor workload;
- review of false-negative consequences;
- subgroup evaluation;
- written approval;
- updated metadata and documentation.

## Review cadence

For a real deployment, an initial schedule could include:

- continuous service-health monitoring;
- weekly operational review;
- monthly drift review;
- performance review when sufficient verified outcomes exist;
- immediate review after a serious incident;
- full governance review before any model or threshold change.

The portfolio project documents this approach but does not claim these reviews are operational.

## Current implementation status

Implemented:

- separate application and model-health endpoints;
- startup artifact validation;
- controlled unavailable state;
- random request identifiers;
- inference-duration logging;
- model-version logging;
- threshold logging;
- thresholded-outcome logging;
- generic public error responses;
- tests ensuring feature payloads are not logged;
- Docker health verification against model health;
- reproducible artifact creation.

Documented foundations:

- operational metrics;
- drift monitoring;
- delayed outcome monitoring;
- subgroup review;
- investigation triggers;
- incident response;
- rollback;
- threshold review;
- retraining governance.

Not implemented:

- a hosted metrics backend;
- dashboards;
- paging or alert delivery;
- long-term prediction storage;
- a real learner-outcome feedback loop;
- automatic retraining.

## Related documentation

- `docs/model-card.md`
- `docs/inference-contract.md`
- `docs/model-evaluation.md`
- `docs/modelling-scope.md`