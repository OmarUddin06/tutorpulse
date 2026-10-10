# TutorPulse v0.2.0 Release Notes

## Release summary

TutorPulse v0.2.0 is the first public portfolio release of the complete project.

It brings together a PostgreSQL-backed FastAPI application, reproducible synthetic-data analysis, leakage-safe machine learning, governed model inference, automated testing, Docker packaging, continuous integration and a live read-only deployment.

The release is intended to demonstrate engineering and data-science skills. It is not a production educational service and must not be used with real learner data or for automatic educational decisions.

## Release details

| Item | Value |
|---|---|
| Version | `0.2.0` |
| Release date | 10 October 2026 |
| Release type | First public portfolio release |
| Live API | [https://tutorpulse-s4oy.onrender.com](https://tutorpulse-s4oy.onrender.com) |
| Interactive demonstration | [https://tutorpulse-s4oy.onrender.com/docs](https://tutorpulse-s4oy.onrender.com/docs) |
| Deployment | Render Free Docker service |
| Database | Neon Free PostgreSQL |

The free Render service sleeps after inactivity. Its first request may take approximately one minute while the service starts; later requests should respond normally.

## Highlights

### PostgreSQL and FastAPI application

- Relational PostgreSQL schema for fictional learners, topics, assessments, assessment results and interventions.
- FastAPI routes with Pydantic request and response validation.
- SQLAlchemy database access and transaction handling.
- Database constraints, migration and deterministic seed data.
- Automatically generated OpenAPI and Swagger documentation.

### Reproducible data and machine learning

- Reproducible synthetic data for 120 fictional learners, 24 assessments and 10,536 topic-level results.
- Leakage-safe feature engineering producing 10,056 chronological modelling rows.
- Comparison of a majority-class baseline, logistic regression and random forest.
- Logistic regression selected for its competitive performance and clearer interpretation.
- Frozen decision threshold of `0.38`, selected using validation data rather than the held-out test period.
- Synthetic held-out test results of `0.884` ROC AUC, `0.798` recall and `0.583` precision.

These figures describe reproducible synthetic data only. They do not demonstrate real-world accuracy, fairness or educational effectiveness.

### Governed model inference

- Frozen 18-feature prediction contract.
- Validated, versioned model artifact loaded once during application startup.
- Separate application-health, deployment-readiness and model-health endpoints.
- Prediction responses expose the model name, artifact version, probability and decision threshold.
- Every prediction states that human review is required.
- Privacy-aware logging excludes raw feature payloads and learner identifiers.

### Testing and continuous integration

- 214 automated tests, including 18 PostgreSQL integration tests.
- Coverage of API behaviour, validation, constraints, transactions, synthetic generation, feature engineering, model evaluation, artifact handling and deployment safety.
- GitHub Actions provisions PostgreSQL, applies the migration, regenerates data, executes the notebook, rebuilds the artifact and runs the complete suite.
- CI also builds the Docker image and verifies readiness, model health, exact seed data, blocked mutations and a real containerised prediction.

### Public portfolio deployment

- Docker application deployed to Render.
- Hosted PostgreSQL database deployed to Neon.
- Database credentials stored in provider secrets rather than Git.
- TLS-protected pooled database connection.
- Public database mutations rejected with `403 Forbidden`.
- Read-only resources and stateless governed predictions remain available.
- Synthetic demonstration records only.

## Live verification

The hosted release was verified to provide:

| Check | Verified result |
|---|---|
| `GET /health` | Application status `ok` |
| `GET /ready` | Application, database and model `ready` |
| `GET /model/health` | Logistic regression, artifact schema `1`, threshold `0.38` |
| `GET /learners` | Four fictional learners |
| `POST /learners` | Rejected with `403 Forbidden` |
| `POST /predictions/support-risk` | Governed prediction returned successfully |
| `GET /docs` | Interactive Swagger documentation available |

## External demonstration feedback

An anonymised external tester completed both the non-technical browser walkthrough and the technical PowerShell walkthrough.

The tester confirmed that:

- the interactive page opened successfully;
- the free-tier cold start took approximately 30 to 40 seconds;
- all instructions and PowerShell commands worked;
- four fictional learners were returned;
- deployment readiness reported that the database and model were ready; and
- the governed prediction completed successfully.

The main improvement requested was a clearer explanation of the prediction fields. The README now explains the probability, `0.38` decision threshold, separate `60%` academic support threshold, thresholded prediction and human-review requirement. The PowerShell example was also clarified to avoid a confusing output wrapper.

## Responsible-use boundary

TutorPulse is a learning and portfolio project built with synthetic data. The prediction is a decision-support signal for tutor review, not an automatic intervention, label or educational decision.

A real deployment would require representative data, authentication and authorisation, privacy and security review, fairness assessment, live monitoring, an outcome-feedback process and appropriate educational governance.

## Known limitations

- The model was trained and evaluated only on synthetic data.
- Free hosting can introduce a noticeable cold start and provides no production uptime guarantee.
- Swagger UI is the interactive interface; there is no custom tutor-facing frontend.
- The public demonstration is deliberately read-only.
- Full authentication and authorisation are not implemented.
- Operational drift and outcome monitoring are documented designs rather than a live monitoring platform.

## Supporting documentation

- [Deployment evidence](deployment-evidence.md)
- [External feedback](external-feedback.md)
- [Two-minute demonstration script](demo-script.md)
- [Portfolio and interview evidence](portfolio-evidence.md)
- [Model evaluation](model-evaluation.md)
- [Inference contract](inference-contract.md)
- [Model card](model-card.md)
- [Monitoring plan](model-monitoring.md)
