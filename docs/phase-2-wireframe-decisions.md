# TutorPulse Phase 2 Wireframe Decisions

## Document status

- Stage: 9 - Define the Phase 2 product and user experience
- GitHub issue: #18
- Status: Approved wireframe baseline
- Baseline: TutorPulse V0.2.0
- Implementation status: Not started
- Interactive wireframe: `docs/wireframes/tutorpulse-stage-9-wireframes.html`

This document preserves the decisions approved after reviewing the Stage 9 wireframes. It is the design source of truth for later implementation stages. The wireframes communicate the intended experience; they are not evidence that the frontend exists.

## Approved visual direction

- Use a dark-purple application background with lighter-purple surfaces and accents.
- Keep navigation, cards and controls visually consistent across teacher and student experiences.
- Reserve green, orange and red for progress meaning rather than decoration.
- Pair every colour with text so meaning never depends on colour alone.
- Maintain readable contrast, visible focus and keyboard-operable controls.
- Keep the public landing-page structure from the reviewed wireframe.

The exact colour tokens may be adjusted during implementation to meet accessibility requirements, but the dark-purple direction is fixed.

## Approved terminology

- Replace **View learners and evidence** with **View learners and progress**.
- Do not use an unexplained **Evidence confidence** score.
- Replace **Low evidence** with a precise statement such as **1 recorded result — limited assessment history**.
- Use **Topics assessed: X of Y** instead of an ambiguous **Curriculum coverage** score.
- Use **assessed** only when TutorPulse has assessment data. Do not claim a topic was taught or covered unless the product explicitly records that event.
- Use **assessment results**, **result count**, **latest result** and **limited assessment history** in ordinary teacher-facing explanations.

In technical documentation, assessment evidence means the marks, questions, topic mappings, dates and related records that support a progress summary. The interface should normally use more direct language.

## Curriculum and tier behaviour

- The first curriculum catalogue must use the official Pearson Edexcel GCSE Mathematics specification selected during Stage 10.
- Foundation and Higher must have separately verified eligible topic sets.
- Do not invent the number of topics in either tier.
- The class page will eventually display the number of assessed topics out of the verified total for that class's tier.
- Higher-tier and Foundation-tier search results must contain only eligible curriculum topics.
- The curriculum source, issue or version, import method and grouping decisions must be documented.

The wireframe intentionally uses `tier total` as a placeholder until Stage 10 creates and verifies the catalogue.

## Teacher dashboard and class detail

- The teacher dashboard summarises classes, awaiting marks and items requiring teacher review.
- Review items must link to progress details rather than present automatic decisions.
- The class page lists learners without ranking them.
- Learner rows show topics assessed, exact result-history information and any item requiring review.
- A class summary may show the count of learners with limited assessment history, but must not display an opaque confidence score.

## Learner curriculum progress page

The learner curriculum progress page is required between class detail and topic detail.

It must:

- show every verified curriculum topic eligible for the learner's tier;
- distinguish assessed and not-yet-assessed topics;
- support topic-name search;
- filter to all, assessed or not-yet-assessed topics;
- sort by lowest percentage, highest percentage or topic name;
- display percentage, progress bar, descriptive label, result count and latest-result date;
- label a percentage supported by only one result as provisional; and
- let the teacher open the detailed record for one topic.

The teacher journey is therefore:

```text
Class detail
-> Learner curriculum progress
-> Learner topic detail
```

## Approved progress bands

| Percentage | Visual treatment | Teacher-facing label |
|---|---|---|
| 90% to 100% | Dark green | Very strong |
| 75% to below 90% | Light green | Strong |
| 55% to below 75% | Orange | Developing - review recommended |
| Below 55% | Red | Priority support recommended |
| No recorded result | Neutral grey or purple | Not yet assessed |

These labels describe current assessment results, not fixed learner ability. A percentage alone is insufficient: the interface must also show the number of contributing results and identify provisional summaries.

## Learner topic detail

- Show the current weighted percentage and its progress label.
- Show the exact result count and latest completion date instead of a vague confidence level.
- Present contributing assessment results chronologically.
- Preserve a route from each result to its source assessment and question.
- Show the support-risk probability and model decision threshold only with an explanation of mandatory human review.
- Keep ordinary assessment information usable when the model is unavailable.
- Provide a clear route back to the learner's full curriculum topic list.

## Assessment builder

The builder records assessment structure rather than question wording.

Required fields and behaviour:

- Assessment title
- Foundation or Higher tier
- Declared total marks
- Class
- Recipient choice: entire class or selected fictional learners
- Question number
- Maximum marks for each question
- Difficulty: Easy, Medium or Hard
- One or more searchable curriculum topics for each question
- Topic results restricted to the selected tier
- Running question-mark total
- Immediate, understandable validation

Question text is not entered into TutorPulse. The teacher retains the original assessment separately.

Publishing remains blocked until:

- every question has a valid positive maximum mark;
- every question has at least one eligible topic;
- every question has a selected difficulty; and
- question maximum marks total exactly the declared assessment total.

The builder does not request a date. The backend must still preserve chronology by recording assignment, completion or finalisation dates at the appropriate lifecycle stage because historical progress and the frozen model depend on ordered results.

## Assignment behaviour

- An assessment can be assigned to an entire fictional class.
- The teacher can instead choose selected fictional learners from that class.
- Recipient selection must be reviewed before confirmation.
- The first wireframe does not require an assessment-definition date.
- Whether the initial release requires an optional due date remains a lifecycle decision for Stage 10 and Stage 14; it must not be confused with the result-completion date required for chronology.

## Difficulty weighting

Difficulty must influence the planned topic-progress calculation, but the exact weights are not approved during Stage 9.

Later work must:

- define transparent Easy, Medium and Hard weights;
- calculate a weighted percentage from awarded and available marks;
- decide how a multi-topic question allocates its contribution without misleading duplication;
- test worked examples and boundary behaviour;
- explain the calculation in teacher-facing language; and
- keep this progress calculation separate from the frozen V0.2.0 machine-learning model.

No implementation should assume arbitrary production-ready weights before that work is complete.

## Approved unchanged concepts

- Public landing-page structure
- Partially complete marking workflow and immediate invalid-mark feedback
- Student progress-page structure and supportive language
- Cold-start, empty, unavailable and forbidden states
- Fictional-data and no-account demonstration boundaries
- Human teacher responsibility for every support decision

## Implementation safeguards

- The existing V0.2.0 release, API contract and model artifact remain preserved.
- Stage 9 approves requirements and wireframes only; it does not authorise frontend or database implementation.
- All examples remain fictional.
- Public demonstration writes require a safe isolated, resettable or browser-only strategy.
- Progress presentation must not become a leaderboard or a permanent-ability label.
- Accessibility verification is required when the visual design becomes code.

## Decisions carried into Stage 10

Stage 10 must resolve and document:

1. The exact Edexcel specification issue or version used.
2. The canonical hierarchy and identifiers for domains, topics and teachable units.
3. Exact Foundation and Higher eligibility.
4. How topic totals used by `X of Y` are calculated.
5. The assessment, question, question-topic and recipient data structures.
6. The distinction between assessment definition, assignment and result dates.
7. The multi-topic allocation rule.
8. The initial difficulty weights and their test examples.

## Approval record

The user reviewed the updated interactive wireframe and confirmed that it matched the intended product direction. This document and the files in `docs/wireframes/` preserve that approved baseline for later work.
