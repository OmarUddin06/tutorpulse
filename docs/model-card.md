# TutorPulse Model Card

## Document status

| Item | Value |
|---|---|
| Model-card version | 1.0 |
| Last updated | 8 October 2026 |
| Project | TutorPulse |
| Model | Logistic regression |
| Model metadata name | `logistic_regression` |
| Artifact schema version | `1` |
| Decision threshold | `0.38` |
| Academic support threshold | Result below `60%` |
| Feature count | 18 |
| Data source | Reproducible synthetic data |
| Current status | Portfolio demonstration |
| Decision authority | Human tutor |

## Summary

TutorPulse uses logistic regression to estimate the probability that a learner’s next assessment result will fall below the project’s 60% support threshold.

The model uses only information that would be available before the target assessment.

It returns:

- a support-risk probability;
- a thresholded support flag;
- the frozen decision threshold;
- the academic support threshold;
- model-version metadata;
- confirmation that human review is required.

The prediction is a decision-support signal. It is not a diagnosis, a confirmed support need or an automatic educational decision.

## Intended purpose

The model demonstrates how TutorPulse could help a tutor prioritise assessment results for review.

The intended workflow is:

1. construct an approved point-in-time feature record;
2. submit it to the inference API;
3. show the prediction to an authorised tutor;
4. allow the tutor to review the available evidence;
5. let the tutor decide whether follow-up is appropriate.

The model must not create an intervention automatically.

## Intended users

The intended user is a tutor or authorised education professional who:

- understands that the output is probabilistic;
- can review the learner’s wider context;
- remains responsible for any decision;
- can disregard an unsuitable prediction;
- can identify circumstances not represented by the model.

The API may also be used by developers and testers working on the TutorPulse demonstration.

## Out-of-scope uses

The model must not be used to:

- make automatic educational decisions;
- deny access to teaching or support;
- assign grades;
- rank learners publicly;
- label a learner permanently;
- discipline a learner;
- infer protected characteristics;
- replace professional judgement;
- claim that a learner definitely needs support;
- make causal claims about why an outcome occurred;
- process real learners without additional validation and governance.

## Modelling question

The modelling question is:

> Using only a learner’s assessment history available before a future assessment, can TutorPulse predict whether their next assessment result will fall below an agreed support threshold?

The target is defined as `needs_support = result_percentage < 60`.

This target identifies a below-threshold result. It does not prove that a learner requires a particular intervention.

## Model architecture

The selected model is logistic regression inside a scikit-learn pipeline.

The pipeline performs:

1. approved feature selection;
2. numerical missing-value imputation;
3. numerical feature scaling;
4. categorical missing-value imputation;
5. one-hot encoding of the topic;
6. logistic-regression probability estimation.

Keeping preprocessing and classification together ensures that the same transformations are applied during training, evaluation and inference.

## Approved feature contract

The model accepts exactly 18 features:

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

The inference contract rejects unexpected fields.

The model input must not contain:

- learner names;
- learner identifiers;
- assessment identifiers;
- result identifiers;
- the future result percentage;
- the target label;
- intervention summaries;
- information created on or after the target assessment date.

## Training data

The model was trained using entirely synthetic TutorPulse data.

The generated data mirrors the project’s PostgreSQL structure:

- learners;
- topics;
- assessments;
- assessment results;
- interventions.

The reproducible generator creates:

- 120 fictional learners;
- 4 topics;
- 24 assessments;
- 10,536 assessment results;
- 1,075 interventions.

After point-in-time feature construction, the modelling dataset contains 10,056 rows.

Synthetic data allows the complete workflow to be demonstrated without using real learner information. It does not establish that the model will perform similarly on real educational data.

## Dataset splits

The data is divided chronologically:

| Split | Rows | Date period | Support rate |
|---|---:|---|---:|
| Training | 5,668 | 29 January–16 July 2025 | 37.2% |
| Validation | 2,168 | 30 July–24 September 2025 | 30.0% |
| Test | 2,220 | 8 October–3 December 2025 | 26.5% |

The splits have separate purposes:

- training fits model parameters;
- validation compares models and selects the threshold;
- test provides one final evaluation.

The chronological design reduces future-information leakage and better represents predicting later results from earlier history.

## Model selection

The project evaluated:

- a majority-class dummy baseline;
- logistic regression;
- random forest.

Logistic regression was retained because it provided:

- competitive validation performance;
- slightly better precision than the random forest;
- better ROC AUC;
- better average precision;
- a lower Brier score;
- reproducible training;
- clearer interpretation.

The small performance difference did not justify selecting the more complex model.

## Threshold selection

The common default probability threshold of 0.50 was not accepted automatically.

The threshold was selected using validation data only. The selection rule prioritised recall while requiring validation precision of at least 0.60.

The selected threshold is `0.38`.

Lowering the threshold identifies more potentially below-threshold results. This reduces false negatives while increasing false positives.

The threshold must not be changed silently. Any change requires documented evaluation and a new governed artifact.

## Final test performance

| Metric | Test result |
|---|---:|
| Accuracy | 0.795 |
| Balanced accuracy | 0.796 |
| Precision | 0.583 |
| Recall | 0.798 |
| F1 score | 0.674 |
| ROC AUC | 0.884 |
| Average precision | 0.744 |
| Specificity | 0.795 |
| True negatives | 1,297 |
| False positives | 335 |
| False negatives | 119 |
| True positives | 469 |

The model identified 469 of the 588 below-threshold test results.

Test precision fell below the validation constraint of 0.60. This result demonstrates that later performance can differ from validation performance and must not be hidden.

## Error considerations

### False positives

A false positive means the model flags a result for review even though the eventual result is not below 60%.

Possible effects include:

- unnecessary tutor review;
- increased workload;
- avoidable concern if the result is communicated poorly.

A false positive must not create an intervention automatically.

### False negatives

A false negative means the model does not flag a result that later falls below 60%.

This is the more important educational error because a possible support need may be missed.

The selected threshold prioritises recall to reduce false negatives, but it cannot eliminate them.

## Topic-level observations

Validation recall varied across the synthetic topics:

| Topic | Validation recall |
|---|---:|
| Algebra | 0.812 |
| Fractions | 0.878 |
| Geometry | 0.786 |
| Statistics | 0.692 |

Statistics had the lowest validation recall and would require particular monitoring.

These figures describe synthetic data and are not evidence about real subjects or learners.

## Interpretability

Logistic-regression coefficients describe conditional associations learned from synthetic training data.

They do not demonstrate that a feature causes a learner to need support.

Correlated features can also make individual coefficient signs appear counterintuitive. Interpretation must remain cautious and contextual.

## Fairness and equity

The synthetic dataset does not contain sensitive demographic characteristics.

Consequently:

- demographic fairness has not been evaluated;
- equal performance across protected groups cannot be claimed;
- the absence of protected characteristics does not prove fairness;
- proxy effects may still exist;
- topic-level analysis is not a substitute for demographic fairness analysis.

Any real-world use would require appropriate lawful data governance and subgroup evaluation.

## Privacy

The inference request excludes direct learner and assessment identifiers.

Prediction logs must not contain:

- learner names;
- learner identifiers;
- raw feature payloads;
- assessment records;
- intervention summaries;
- free-text educational notes.

The API creates a random request identifier for operational tracing. It is not a learner identifier.

## Human oversight

Every prediction is intended for human review.

A tutor should consider:

- circumstances not represented by the model;
- possible data-quality problems;
- incomplete learner history;
- the consequences of acting or not acting;
- whether the suggested review is proportionate;
- the learner’s broader educational context.

The tutor remains the decision-maker.

## Deployment

The trusted artifact contains:

- `artifacts/models/tutorpulse_pipeline.joblib`
- `artifacts/models/tutorpulse_metadata.json`

The artifact is built reproducibly during the Docker build and loaded once during FastAPI startup.

The API provides:

- `GET /model/health`
- `POST /predictions/support-risk`

The Docker container is only considered healthy when the model-health endpoint reports that the validated artifact is ready.

## Artifact security

Joblib uses Python pickle internally.

Only artifacts produced by the trusted TutorPulse workflow may be loaded. An artifact from an untrusted source could execute malicious code during deserialisation.

The loader validates:

- required artifact files;
- metadata structure;
- artifact schema version;
- model name;
- feature contract;
- decision threshold;
- pipeline type;
- prediction consistency after reloading.

## Monitoring requirements

Monitoring should cover:

- model availability;
- prediction error rate;
- request latency;
- request volume;
- validation-error rate;
- predicted-support rate;
- topic distribution;
- numerical feature distributions;
- missing-value rates;
- delayed precision and recall when verified outcomes become available.

Monitoring must use aggregate information wherever possible and follow `docs/model-monitoring.md`.

## Retraining and change control

The service does not retrain online.

Retraining or replacement requires:

1. an explicit modelling question;
2. an approved dataset;
3. leakage-safe feature construction;
4. chronological evaluation;
5. candidate-model comparison;
6. validation-based threshold selection;
7. one final test evaluation;
8. updated documentation;
9. a new artifact version when appropriate;
10. code review and automated verification.

A production incident must not be handled by silently changing the decision threshold.

## Known limitations

The current model has important limitations:

- all data is synthetic;
- generated patterns may not represent real educational behaviour;
- educational effectiveness has not been demonstrated;
- demographic fairness cannot currently be evaluated;
- the target is derived from assessment score rather than verified support need;
- false positives and false negatives occur;
- test precision was below the validation constraint;
- distributions changed across chronological periods;
- coefficients are associative rather than causal;
- the test split was accessed earlier than ideal during development;
- there is no production feedback loop or observability platform.

## Reproducibility

The workflow is reproduced by running:

1. `python -m analysis.synthetic_data`
2. `python -m analysis.modelling_dataset`
3. `python -m analysis.model_artifact`

Automated tests verify the data contract, modelling workflow, artifact validation and inference service.

## Related documentation

- `docs/modelling-scope.md`
- `docs/model-evaluation.md`
- `docs/inference-contract.md`
- `docs/model-monitoring.md`