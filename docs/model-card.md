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

TutorPulse uses a logistic-regression model to estimate the probability that a learner's next assessment result will fall below the project's 60% support threshold.

The model uses only information that would be available before the target assessment. It returns:

- a support-risk probability;
- a thresholded support flag;
- the frozen decision threshold;
- the academic support threshold;
- model-version metadata;
- a reminder that human review is required.

The prediction is a decision-support signal. It is not a diagnosis, confirmed support need or automatic educational decision.

## Intended purpose

The model demonstrates how TutorPulse could help a tutor prioritise assessment results for review.

Its intended workflow is:

1. construct an approved point-in-time feature record;
2. request a prediction from the inference API;
3. display the result to a tutor;
4. allow the tutor to review the available evidence;
5. let the tutor decide whether any follow-up is appropriate.

The model must not create an intervention automatically.

## Intended users

The intended user is a tutor or authorised education professional who:

- understands that the output is probabilistic;
- can review the learner's broader context;
- remains responsible for any decision;
- can disregard an unsuitable prediction;
- can identify circumstances not represented by the model.

The API may also be used by developers and testers working on the TutorPulse demonstration.

## Out-of-scope uses

The model must not be used to:

- make automatic educational decisions;
- deny a learner access to teaching or support;
- assign grades;
- rank learners publicly;
- label a learner permanently;
- discipline a learner;
- infer protected characteristics;
- replace professional judgement;
- claim that a learner definitely needs support;
- predict outcomes for real learners without further validation and governance;
- make causal claims about why an outcome may occur.

## Modelling question

The modelling question is:

> Using only a learner's assessment history available before a future assessment, can TutorPulse predict whether their next assessment result will fall below an agreed support threshold?

The target is:

```text
needs_support = result_percentage < 60