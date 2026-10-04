# TutorPulse Database

This directory contains the initial PostgreSQL database implementation for TutorPulse.

TutorPulse uses fictional and anonymised development data to demonstrate how tutors could review learner performance, identify topic-level learning gaps and record support interventions.

## Database structure

```text
database/
├── migrations/
│   └── 001_create_initial_schema.sql
├── queries.sql
├── README.md
└── seed.sql
```

- `migrations/001_create_initial_schema.sql` creates the tables, relationships and constraints.
- `seed.sql` inserts fictional development data.
- `queries.sql` contains reusable reporting and validation queries.
- `README.md` explains how to create and populate the database.

The design decisions and entity-relationship diagram are available in:

- [`docs/database-design.md`](../docs/database-design.md)
- [`docs/database-erd.md`](../docs/database-erd.md)

## Requirements

Install PostgreSQL and ensure its command-line tools are available from the terminal.

The database was developed and tested with PostgreSQL 18.

Confirm the installation:

```powershell
psql --version
```

Do not store PostgreSQL passwords or real learner information in the repository.

## Create the development database

From PowerShell, create an empty local database:

```powershell
createdb -U postgres -h localhost -p 5432 tutorpulse
```

Enter the local PostgreSQL administrator password when prompted.

## Apply the migration

Run this command from the repository root:

```powershell
psql -U postgres -h localhost -p 5432 -d tutorpulse -v ON_ERROR_STOP=1 -f database/migrations/001_create_initial_schema.sql
```

The migration creates:

- `learners`
- `assessments`
- `topics`
- `assessment_results`
- `interventions`

`ON_ERROR_STOP=1` makes `psql` stop immediately if a statement fails. The migration also uses a transaction so that PostgreSQL does not leave a partially created schema.

A migration should normally be applied only once to each database.

## Populate the database

Insert the fictional development data:

```powershell
psql -U postgres -h localhost -p 5432 -d tutorpulse -v ON_ERROR_STOP=1 -f database/seed.sql
```

The seed creates:

- Four fictional learners
- Two assessments
- Three topics
- Sixteen topic-level assessment results
- Three interventions

The seed file is intended for an empty development database and should normally be applied only once.

## Run the reporting queries

Execute all reporting and validation queries:

```powershell
psql -U postgres -h localhost -p 5432 -d tutorpulse -v ON_ERROR_STOP=1 -f database/queries.sql
```

The queries demonstrate:

- Filtering and sorting
- Calculated percentages
- Inner and left joins
- Aggregate functions
- `GROUP BY` and `HAVING`
- Conditional aggregation with `CASE`
- Finding learners without related intervention records
- Comparing topic performance between assessments

## Verify the tables

List the tables:

```powershell
psql -U postgres -h localhost -p 5432 -d tutorpulse -c "\dt"
```

The output should contain all five TutorPulse tables.

Inspect an individual table and its constraints:

```powershell
psql -U postgres -h localhost -p 5432 -d tutorpulse -c "\d assessment_results"
```

## Recreate the local database

The following commands permanently remove and recreate the local `tutorpulse` database.

Only use them for the fictional local development database. Never use them against a database containing information that must be retained.

```powershell
dropdb -U postgres -h localhost -p 5432 tutorpulse
createdb -U postgres -h localhost -p 5432 tutorpulse
```

After recreating the database, apply the migration and seed again using the commands above.

## Privacy

All committed learner records are synthetic. Real names, contact details, university identifiers, assessment submissions and other personal information must not be added to this repository.