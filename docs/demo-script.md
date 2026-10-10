# TutorPulse Two-Minute Demonstration Script

## Purpose

This script presents TutorPulse clearly to an employer or interviewer in approximately two minutes.

It focuses on evidence: the deployed API, hosted PostgreSQL database, governed machine-learning inference, Docker packaging, automated testing and responsible-use boundaries.

## Before the demonstration

1. Open [the live API documentation](https://tutorpulse-s4oy.onrender.com/docs) at least two minutes before presenting.
2. Allow the Render Free service to wake if it has been inactive.
3. Confirm [deployment readiness](https://tutorpulse-s4oy.onrender.com/ready) reports that the database and model are ready.
4. Keep the GitHub repository and latest successful Actions run open in separate tabs.
5. Use only the fictional prediction example from the README.
6. Do not display Render or Neon environment variables, credentials or connection strings.

## 0:00-0:20 - Problem and purpose

Show the repository README.

Say:

> TutorPulse is a portfolio learning-outcomes and intervention API for tutors. I built it to demonstrate an end-to-end Python, SQL and machine-learning workflow, from relational data design through tested model inference and public deployment. It uses synthetic data only and is not presented as a production educational decision system.

## 0:20-0:40 - Architecture

Show the technology and live-demonstration sections of the README.

Say:

> The FastAPI application is packaged with Docker and deployed on Render. It connects securely to hosted PostgreSQL on Neon. GitHub Actions reproduces the data and model pipeline, runs 214 automated tests, builds the container and verifies the read-only demonstration behaviour.

## 0:40-1:00 - Health and hosted data

Open `/ready`, then return to Swagger UI and execute `GET /learners`.

Say:

> This readiness endpoint checks both the hosted database and the packaged model artifact. The learners endpoint is reading four fictional seed records from Neon rather than from my development computer.

Point out the `200` response and the names `Learner 001` to `Learner 004`.

## 1:00-1:30 - Governed model inference

In Swagger UI, open `POST /predictions/support-risk`, paste the fictional README example and execute it.

Say:

> This endpoint loads the selected logistic-regression pipeline and applies the frozen 18-feature contract. The result includes a probability, the fixed 0.38 decision threshold, artifact metadata and an explicit human-review requirement. It does not create an intervention or make an automatic educational decision.

Point out:

- `support_probability`;
- `predicted_needs_support`;
- `decision_threshold`;
- `model_name`;
- `artifact_schema_version`;
- `human_review_required`.

## 1:30-1:50 - Safety and engineering evidence

Show the README read-only explanation and the successful GitHub Actions run.

Say:

> The public demo deliberately blocks all database writes while allowing read-only exploration and stateless predictions. Secrets remain outside Git, prediction logs exclude feature payloads and the CI workflow tests the database, API, analysis, modelling and containerised deployment together.

## 1:50-2:00 - Honest limitations

Say:

> The model uses synthetic data, so its metrics do not demonstrate real educational effectiveness or fairness. The free hosting can also have a cold start. I documented those limitations rather than presenting the prototype as production-ready.

## Likely follow-up questions

### Why logistic regression?

It provided competitive validation performance and probability quality while remaining more interpretable than the random-forest comparison model.

### How did you prevent data leakage?

Features use only assessment results and interventions dated before each target assessment. Same-day and future information is excluded, and the dataset is split chronologically by complete assessment dates.

### Why is the decision threshold 0.38 instead of 0.5?

The threshold was selected using validation data only. It prioritises recall while requiring validation precision of at least 60%, reflecting the cost of missing fictional learners who may need support.

### How is the public database protected?

Deployment middleware permits safe read methods and stateless prediction requests but returns `403 Forbidden` for database mutations. The behaviour is covered by automated tests and a live verification check.

### What would be required before real use?

Representative data, lawful and secure data handling, authentication and authorisation, fairness evaluation, operational and drift monitoring, human-review processes, appeals, incident response and evidence of educational benefit would all be required.

### Why is there no conventional website?

TutorPulse is an API, database and machine-learning portfolio project. Swagger UI provides an interactive live interface to the API contract. A tutor-facing frontend is a clearly identified future enhancement.
