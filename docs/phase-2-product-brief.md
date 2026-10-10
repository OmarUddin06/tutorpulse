# TutorPulse Phase 2 Product Brief

## Document status

- Stage: 9 - Define the Phase 2 product and user experience
- GitHub issue: #18
- Status: Approved Stage 9 foundation; remaining Stage 9 sections in progress
- Baseline: TutorPulse V0.2.0
- Data boundary: fictional and synthetic demonstration data only

This document defines the problem, audience and initial product direction for TutorPulse Phase 2. It is a planning document, not evidence that the frontend or any new product capability has been implemented.

## V0.2.0 foundation audit

TutorPulse V0.2.0 is a complete technical portfolio demonstration rather than a conventional end-user website.

### Capabilities already available

- A FastAPI application backed by PostgreSQL and SQLAlchemy.
- CRUD resources for learners, topics, assessments, assessment results and interventions.
- Validation of names, titles, marks, relationships and intervention states.
- A reproducible synthetic-data, analysis and machine-learning pipeline.
- A frozen logistic-regression artifact using an 18-feature inference contract.
- Governed support-risk predictions with a visible decision threshold and mandatory human review.
- Application-health, deployment-readiness and model-health endpoints.
- Automated unit, API, modelling and PostgreSQL integration tests.
- Docker packaging and GitHub Actions verification.
- A live Render deployment backed by Neon PostgreSQL.
- A public read-only boundary that protects the shared synthetic records while permitting stateless predictions.
- Versioned release evidence, external testing, documentation and a demonstration script.

### Existing domain model

The current relational model contains:

- learners;
- topics;
- assessments;
- one topic-level result for a learner within an assessment;
- interventions connected to a learner and optionally a topic.

This is a useful foundation, but it does not yet represent classes, accounts, ownership, curriculum tiers, assessment questions, assessment assignments or historical progress snapshots.

### Existing public experience

The current public interface is FastAPI's generated Swagger documentation. It enables a visitor to list four fictional learners and submit a supplied fictional prediction request. This demonstrates the API contract effectively to technical reviewers.

For a non-technical visitor, however, the experience begins with endpoints, HTTP methods and JSON. The visitor must follow detailed instructions before the underlying educational idea becomes visible. There is no homepage, guided product story, teacher workspace, student view or visual progress explanation.

### Constraints that Phase 2 inherits

- V0.2.0 remains a preserved and independently referencable release.
- The existing model, feature contract, artifact schema and `0.38` decision threshold remain frozen unless a later separately scoped stage explicitly changes them.
- Predictions remain decision-support signals rather than automated educational decisions.
- No real learner, teacher or school information may be used.
- The current public API demonstration remains read-only.
- Secrets remain outside Git and public responses.
- Phase 2 must not imply that TutorPulse is ready for real educational deployment.

## Phase 2 problem statement

TutorPulse demonstrates substantial backend, database, machine-learning, testing and deployment work, but most of that value is hidden behind an API-oriented interface. A non-technical reviewer can verify that the system works, yet cannot immediately experience how its capabilities could support a teacher or learner.

Phase 2 must turn the existing technical demonstration into a coherent, attractive and interactive product demonstration. It should let a visitor understand the educational workflow through familiar screens, purposeful visualisations and guided fictional scenarios, while preserving the project's privacy, governance and evidence standards.

The challenge is not simply to put buttons in front of the existing endpoints. The frontend must communicate:

- what problem TutorPulse is exploring;
- what a fictional teacher or student can do;
- where assessment evidence comes from;
- how topic-level progress is calculated and explained;
- where model predictions assist human review;
- which conclusions remain uncertain or provisional; and
- why the demonstration must not be treated as a production education system.

## Product objective

Create a polished portfolio demonstration in which a visitor can move through realistic fictional teacher and student journeys, understand topic-level progress, inspect the evidence behind a support signal and recognise that final judgment remains with a human teacher.

The interface should be visually impressive enough to demonstrate product thinking, while remaining understandable to people who do not work in software.

## Intended audience

TutorPulse has two different audience layers. They must not be confused.

### Portfolio audience

These people evaluate the project rather than operate it as a real service.

#### Primary portfolio audience: technical employers and reviewers

They should be able to see evidence of full-stack engineering, database design, testing, deployment, accessibility, security reasoning and responsible model integration. They may inspect the repository after trying the interface.

#### Primary portfolio audience: mathematics teachers and education professionals

They should be able to understand the proposed workflow without knowing what an API, JSON payload or model artifact is. Their feedback is especially valuable for checking whether the terminology, progress presentation and teacher workflow feel credible.

#### Secondary portfolio audience: non-technical recruiters, tutors and general visitors

They should understand the project within a few minutes, complete a guided interaction and identify the main value without reading the technical documentation first.

### Demonstration product users

These are fictional roles represented inside the product experience. They are not real account holders during the initial Phase 2 demonstration.

#### Fictional teacher

The teacher needs to organise classes and learners, understand curriculum coverage, create and assign assessments, record marks, inspect topic-level progress and review support signals with their underlying evidence.

#### Fictional student

The student needs a simpler view of assigned work, completed assessment outcomes, topic strengths, areas to revisit and progress over time. The language must be supportive and must not present a prediction as a fixed label or judgment.

## Initial success criteria

Phase 2 will be successful when a first-time visitor can:

1. understand what TutorPulse is from the landing experience;
2. enter a clearly labelled fictional demonstration without creating an account;
3. recognise whether they are viewing the teacher or student experience;
4. complete the principal journey without Swagger UI or copied JSON;
5. understand a topic-level progress view and the evidence supporting it;
6. understand that model output supports human review rather than making a decision;
7. use the experience on desktop and mobile with keyboard-accessible controls; and
8. find an honest explanation of synthetic data, limitations and privacy boundaries.

## Explicit non-goals for the initial Phase 2 release

- Payments, subscriptions or billing.
- Real school onboarding or production operations.
- Real children, teachers, parents or school data.
- Public self-service account registration.
- Verified email delivery or password recovery.
- Parent, guardian or school-administrator portals.
- Multiple subjects or exam boards.
- Automated interventions or educational decisions.
- Claims of real-world model accuracy, fairness or educational benefit.
- Native mobile applications.

## Decisions still required during Stage 9

- The exact minimum teacher journey for the first interactive release.
- The exact minimum student journey for the first interactive release.
- Whether the public demonstration uses role-selection, preconfigured fictional identities or both.
- The page map, navigation structure and principal page hierarchy.
- The visual design direction and reusable interface principles.
- The low-fidelity layout of every principal page and important failure state.
- Which V0.2.0 API resources can be reused unchanged and which later stages must extend.
- The evidence required before Stage 9 can be marked complete.

## Approved journey decisions

The following Stage 9 decisions are approved and must guide the remaining requirements, page map and wireframes:

1. The primary two-minute demonstration follows the Demo Teacher from dashboard to class, learner, topic evidence and a teacher-reviewed support signal.
2. Assessment creation and keyboard-friendly marking remain inside the initial Phase 2 product scope because they demonstrate the complete evidence workflow.
3. The initial Demo Student experience presents assignments, results and progress but does not provide online assessment completion.
4. Public demonstration interactions must not alter the permanent shared dataset. A temporary, isolated, resettable or client-side demonstration approach must be selected before public writes are implemented.
5. A visitor enters the demonstration by selecting either the teacher or student role without creating an account.

These decisions refine the plan recorded in the Phase 2 learning journey and memory checkpoint. They do not authorise application implementation during Stage 9.

## Stage 9 completion boundary

Stage 9 produces reviewed requirements, user journeys, a page map, wireframes and recorded decisions. It does not produce the React application, new database tables, authentication, teacher workflows or student workflows. Those belong to later stages.
