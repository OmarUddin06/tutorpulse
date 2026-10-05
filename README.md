# TutorPulse

TutorPulse is a learning-outcomes and intervention service for tutors.

It provides a REST API for recording anonymised assessment results, monitoring topic-level performance and documenting support interventions. The project uses synthetic demonstration data and must not contain identifiable pupil information.

## Current functionality

The API currently supports:

- Creating, viewing, updating and deleting anonymised learners
- Creating, viewing, updating and deleting curriculum topics
- Creating, viewing, updating and deleting assessments
- Recording and managing topic-level assessment results
- Recording and managing learner interventions
- Validating names, titles, scores and intervention states
- Returning clear HTTP status codes and error responses
- Interactive API documentation through FastAPI
- Automated unit and API tests

## Technology

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Psycopg
- pytest

The current development environment uses Python 3.14 and PostgreSQL 18.

## Privacy

Only fictional, synthetic or fully anonymised learner data may be used.

Do not add real pupil names, contact details, school identifiers or other personal information to the database, source code, tests, screenshots or repository history.

## Project structure

```text
tutorpulse/
├── app/
│   ├── routers/
│   │   ├── assessment_results.py
│   │   ├── assessments.py
│   │   ├── interventions.py
│   │   ├── learners.py
│   │   └── topics.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── database/
│   ├── migrations/
│   │   └── 001_create_initial_schema.sql
│   ├── queries.sql
│   ├── README.md
│   └── seed.sql
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

## API resources

| Resource | Path | Supported operations |
|---|---|---|
| Health check | `/health` | Read |
| Learners | `/learners` | Create, list, read, update and delete |
| Topics | `/topics` | Create, list, read, update and delete |
| Assessments | `/assessments` | Create, list, read, update and delete |
| Assessment results | `/assessment-results` | Create, list, read, update and delete |
| Interventions | `/interventions` | Create, list, read, update and delete |

## Local setup

The following instructions use Windows PowerShell.

### 1. Clone the repository

```powershell
git clone https://github.com/OmarUddin06/tutorpulse.git
cd tutorpulse
```

### 2. Create a virtual environment

```powershell
py -m venv .venv
```

If PowerShell blocks activation scripts, temporarily allow them in the current window:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

The PowerShell prompt should begin with `(.venv)`.

### 3. Install the Python dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The main dependencies are:

- FastAPI for the web API
- SQLAlchemy for database access
- Psycopg for the PostgreSQL connection
- Pydantic Settings for environment-based configuration
- pytest and HTTPX2 for automated testing

### 4. Create the PostgreSQL database

```powershell
createdb -U postgres -h localhost -p 5432 tutorpulse
```

PostgreSQL will request the local `postgres` user password.

### 5. Create the database tables

```powershell
psql -U postgres -h localhost -p 5432 -d tutorpulse -v ON_ERROR_STOP=1 -f database/migrations/001_create_initial_schema.sql
```

### 6. Add the synthetic demonstration data

```powershell
psql -U postgres -h localhost -p 5432 -d tutorpulse -v ON_ERROR_STOP=1 -f database/seed.sql
```

### 7. Configure the database connection

Copy the example configuration:

```powershell
Copy-Item .env.example .env
```

Open `.env` and replace the password placeholder with the password for the local PostgreSQL `postgres` user:

```text
TUTORPULSE_DB_HOST=localhost
TUTORPULSE_DB_PORT=5432
TUTORPULSE_DB_NAME=tutorpulse
TUTORPULSE_DB_USER=postgres
TUTORPULSE_DB_PASSWORD=your-local-postgres-password
```

The `.env` file is ignored by Git. Never commit database passwords or other secrets.

## Run the API

Ensure the virtual environment is active, then run:

```powershell
python -m uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Use the interactive FastAPI documentation at:

```text
http://127.0.0.1:8000/docs
```

The OpenAPI specification is available at:

```text
http://127.0.0.1:8000/openapi.json
```

Stop the development server by pressing `Ctrl + C`.

## Run the automated tests

With the virtual environment active, run:

```powershell
python -m pytest -v
```

The test suite checks API health, request validation, CRUD behaviour, status codes, missing records, duplicate data, score constraints and intervention completion rules.

The current suite contains 57 tests.

## Database documentation

More information about the schema, relationships, migration, seed data and reporting queries is available in `database/README.md`.

The database includes:

- Primary and foreign keys
- One-to-many relationships
- Uniqueness constraints
- Score validation constraints
- Intervention status rules
- Synthetic seed data
- Twelve reporting queries

## Initial user stories

### Record an anonymised learner

As a tutor, I want to create an anonymised learner record so that I can monitor progress without storing unnecessary personal information.

### Record an assessment result

As a tutor, I want to record an assessment result against an assessment and topic so that I can track a learner’s performance over time.

### Review topic-level progress

As a tutor, I want to view a learner’s results by topic so that I can identify areas where additional support may be beneficial.

## Planned development

Future stages of TutorPulse include:

- PostgreSQL integration tests
- Docker Compose development setup
- Expanded GitHub Actions checks
- Exploratory data analysis
- An interpretable learner-intervention model
- Model evaluation and documentation
- A prediction endpoint
- Logging and production limitations
- Public deployment

## Author

Omar Uddin  
Final-year Computer Science student and mathematics tutor