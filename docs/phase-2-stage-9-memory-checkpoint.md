# TutorPulse Phase 2 Stage 9 Memory Checkpoint

## Purpose

This checkpoint allows a future working session to resume Phase 2 without reconstructing the design decisions from chat history. Read this file together with:

- `docs/phase-2-product-brief.md`
- `docs/phase-2-user-journeys.md`
- `docs/phase-2-mvp-scope.md`
- `docs/phase-2-page-map.md`
- `docs/phase-2-wireframe-decisions.md`
- `docs/phase-2-frontend-backend-relationship.md`
- `docs/phase-2-stage-9-learning-journey.md`
- `docs/phase-2-stage-9-evidence.md`
- `docs/wireframes/README.md`

## Repository state at this checkpoint

- Protected public release: TutorPulse V0.2.0 on `main`
- Phase 2 integration branch: `phase-2-interactive-product`
- Active Stage 9 issue branch: `18-define-phase-2-product-and-user-experience`
- GitHub issue: #18
- Existing public API deployment must remain operational while Phase 2 is developed separately.
- Stage 9 status: requirements, journeys, scope, page map, wireframes, architecture handoff, evidence and reflection complete; pull-request review and merge remain.

## Phase 2 objective

Transform the API-centred portfolio demonstration into a visually polished, understandable interactive product for employers, mathematics teachers and non-technical visitors. It remains a fictional portfolio demonstration, not a public school product or invitation to enter real learner data.

## Approved product experience

- Public landing experience with separate teacher and student demonstrations
- Fictional role identities with no signup
- Teacher dashboard, classes, learners, curriculum, assessments, marking, progress and support review
- Student dashboard, assigned-assessment information, results and supportive topic progress
- Dark-purple visual system with lighter-purple accents
- Responsive desktop and mobile behaviour
- Explicit loading, empty, unavailable, validation and forbidden states
- Human-reviewed model output and no automatic intervention

## Approved teacher progress flow

```text
Teacher dashboard
-> Class detail
-> Learner curriculum progress
-> Learner topic detail
-> Teacher-reviewed support signal
```

The learner curriculum progress page must list all verified tier-eligible topics before the teacher opens an individual topic. It includes search, assessed/not-assessed filters, percentage ordering, progress bars, labels, result counts and latest-result dates.

## Approved progress boundaries

- 90% to 100%: Very strong, dark green
- 75% to below 90%: Strong, light green
- 55% to below 75%: Developing - review recommended, orange
- Below 55%: Priority support recommended, red
- No result: Not yet assessed, neutral

All states require text as well as colour. Percentages based on one result are provisional. Labels describe current evidence rather than learner ability.

## Approved terminology changes

- Use **learners and progress**, not **learners and evidence**, in primary navigation.
- Use exact result counts, not an unexplained **evidence confidence** score.
- Use **limited assessment history**, with the reason shown, instead of **low evidence**.
- Use **topics assessed X of Y**, where Y is the verified total for the class tier, instead of ambiguous **curriculum coverage**.

## Approved assessment-builder requirements

- No question-text entry
- Assessment title, tier, class and total marks
- Entire-class or selected-learner assignment
- Question number and maximum marks
- Easy, Medium or Hard difficulty
- Searchable, tier-filtered topics
- Multiple topics per question
- Running mark total
- Publication blocked unless question marks exactly equal the declared total and every question is valid
- No date field in the assessment-definition step

Chronological dates remain required in the backend at assignment, completion or finalisation time. The frozen V0.2.0 model and its chronological safeguards must not be weakened.

## Approved wireframe files

- Interactive standalone review: `docs/wireframes/tutorpulse-stage-9-wireframes.html`
- Editable source: `docs/wireframes/tutorpulse-stage-9-wireframes.fragment.html`
- Static previews: `docs/wireframes/images/`
- Full decision record: `docs/phase-2-wireframe-decisions.md`

## Intentionally unresolved

The following are not omissions; they are assigned to later stages:

- exact verified Edexcel Foundation and Higher topic catalogue;
- exact topic totals;
- exact Easy, Medium and Hard weights;
- multi-topic question allocation rule;
- final database schema and API changes;
- safe architecture for public demonstration writes;
- final production colour tokens after accessibility testing.

## Next-stage handoff

After Stage 9 is reviewed and merged into `phase-2-interactive-product`, Stage 10 should define the curriculum and assessment domain. It must use the decisions above rather than redesigning the experience from scratch.

Stage 10 should begin by verifying the official Pearson Edexcel GCSE Mathematics specification, defining stable curriculum identifiers and tier eligibility, and producing worked examples for question-to-topic progress calculations.

## Do not accidentally change

- Do not replace or rewrite the V0.2.0 release on `main` while planning Phase 2.
- Do not treat wireframe percentages as production data or validated educational thresholds.
- Do not add payments, real school onboarding or real-user accounts to the initial Phase 2 release.
- Do not retrain or alter the frozen V0.2.0 model during these frontend stages.
- Do not describe Stage 9 wireframes as implemented features.
