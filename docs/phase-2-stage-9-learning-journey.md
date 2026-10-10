# TutorPulse Phase 2 Stage 9 Learning Journey

## Stage goal

Define the product before implementation: who it is for, what the first interactive release must demonstrate, how fictional teachers and students move through it, what each page must communicate and where safety boundaries remain.

## Starting point

TutorPulse V0.2.0 already provided a tested FastAPI, PostgreSQL and machine-learning demonstration. Its technical evidence was strong, but the user experience began with Swagger UI, endpoints and JSON. A non-technical visitor had to follow instructions before understanding the product idea.

The stage therefore began from a preserved release rather than an empty repository. `main`, tag `V0.2.0` and the existing Render deployment remained unchanged while planning continued on a separate Phase 2 branch and issue branch.

## What was learned

### Product requirements come before pages

Starting with the intended portfolio audience prevented the interface from becoming a random collection of dashboard components. The primary audiences are technical employers, mathematics teachers and non-technical reviewers. Teacher and student identities inside the demonstration are fictional product roles, not real public accounts.

### An MVP can still tell a complete story

The Phase 2 MVP is intentionally broader than a landing page because the portfolio story depends on a complete flow:

```text
curriculum
-> assessment structure
-> assignment
-> marking
-> topic progress
-> human-reviewed support signal
```

Payments, real school onboarding, real accounts, online question completion, automated marking and production educational claims remain outside the release.

### Interface terminology must match what the data proves

The first wireframes used phrases such as **evidence confidence**, **low evidence** and **curriculum coverage**. Review exposed that these could imply more certainty than TutorPulse possesses.

They were replaced with:

- exact result counts;
- latest-result dates;
- limited assessment history with an explicit reason; and
- topics assessed out of the verified total for the selected tier.

This preserves transparency and makes the product easier for mathematics teachers to understand.

### Learners need a curriculum-wide page before topic detail

The initial page flow moved too quickly from a learner to one topic. Review identified the need for an intermediate page listing every Foundation- or Higher-eligible topic. This page became a central product requirement, with topic search, assessed/not-assessed filters, percentage ordering and visible progress bands.

### Colour needs language and context

The approved percentage bands use dark green, light green, orange and red, but every band also has a label. A neutral not-yet-assessed state prevents missing data from appearing as poor performance. A one-result percentage is provisional rather than presented as a stable judgment.

### Assessment structure is different from assessment content

TutorPulse does not need teachers to copy question wording into the product. The builder records question number, maximum marks, difficulty and one-or-more curriculum topics. This provides the structure needed for marking and progress while leaving the original paper with the teacher.

### Removing a visible date does not remove chronology

The assessment-definition wireframe no longer asks for a date, matching the intended workflow. The backend must still record appropriate assignment, completion or finalisation dates because progress history and the frozen model rely on chronological ordering.

### A frontend does not replace backend responsibility

The planned React and TypeScript interface will call FastAPI over HTTPS. Validation, authorization, database access, progress calculations and model inference remain backend responsibilities. No browser code receives database credentials or the model artifact.

## Design outcome

The approved direction is a polished dark-purple product with lighter-purple accents and semantic progress colours. The wireframe set covers:

1. Public landing page
2. Teacher dashboard
3. Teacher class detail
4. Learner curriculum progress
5. Learner topic detail
6. Invalid assessment builder
7. Partially complete marking
8. Student progress
9. Loading, empty, unavailable and forbidden states

The wireframes and static previews are preserved under `docs/wireframes/`.

## Feedback incorporated

Review confirmed the overall product direction and requested:

- clearer definitions of assessment evidence;
- verified Edexcel Foundation and Higher topics;
- a useful replacement for vague curriculum coverage;
- removal of opaque evidence-confidence language;
- the learner curriculum-progress page;
- approved progress boundaries and supportive wording;
- class or selected-learner assignment;
- declared total marks and exact-total validation;
- searchable multiple topics per question;
- Easy, Medium and Hard question difficulty; and
- removal of question-text and assessment-date inputs from the builder.

Every point is now represented in the requirements, page map, decision record or later-stage handoff.

## Evidence produced

- Product brief
- Teacher and student personas and journeys
- Prioritised MVP and explicit non-goals
- Page map and navigation rules
- Approved wireframes and nine image previews
- Wireframe decision record
- Frontend/backend relationship and API reuse handoff
- Stage 9 verification record
- Stage 9 memory checkpoint

## What remains deliberately unresolved

Stage 10 must verify the exact Pearson Edexcel specification structure and tier eligibility. Later stages must define difficulty weights, multi-topic allocation, safe public demonstration writes, database migrations, authorization and production accessibility evidence.

Deferring these decisions is deliberate because they require domain modelling, worked examples or implementation testing rather than visual preference alone.

## Reflection

The main improvement during Stage 9 was moving from attractive screens to defensible product rules. The wireframes now explain what the system knows, what it does not know and why a teacher remains responsible. This reduces rework before frontend implementation and creates a clear basis for testing later stages.

## Stage boundary

Stage 9 contains planning and evidence only. No frontend components, database migrations, role system or new product API endpoints were implemented.
