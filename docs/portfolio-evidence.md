# TutorPulse Portfolio and Interview Evidence

## Purpose

This document translates the completed TutorPulse engineering work into concise, evidence-backed material for CVs, applications, GitHub profiles and interviews.

Use only the statements that fit the available space and the role being targeted. Do not present synthetic model results as evidence of real educational effectiveness.

## Two-sentence project pitch

TutorPulse is an end-to-end learning-outcomes and intervention API built with Python, FastAPI, PostgreSQL and SQLAlchemy, with a reproducible machine-learning workflow for identifying fictional assessment results that may require tutor review. I designed the relational schema, implemented and tested the API, engineered leakage-safe chronological features, compared classification models, served a governed model through Docker and deployed a read-only demonstration using Render and Neon.

## Short spoken introduction

> TutorPulse started as a SQL-backed FastAPI service for recording anonymised assessment results and interventions. I expanded it into an end-to-end portfolio system covering database design, automated testing, reproducible analysis, leakage-safe machine learning, model governance, Docker, GitHub Actions and a free public deployment. The model uses synthetic data only, and every prediction remains a decision-support signal requiring human review.

## GitHub repository description

Suggested short description:

> End-to-end Python, FastAPI, PostgreSQL and machine-learning portfolio project with leakage-safe modelling, 214 automated tests, Docker, GitHub Actions and a governed read-only deployment.

Suggested repository topics:

- `python`
- `fastapi`
- `postgresql`
- `sqlalchemy`
- `machine-learning`
- `scikit-learn`
- `docker`
- `github-actions`
- `pytest`
- `data-analysis`
- `model-governance`

## CV project heading

**TutorPulse - Python, PostgreSQL and Machine-Learning Portfolio Project**

Suggested technology line:

**Python, FastAPI, PostgreSQL, SQLAlchemy, Pydantic, pandas, scikit-learn, pytest, Docker, GitHub Actions, Render, Neon**

## CV bullet bank

Choose three or four bullets that best match the job description.

- Designed and implemented a FastAPI and PostgreSQL service for managing fictional learners, topics, assessments, topic-level results and tutor interventions, with relational constraints, validation and complete CRUD routes.
- Built a reproducible synthetic-data and leakage-safe feature-engineering pipeline producing 10,056 chronological modelling rows from 120 fictional learners, 24 assessments and 10,536 topic-level results.
- Trained and compared a majority-class baseline, logistic regression and random forest; selected an interpretable logistic model that achieved `0.884` ROC AUC and `0.798` recall on a held-out synthetic chronological test period.
- Prevented temporal leakage by excluding same-day and future results and interventions, splitting by complete assessment dates and protecting the feature contract with automated regression tests.
- Implemented governed inference through an 18-feature Pydantic contract, frozen decision threshold, validated model artifact, privacy-aware logging and explicit human-review metadata.
- Created a 214-test automated suite covering API behaviour, schemas, PostgreSQL constraints, transactions, synthetic generation, feature engineering, model evaluation, artifact handling, deployment configuration and public-demo safety.
- Built a GitHub Actions workflow that provisions PostgreSQL, applies migrations, regenerates data, executes the analysis notebook, rebuilds the model artifact, runs all tests and verifies a real Docker prediction.
- Packaged the application and reproducible model artifact with Docker and deployed a read-only public demonstration on Render backed by Neon PostgreSQL, with secrets kept outside Git and readiness checks covering both database and model availability.
- Documented the modelling scope, evaluation, inference contract, model card, monitoring plan, deployment architecture, known limitations and responsible-use requirements.

## Evidence behind the numbers

| Claim | Repository evidence |
|---|---|
| 214 automated tests | Complete pytest suite and GitHub Actions repository check |
| 18 PostgreSQL integration tests | `tests/integration/` |
| 120 fictional learners | Default synthetic-data generator manifest |
| 24 fictional assessments | Default synthetic-data generator manifest |
| 10,536 fictional assessment results | Default generated relational dataset |
| 10,056 modelling rows | Leakage-safe prepared dataset |
| `0.884` test ROC AUC | `docs/model-evaluation.md` |
| `0.798` test recall | `docs/model-evaluation.md` |
| 18 governed inference features | `docs/inference-contract.md` |
| Live Docker deployment | `docs/deployment-evidence.md` |

All dataset sizes and model metrics relate to reproducible synthetic data.

## Skills demonstrated

| Skill | Evidence |
|---|---|
| Python | Application, analysis, modelling, tests and deployment server |
| SQL | Schema migration, seed data, reporting queries and hosted database setup |
| PostgreSQL | Constraints, relationships, transactions, migration and Neon deployment |
| API development | FastAPI routes, Pydantic validation, OpenAPI documentation and error handling |
| Data engineering | Reproducible relational generation, joins, validation and feature preparation |
| Machine learning | Baseline comparison, preprocessing, chronological evaluation and interpretation |
| Leakage prevention | Point-in-time feature rules and automated same-day/future exclusion tests |
| Testing | Unit, API, modelling, integration, deployment and container checks |
| Docker | Multi-component local environment and reproducible inference image |
| Continuous integration | End-to-end GitHub Actions workflow with PostgreSQL and Docker verification |
| Cloud deployment | Render web service, Neon PostgreSQL, TLS and environment-secret configuration |
| Responsible AI | Model card, human review, privacy-aware logging and documented limitations |
| Git and GitHub | Issue-based branches, incremental commits, pull requests and CI-gated merges |

## STAR example 1 - Preventing temporal data leakage

### Situation

TutorPulse needed to predict whether a future fictional assessment result would fall below the support threshold. A random row split or careless aggregation could expose the model to information that would not exist at prediction time.

### Task

Create a reproducible modelling dataset whose features use only information available before each target assessment.

### Action

I defined the prediction point immediately before the target assessment, excluded same-day and future results and interventions, calculated historical features separately for each target row and split the data by complete chronological assessment dates. I added regression tests covering same-day exclusion, future exclusion, intervention timing, prohibited target fields and non-overlapping date periods.

### Result

The pipeline produced 10,056 leakage-safe synthetic modelling rows with reproducible train, validation and test periods. Model selection and threshold selection used training and validation data, while the final chronological test period remained held out.

## STAR example 2 - Building a safe public demonstration

### Situation

The portfolio needed a live deployment, but an anonymous public API with unrestricted CRUD operations could allow visitors to change the shared demonstration database.

### Task

Deploy the complete service for free while preserving useful API and model demonstrations without exposing secrets or allowing database mutations.

### Action

I deployed the Docker application to Render and PostgreSQL to Neon, stored the pooled database URL as a platform secret and added a read-only deployment boundary. Safe read methods and stateless predictions remain available, while creating, updating and deleting database records return `403 Forbidden`. I added readiness checks, deployment tests and CI verification of both the blocked write and permitted prediction.

### Result

The public service successfully reads four fictional hosted records, loads the validated logistic-regression artifact and serves governed predictions. A live mutation attempt returned `403`, and the learner count remained unchanged.

## STAR example 3 - Diagnosing a continuous-integration failure

### Situation

The first deployment-safety CI check failed even though the application and containers were healthy.

### Task

Determine whether the failure represented a genuine deployment fault or an incorrect test assumption.

### Action

I inspected the failing workflow step and compared its expected learner names with the committed seed data. The check expected names beginning with `Synthetic`, while the actual deterministic seed records were `Learner 001` through `Learner 004`. I corrected the assertion to verify the exact authoritative seed records and reran the workflow.

### Result

The repository check passed and now protects the intended behaviour with a more precise assertion. This demonstrated the importance of testing against the real data contract rather than an outdated assumption.

## STAR example 4 - Choosing an interpretable model and threshold

### Situation

TutorPulse required a support-risk model that performed better than a trivial baseline while remaining understandable and suitable for human review.

### Task

Compare candidate models and select a decision threshold without using the held-out test period for tuning.

### Action

I trained a majority-class baseline and logistic-regression pipeline, added a random-forest comparison and evaluated discrimination, probability quality and thresholded metrics on validation data. I selected a `0.38` threshold using validation data only, prioritising recall while requiring precision of at least 60%. Logistic regression was retained because it offered competitive performance, reproducibility and clearer interpretation.

### Result

On the synthetic chronological test period, the selected model achieved `0.884` ROC AUC, `0.798` recall and `0.583` precision. I documented that these metrics do not establish real-world educational performance.

## Likely interview questions

### Why did you use PostgreSQL instead of SQLite?

The project demonstrates production-relevant relational behaviour: foreign keys, check constraints, unique constraints, transaction isolation and concurrent service access. PostgreSQL also allowed the same database engine to be used locally, in integration tests and through Neon.

### Why did you use FastAPI?

FastAPI provides typed request validation through Pydantic, automatic OpenAPI documentation and straightforward dependency injection for database sessions. Those features made the API contract visible and testable.

### How did you stop the model from seeing future information?

Every historical feature is calculated relative to one target assessment date. Only records from earlier dates are permitted; same-day and future results and interventions are excluded. The split boundaries also use complete assessment dates rather than random rows.

### Why did you not use accuracy alone?

The target classes are imbalanced and the costs of false negatives and false positives differ. I therefore evaluated recall, precision, F1, balanced accuracy, ROC AUC, average precision, specificity, confusion counts and Brier score.

### Why is the threshold `0.38`?

It was selected on validation data to maximise recall subject to precision of at least 60%. The threshold is stored with the artifact and returned in prediction responses so the decision rule remains visible.

### Why was logistic regression selected over random forest?

The logistic model had competitive validation performance and probability quality, was reproducible and offered clearer coefficient-based interpretation. For a tutor-review decision-support prototype, transparency was an important design consideration.

### How is the model deployed reproducibly?

The Docker build regenerates the synthetic data, prepares the leakage-safe dataset and creates the validated model artifact. The application loads that trusted artifact once during startup and checks its schema, feature contract and metadata.

### How are credentials protected?

Connection strings and passwords are stored in ignored local environment files or provider secret settings. They are not committed to Git, placed in documentation or returned by API responses.

### Why is the public deployment read-only?

The service has no full user-authentication system, so allowing anonymous mutations would make the shared demonstration unreliable. Read-only middleware preserves safe exploration while still allowing stateless model predictions.

### What would you build next?

For a portfolio enhancement, I would add a small tutor-facing frontend. Before any real educational use, priorities would instead be authentication and authorisation, representative data, fairness assessment, monitoring, governance, appeals and security review.

## Honest limitations to state in interviews

- All learners, results, interventions and model patterns are synthetic.
- Model metrics do not demonstrate real-world accuracy, fairness or educational benefit.
- The support threshold is a transparent project assumption rather than a universal standard.
- The deployment uses free infrastructure and may have a noticeable cold start.
- Swagger UI is the interactive interface; there is no custom tutor-facing frontend.
- The public demonstration is deliberately read-only.
- Full user authentication and authorisation are not implemented.
- Operational drift and outcome monitoring are documented designs rather than a live production monitoring system.

## Portfolio links

- Repository: [https://github.com/OmarUddin06/tutorpulse](https://github.com/OmarUddin06/tutorpulse)
- Live API documentation: [https://tutorpulse-s4oy.onrender.com/docs](https://tutorpulse-s4oy.onrender.com/docs)
- Deployment readiness: [https://tutorpulse-s4oy.onrender.com/ready](https://tutorpulse-s4oy.onrender.com/ready)
- Model health: [https://tutorpulse-s4oy.onrender.com/model/health](https://tutorpulse-s4oy.onrender.com/model/health)
- Demonstration script: `docs/demo-script.md`
- Deployment evidence: `docs/deployment-evidence.md`

## Usage guidance

For a one-page CV, use the technology line and three or four role-relevant bullets. For an application form, combine the short spoken introduction with one STAR example. During an interview, demonstrate the live API first and use the repository documentation to answer deeper questions.

Keep every claim tied to the repository evidence and always qualify the data and model results as synthetic.
