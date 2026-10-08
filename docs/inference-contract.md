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