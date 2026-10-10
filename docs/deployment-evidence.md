# TutorPulse Deployment Evidence

## Purpose

This document records the evidence used to verify TutorPulse's Stage 8 public portfolio deployment.

The deployment demonstrates that the Python, FastAPI, PostgreSQL, machine-learning, Docker and continuous-integration components operate outside the development computer. It is a free, non-commercial portfolio demonstration and is not a production educational service.

## Verification record

| Item | Value |
|---|---|
| Verification date | 10 October 2026 |
| Repository | `OmarUddin06/tutorpulse` |
| Deployment branch | `16-deploy-validate-and-release-tutorpulse` |
| Verified deployment commit | `00ce552` |
| API host | Render Free web service |
| API region | Frankfurt, EU Central |
| Application packaging | Repository Dockerfile |
| Database host | Neon Free PostgreSQL |
| Database region | AWS Europe West 2, London |
| Database branch | `production` |
| Database | `neondb` |
| Public API | [https://tutorpulse-s4oy.onrender.com](https://tutorpulse-s4oy.onrender.com) |
| Interactive documentation | [https://tutorpulse-s4oy.onrender.com/docs](https://tutorpulse-s4oy.onrender.com/docs) |

No credentials, passwords or complete database connection strings are recorded in this document.

## Architecture verified

```text
GitHub repository
        |
        | automatic deployment from selected branch
        v
Render Free Docker web service
        |
        | TLS-protected pooled PostgreSQL connection
        v
Neon Free PostgreSQL
```

Render builds the repository Dockerfile. The image installs the model-serving dependencies, regenerates the reproducible synthetic analysis data, rebuilds the leakage-safe modelling dataset and packages the trusted logistic-regression artifact.

At application startup, TutorPulse validates the artifact before serving governed predictions. The application connects to Neon using a pooled connection string stored as a Render secret.

## Hosted database preparation

The committed migration and seed scripts were applied to Neon using a temporary direct connection held only in the local PowerShell process:

- `database/migrations/001_create_initial_schema.sql`
- `database/seed.sql`

The hosted database was verified to contain:

| Table | Rows |
|---|---:|
| `learners` | 4 |
| `topics` | 3 |
| `assessments` | 2 |
| `assessment_results` | 16 |
| `interventions` | 3 |

The seed records are fictional. No real learner information was uploaded.

## Live endpoint verification

| Check | Expected behaviour | Verified result |
|---|---|---|
| `GET /health` | Application process is available | `200 OK`, status `ok` |
| `GET /ready` | Database and model are ready | `200 OK`, all components `ready` |
| `GET /model/health` | Frozen artifact metadata is available | `200 OK`, logistic regression, schema `1`, threshold `0.38` |
| `GET /learners` | Fictional seed data is readable | `200 OK`, four fictional learners |
| `POST /learners` | Public database mutation is rejected | `403 Forbidden` |
| `GET /learners` after rejected write | Database remains unchanged | Four fictional learners remained |
| `POST /predictions/support-risk` | Governed inference remains available | `200 OK` with model metadata and human-review flag |
| `GET /docs` | Interactive API contract is available | Swagger UI loaded successfully |

The verified fictional prediction returned:

| Field | Result |
|---|---:|
| Support probability | `0.4121258981581896` |
| Predicted as needing support | `true` |
| Decision threshold | `0.38` |
| Academic support threshold | `60.0` |
| Model name | `logistic_regression` |
| Artifact schema version | `1` |
| Human review required | `true` |

The probability is a reproducible result for the supplied fictional example. It is not evidence about a real learner.

## Read-only demonstration boundary

The hosted service runs with `TUTORPULSE_DEMO_READ_ONLY=true`.

The boundary permits:

- `GET`, `HEAD` and `OPTIONS` requests;
- application, readiness and model-health checks;
- `POST /predictions/support-risk`, which does not change stored data.

It rejects all database-creating, updating and deleting requests with `403 Forbidden`.

The rejected learner-creation test and the unchanged four-row learner count demonstrate that the public deployment cannot alter the shared seed data through the API.

## Secret and privacy controls

The deployment was checked against the following controls:

- the pooled Neon connection string is stored only as a Render secret;
- database credentials are absent from Git, screenshots and documentation;
- temporary local connection environment variables were removed after database setup;
- the local clipboard was cleared after transferring the connection string;
- hosted records are synthetic;
- the public database API is read-only;
- prediction requests do not accept learner names or identifiers;
- prediction logs exclude raw feature payloads and database credentials;
- public prediction responses contain controlled metadata rather than internal stack traces.

## Automated evidence

The repository check verifies the complete application in GitHub Actions.

The successful workflow covers:

- PostgreSQL 18.6 integration testing;
- migration application;
- Python compilation;
- reproducible data generation;
- leakage-safe dataset preparation;
- non-interactive notebook execution;
- model training, comparison, evaluation and interpretation;
- trusted artifact creation and reload validation;
- the complete 214-test suite;
- Docker Compose validation;
- container image construction;
- containerised readiness and model-health checks;
- exact synthetic seed-record verification;
- rejection of a database mutation in read-only mode;
- a real governed containerised prediction.

The workflow associated with the live-deployment documentation commit `00ce552` completed successfully.

## Free-tier limitations

- The Render service sleeps after inactivity.
- The first request after a sleep may take approximately one minute.
- Free infrastructure does not provide production uptime guarantees.
- Render's local container filesystem is ephemeral.
- Persistent records therefore remain in Neon rather than in the container filesystem.
- The service has no custom domain.
- The project exposes an API and interactive documentation, not a custom graphical frontend.
- Full user authentication and authorisation are outside this portfolio deployment.
- The model was trained and evaluated using synthetic data.
- The deployment is unsuitable for real learner information or automatic educational decisions.

## External feedback status

An anonymised external demonstration request was sent on 10 October 2026.

Feedback is pending. It must not be marked complete until another person has attempted the supplied browser walkthrough and reported whether the instructions, read-only endpoint and fictional prediction were understandable and reliable.

No tester name, email address or other personal information will be recorded.

## Conclusion

The technical deployment checkpoint is complete. TutorPulse is publicly accessible, connects to hosted PostgreSQL, loads the governed model artifact, exposes health and readiness evidence, serves synthetic data, blocks database mutations and permits controlled model inference.

Stage 8 remains open until external feedback is recorded and acted on, the final pull request is merged, the release is tagged and the portfolio learning documents are finalised.
