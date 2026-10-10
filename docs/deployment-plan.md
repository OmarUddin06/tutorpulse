# TutorPulse Deployment Plan

## Purpose

This document defines the Stage 8 deployment approach for TutorPulse.

The deployment is a portfolio demonstration proving that the Python, FastAPI, PostgreSQL, machine-learning, Docker and continuous-integration components can operate outside the development computer.

TutorPulse is not being launched as a commercial or production educational service.

## Deployment goals

The deployment must:

- remain free to operate within the selected providers' published free-tier limits;
- build the application from the repository Dockerfile;
- use a hosted PostgreSQL database;
- preserve the governed Stage 7 model artifact and inference contract;
- use synthetic demonstration data only;
- keep credentials and connection strings outside Git;
- prevent public users from modifying stored demonstration data;
- continue allowing governed support-risk predictions;
- expose sufficient health information for deployment verification;
- document limitations honestly.

## Selected architecture

| Component | Selected service | Plan |
|---|---|---|
| Source control | GitHub | Existing free account |
| API hosting | Render web service | Free |
| Application packaging | Docker | Repository Dockerfile |
| PostgreSQL hosting | Neon | Free |
| TLS | Render and Neon managed TLS | Included |
| Continuous integration | GitHub Actions | Existing workflow |
| Domain | Render-provided `onrender.com` address | Free |

No custom domain or paid infrastructure is required.

## Why Render is used for the API

Render supports:

- deployment from a connected GitHub repository;
- builds from a repository Dockerfile;
- environment variables and secrets;
- HTTPS through a managed `onrender.com` address;
- HTTP health checks;
- deployment logs;
- automatic deployment from a selected branch;
- a free web-service plan suitable for portfolio demonstrations.

The free service can sleep after inactivity and may take approximately one minute to wake. This is acceptable for a non-commercial portfolio demonstration and must be stated in the README.

## Why Neon is used for PostgreSQL

Neon provides a PostgreSQL-compatible hosted database with a free plan suitable for a small synthetic demonstration dataset.

It is preferred over Render's free PostgreSQL plan because Render's free database expires after 30 days.

The Neon connection string will be stored only as a Render secret and local ignored configuration when required. It must never be committed.

## Cost boundary

The intended infrastructure cost is £0.

The project must not:

- select a paid Render compute plan;
- select a paid Neon plan;
- purchase a custom domain;
- enable a paid add-on;
- add payment details for an automatic upgrade;
- introduce another chargeable service without an explicit decision.

If a free limit is reached, temporary service suspension is preferable to an automatic charge.

## Frozen model contract

Deployment must preserve the completed Stage 7 contract:

| Item | Frozen value |
|---|---|
| Model | Logistic regression |
| Model metadata name | `logistic_regression` |
| Decision threshold | `0.38` |
| Academic support threshold | Result below `60%` |
| Artifact schema version | `1` |
| Feature count | `18` |
| Training data | Reproducible synthetic data |
| Decision authority | Human tutor |

Deployment must not retrain the model, change its features or retune the threshold.

## Planned deployment configuration

The application will gain support for the following hosted settings:

- `TUTORPULSE_DATABASE_URL` — complete hosted PostgreSQL connection string;
- `TUTORPULSE_MODEL_ARTIFACT_DIRECTORY` — model-artifact directory inside the container;
- `TUTORPULSE_DEMO_READ_ONLY` — enables the public demonstration safety boundary;
- `PORT` — HTTP port supplied by the hosting platform.

Existing split database settings will remain supported for local development and Docker Compose.

## Public demonstration boundary

The hosted demonstration will contain synthetic data only.

When `TUTORPULSE_DEMO_READ_ONLY=true`:

- database-creating, updating and deleting requests must be rejected;
- read-only database endpoints must remain available;
- `POST /predictions/support-risk` must remain available because it performs inference without modifying database records;
- application and model-health endpoints must remain available;
- rejected writes must return a clear HTTP response;
- local development must retain the existing CRUD behaviour when read-only mode is disabled.

This boundary prevents anonymous public users from changing the shared demonstration database while preserving the important portfolio functionality.

## Health and readiness

TutorPulse currently separates:

- `GET /health` — confirms that the FastAPI application is running;
- `GET /model/health` — confirms that the governed model artifact is ready.

Stage 8 will add or document a deployment readiness check covering the dependencies required to serve the demonstration, including PostgreSQL connectivity and model readiness.

Render must use an appropriate successful health endpoint before routing traffic to a new deployment.

## Database preparation

The hosted database will be initialised using the committed schema migration and synthetic seed data.

The process must:

- use `database/migrations/001_create_initial_schema.sql`;
- use `database/seed.sql`;
- connect through a secret hosted connection string;
- avoid placing credentials in Git, screenshots or documentation;
- be reproducible;
- avoid re-inserting seed data on every application restart;
- be verified with expected table and row counts.

The hosted database must never contain real learner information.

## Secret management

Secrets will be stored using Render and Neon configuration interfaces.

The following must not be committed:

- hosted database passwords;
- complete connection strings;
- access tokens;
- provider API keys;
- local deployment `.env` files.

Tracked example files may contain variable names and clearly fictional placeholder values only.

## Logging and privacy

Stage 7 privacy rules remain in force.

Prediction logs may contain:

- generated request identifier;
- model name and version;
- decision threshold;
- thresholded outcome;
- request duration;
- controlled failure category.

Prediction logs must not contain:

- learner names or identifiers;
- raw feature payloads;
- database credentials;
- connection strings;
- intervention notes;
- complete stack traces returned to public clients.

## API documentation and CORS

Interactive API documentation may remain available because demonstrating the API contract is part of the portfolio purpose.

TutorPulse has no browser frontend, so cross-origin access does not need to be enabled by default.

Debug mode must remain disabled in the hosted environment.

## Deployment verification

The hosted deployment must verify:

1. the Render service builds from the repository Dockerfile;
2. the application starts using the platform-provided port;
3. the database connection succeeds;
4. `GET /health` succeeds;
5. the readiness check succeeds;
6. `GET /model/health` reports the expected model and threshold;
7. representative read-only database endpoints return synthetic data;
8. database mutation requests are rejected in demonstration mode;
9. `POST /predictions/support-risk` returns a governed prediction;
10. logs exclude the feature payload and credentials.

## External feedback

At least one other person should be asked to:

- open the deployed demonstration;
- follow the README or demonstration instructions;
- inspect the API documentation;
- try a read-only endpoint;
- submit the supplied fictional prediction example;
- describe anything confusing, slow or unreliable.

Feedback must be recorded without collecting personal information.

The highest-value reliability or usability problem should be fixed and protected with an automated regression test where appropriate.

## Release evidence

The final portfolio release should contain:

- the deployed demonstration link or reproducible deployment evidence;
- a passing GitHub Actions workflow;
- a tagged GitHub release;
- concise release notes;
- the final README;
- deployment limitations;
- a two-minute demonstration script;
- evidence-based CV bullets;
- STAR interview examples;
- the completed TutorPulse learning journey;
- the completed implementation memory checkpoint.

## Known limitations

- The model was trained and evaluated using synthetic data.
- Predictions are decision-support signals, not educational decisions.
- The free API may sleep after inactivity and have a noticeable cold start.
- Free services do not provide production uptime guarantees.
- The public demonstration is intentionally read-only.
- Authentication and authorisation are not implemented as a full user-account system.
- The demonstration is unsuitable for real learner data.
- Free-tier limits and provider policies can change.

## Definition of done

Stage 8 is complete when:

- the deployment configuration is implemented and tested;
- the hosted PostgreSQL database contains only synthetic data;
- the Docker application is deployed successfully;
- health, readiness, read-only and inference behaviour are verified;
- credentials remain outside Git;
- external feedback is recorded and acted on;
- the complete automated suite and GitHub Actions pass;
- the README and project documents are current;
- a tagged release and release notes exist;
- portfolio and interview evidence is prepared;
- the pull request is merged;
- issue #16 is closed;
- the feature branch is cleaned up;
- the learning journey and memory checkpoint are finalised.