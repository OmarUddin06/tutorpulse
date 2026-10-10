# TutorPulse Phase 2 Page Map and Navigation

## Document status

- Stage: 9 - Define the Phase 2 product and user experience
- GitHub issue: #18
- Status: Approved Stage 9 baseline
- Baseline: TutorPulse V0.2.0
- Implementation status: Not started

This document translates the approved Phase 2 personas, journeys and MVP scope into a bounded set of pages. Routes are planning identifiers and may be refined during implementation without changing the agreed user experience.

## Navigation principles

- A visitor must always know whether they are in the public, Demo Teacher or Demo Student experience.
- The public experience explains the project; role experiences prioritise completing tasks.
- The teacher experience may contain more detailed controls and evidence than the student experience.
- The student experience must not expose teacher-only navigation, internal notes or raw risk labels.
- Important pages must remain directly addressable so demonstrations and tests can open them predictably.
- Desktop navigation may use a sidebar, but mobile navigation must remain usable without compressing the full sidebar.
- Breadcrumbs must preserve context on class, learner, assessment and topic detail pages.
- Every role experience must provide a clear **Exit demo** or **Switch role** action.
- Page titles, active navigation and browser titles must agree.

## Top-level page map

```text
TutorPulse
|
+-- Public experience
|   +-- Home
|   +-- Explore demo / role selection
|   +-- How TutorPulse works
|   +-- Responsible use and limitations
|   +-- Project evidence
|
+-- Demo Teacher
|   +-- Dashboard
|   +-- Classes
|   |   +-- Class detail
|   |       +-- Learner detail
|   |           +-- Topic evidence
|   +-- Curriculum
|   |   +-- Curriculum topic detail
|   +-- Assessments
|   |   +-- Assessment detail
|   |   +-- Create or edit assessment
|   |   +-- Preview and publish
|   |   +-- Assign assessment
|   +-- Marking
|   |   +-- Mark assessment
|   |   +-- Review and finalise
|   +-- Progress
|       +-- Class progress
|       +-- Support review
|
+-- Demo Student
|   +-- Dashboard
|   +-- My assessments
|   |   +-- Assessment information
|   +-- My results
|   |   +-- Result detail
|   +-- My progress
|       +-- Topic progress detail
|
+-- System experiences
    +-- Demonstration loading / cold start
    +-- Unavailable or retry
    +-- Forbidden
    +-- Not found
```

Several child views may be implemented as tabs or steps inside one route rather than separate full pages. The required experience matters more than the final URL count.

## Public experience

### Home

- Proposed route: `/`
- Audience: All visitors
- Purpose: Explain the product and direct visitors into the demonstration.
- Primary actions: **Explore teacher demo** and **Explore student demo**.
- Key content:
  - plain-language product statement;
  - short assessment-to-progress explanation;
  - visual preview of the product;
  - synthetic-data and portfolio-demonstration notice;
  - selected engineering evidence;
  - responsible-use summary.
- Required states: normal, backend waking, backend unavailable.

The landing page must remain useful while the free backend wakes. Static explanatory content and role selection should not depend on the API responding first.

### Explore demo

- Proposed route: `/demo`
- Audience: All visitors
- Purpose: Explain the difference between teacher and student roles before entry.
- Primary action: Choose one fictional role.
- Key content:
  - role cards;
  - what each demonstration contains;
  - approximate walkthrough length;
  - reminder that no account or real information is required.
- Required states: normal and temporarily unavailable.

### How TutorPulse works

- Proposed route: `/how-it-works`
- Audience: Non-technical and technical visitors
- Purpose: Explain the fictional workflow from curriculum and assessment evidence to progress and human review.
- Primary action: Enter the teacher demonstration.
- Key content:
  - workflow diagram;
  - definitions of assessment evidence, topic progress and support signal;
  - distinction between teacher judgment and model output.

### Responsible use and limitations

- Proposed route: `/responsible-use`
- Audience: All visitors
- Purpose: Keep privacy, synthetic-data, model and adoption limitations visible.
- Primary action: Return to the demonstration.
- Key content:
  - fictional-data boundary;
  - human-review requirement;
  - no claim of educational effectiveness;
  - portfolio-only release posture;
  - accessibility and privacy intentions.

### Project evidence

- Proposed route: `/evidence`
- Audience: Employers and technical reviewers
- Purpose: Connect the polished interface to verifiable engineering work.
- Primary actions: Open repository, live API documentation or release evidence.
- Key content:
  - architecture summary;
  - technology list;
  - automated-test evidence;
  - deployment and release links;
  - learning-journey link;
  - current limitations.

This page summarises evidence rather than duplicating the complete README.

## Demo Teacher experience

### Teacher dashboard

- Proposed route: `/demo/teacher`
- Purpose: Provide an immediate overview and starting point.
- Primary actions: Open a class, continue marking or review a flagged item.
- Key content:
  - fictional teacher and demonstration label;
  - class summary;
  - recent assessments;
  - marking queue;
  - review queue;
  - brief product-guidance prompt.
- Required states: loading, empty summaries, partial dependency failure and normal.

### Classes

- Proposed route: `/demo/teacher/classes`
- Purpose: Find and open a fictional class.
- Primary action: Open class.
- Key content: class name, tier, learner count, recent assessment and evidence status.
- Required states: loading, no classes, filter with no matches and normal.

### Class detail

- Proposed route: `/demo/teacher/classes/:classId`
- Purpose: Review one class and reach its learners, curriculum and assessments.
- Primary action: Open learner.
- Secondary actions: View class progress, create assessment and filter learners.
- Key content:
  - class identity and tier;
  - learner list;
  - recent assessments;
  - topics assessed out of the verified total for the class tier;
  - exact counts of learners with limited assessment history;
  - no unexplained evidence-confidence score and no learner ranking.
- Required states: class missing, no learners, sparse evidence and normal.

### Learner detail

- Proposed route: `/demo/teacher/learners/:learnerId`
- Purpose: Show every verified curriculum topic available to one fictional learner before opening detailed topic evidence.
- Primary action: Inspect topic evidence.
- Secondary actions: Search topics, filter assessed or not-yet-assessed topics, sort by percentage or topic name and inspect recent assessment.
- Key content:
  - fictional display name;
  - Foundation or Higher tier;
  - every verified topic eligible for that tier;
  - current percentage, progress bar and descriptive label;
  - exact contributing-result count and latest-result date;
  - provisional wording when only one result exists;
  - explicit not-yet-assessed state;
  - recent results;
  - progress over time;
  - recorded interventions;
  - teacher-reviewed support area.
- Required states: learner missing, no evidence, mixed evidence, model unavailable and normal.

### Topic evidence

- Proposed route: `/demo/teacher/learners/:learnerId/topics/:topicId`
- Purpose: Explain how one topic summary was formed.
- Primary action: Return to learner or record teacher judgment when safely supported.
- Key content:
  - assessment evidence in chronological order;
  - progress calculation explanation;
  - exact result count, latest-result date and any provisional wording;
  - relevant interventions;
  - model probability and thresholds when available;
  - mandatory human-review explanation.
- Required states: insufficient evidence, conflicting evidence, model unavailable and normal.

### Curriculum

- Proposed route: `/demo/teacher/curriculum`
- Purpose: Browse the verified mathematics structure and understand tier behaviour.
- Primary action: Open curriculum topic.
- Key content: selected specification, version, tier filter, areas, topics and teachable units.
- Required states: loading, no matches, unavailable and normal.

### Curriculum topic detail

- Proposed route: `/demo/teacher/curriculum/:topicId`
- Purpose: Explain one topic and show where it appears in assessments and progress evidence.
- Primary action: Create assessment using topic.
- Key content: curriculum path, tier availability, description and connected assessments.

### Assessments

- Proposed route: `/demo/teacher/assessments`
- Purpose: Find assessments and understand their lifecycle state.
- Primary action: Create assessment.
- Key content: drafts, published assessments, assignments, optional assignment timing and marking status.
- Required states: loading, no assessments, filter with no matches and normal.

### Assessment detail

- Proposed route: `/demo/teacher/assessments/:assessmentId`
- Purpose: Inspect the definition, questions, mappings, assignments and marking status.
- Primary action: Continue the next valid lifecycle step.
- Required states: draft, published, assigned, partly marked, finalised, missing and unavailable.

### Create or edit assessment

- Proposed routes: `/demo/teacher/assessments/new` and `/demo/teacher/assessments/:assessmentId/edit`
- Purpose: Construct a valid fictional mathematics assessment.
- Primary action: Continue to preview.
- Key content: title, tier, class, declared total marks, numbered questions, maximum marks, difficulty, one-or-more tier-filtered curriculum topics, running total and validation summary.
- Required states: pristine, editing, invalid, unsaved, save failed and saved draft.

Question wording is not entered into TutorPulse. Publication remains blocked until every question has valid marks, difficulty and topic mappings and the question marks total exactly the declared assessment total.

### Preview and publish

- Proposed route: `/demo/teacher/assessments/:assessmentId/preview`
- Purpose: Verify the complete assessment before changing its lifecycle state.
- Primary action: Publish assessment.
- Key content: question order, marks, mappings, total marks and validation.
- Required states: blocked publication, ready and publishing.

### Assign assessment

- Proposed route: `/demo/teacher/assessments/:assessmentId/assign`
- Purpose: Select fictional recipients and confirm assignment details.
- Primary action: Confirm assignment.
- Key content: entire-class or selected-learner choice and recipient summary.
- Required states: no eligible recipients, empty selected-learner choice, confirmation and failure.

The assessment-definition builder has no date field. Assignment, completion and finalisation dates remain backend lifecycle data so chronological progress and the frozen model remain valid. Whether the initial assignment flow includes an optional due date is deferred to the Stage 10 and Stage 14 lifecycle design.

### Marking queue

- Proposed route: `/demo/teacher/marking`
- Purpose: Find assigned assessments requiring marks.
- Primary action: Start or continue marking.
- Key content: assessment, class, completion count, optional assignment timing and marking state.
- Required states: nothing to mark, filter with no matches and normal.

### Mark assessment

- Proposed route: `/demo/teacher/marking/:assignmentId`
- Purpose: Enter marks efficiently and accurately.
- Primary action: Save progress or continue to final review.
- Key content: learner context, question context, awarded marks, maximum marks, keyboard guidance and completion status.
- Required states: partially complete, invalid mark, unsaved, saving, save failed and saved.

### Review and finalise marks

- Proposed route: `/demo/teacher/marking/:assignmentId/review`
- Purpose: Check completeness before creating final progress evidence.
- Primary action: Finalise results.
- Key content: missing marks, totals, validation, consequences and confirmation.
- Required states: blocked, ready, finalising, failed and completed.

### Progress

- Proposed route: `/demo/teacher/progress`
- Purpose: Compare curriculum evidence across a fictional class without creating a leaderboard.
- Primary action: Open learner or topic evidence.
- Key content: topics assessed, exact result-history information, time filter and items for review.
- Required states: no evidence, partial evidence, filter with no matches and normal.

### Support review

- Proposed route: `/demo/teacher/review`
- Purpose: Gather items requiring human attention without automating decisions.
- Primary action: Open underlying evidence.
- Key content: reason for review, evidence availability, model availability and teacher-judgment status.
- Required states: nothing requiring review, model unavailable and normal.

## Demo Student experience

### Student dashboard

- Proposed route: `/demo/student`
- Purpose: Summarise the fictional student's work and progress in supportive language.
- Primary actions: View assignment, recent result or progress.
- Key content: fictional identity, assignments, recent results, strength, topic to revisit and next step.
- Required states: no assignments, no results, sparse evidence and normal.

### My assessments

- Proposed route: `/demo/student/assessments`
- Purpose: List assigned and completed assessments without online completion.
- Primary action: Open assessment information.
- Key content: title, optional assignment timing, status and completion information.
- Required states: no assignments, filter with no matches and normal.

### Assessment information

- Proposed route: `/demo/student/assessments/:assessmentId`
- Purpose: Explain one assignment or completed assessment.
- Primary action: Return to assessments or open available result.
- Key content: title, teacher-provided description, optional assignment timing, status and topic coverage.

### My results

- Proposed route: `/demo/student/results`
- Purpose: Present completed assessment outcomes clearly.
- Primary action: Open result.
- Key content: assessment, date, total outcome and covered topics.
- Required states: no results, filter with no matches and normal.

### Result detail

- Proposed route: `/demo/student/results/:assessmentId`
- Purpose: Explain one fictional assessment outcome without exposing internal teacher information.
- Primary action: Open related topic progress.
- Key content: total outcome, topic outcomes, plain-language explanation and constructive next steps.

### My progress

- Proposed route: `/demo/student/progress`
- Purpose: Show topic-level evidence and change over time.
- Primary action: Open topic detail.
- Key content: curriculum grouping, accessible progress labels, exact result-history context and supportive next steps.
- Required states: no evidence, sparse evidence, mixed evidence and normal.

### Topic progress detail

- Proposed route: `/demo/student/progress/:topicId`
- Purpose: Explain the evidence behind one topic summary in student-appropriate language.
- Primary action: Return to progress.
- Key content: recent fictional results, simple trend explanation, evidence limitation and suggested next step.
- Required states: insufficient evidence, mixed evidence and normal.

## Global system experiences

### Demonstration loading and cold start

- Explain that free hosting may need time to wake.
- Keep static product information visible.
- Display progress without promising an exact completion time.
- Retry automatically with a manual retry option.

### Unavailable or retry

- Explain which part is unavailable in plain language.
- Preserve entered information when safe.
- Offer a specific retry or return action.
- Do not expose stack traces, credentials or internal infrastructure details.

### Forbidden

- Explain that the selected role cannot access the page or action.
- Provide a route back to that role's dashboard.
- Do not reveal whether inaccessible records exist.

### Not found

- Use the active role's navigation where appropriate.
- Explain that the page or fictional record could not be found.
- Provide a safe return action.

## Desktop navigation

### Public header

- TutorPulse identity
- How it works
- Responsible use
- Project evidence
- Explore demo

### Teacher sidebar

- Dashboard
- Classes
- Curriculum
- Assessments
- Marking
- Progress
- Support review
- Switch role or exit demo

### Student navigation

- Dashboard
- My assessments
- My results
- My progress
- Switch role or exit demo

## Mobile navigation

- Use a compact header containing TutorPulse, active role and menu control.
- Present the role's navigation in an accessible drawer or similarly clear compact pattern.
- Keep the most important page action visible without covering content.
- Do not place every teacher section into a permanently visible bottom bar.
- Ensure menus can be opened, traversed and closed with a keyboard and screen reader.

## Breadcrumb rules

- Do not show breadcrumbs on the public home page or role dashboards.
- Use breadcrumbs when a visitor moves into class, learner, topic, assessment, assignment or result detail.
- Use human-readable fictional names rather than raw database identifiers.
- Never make the current page breadcrumb a misleading link.

Examples:

```text
Classes > Year 10 Higher > Learner 001 > Algebra
Assessments > Autumn Algebra Check > Assign
My results > Autumn Algebra Check
```

## Two-minute employer demonstration route

The default demonstration path is:

```text
Home
-> Explore teacher demo
-> Teacher dashboard
-> Year 10 Higher class
-> Learner 001
-> Algebra topic evidence
-> Teacher-reviewed support signal
-> Project evidence
```

This route must work with prepared synthetic data and must not depend on completing a write operation.

## Page-state requirement

The wireframe set must cover at least:

- one normal desktop page from each major navigation group;
- landing-page cold start;
- empty teacher state;
- invalid assessment form;
- partially completed marking state;
- insufficient progress evidence;
- model unavailable while ordinary evidence remains visible;
- forbidden role access;
- mobile teacher navigation; and
- mobile student progress.

## Stage dependencies

| Page group | Principal delivery stage |
|---|---|
| Public shell and evidence | Stage 12 foundation, completed in Stage 17 |
| Curriculum pages | Stages 10 and 13 |
| Role boundaries | Stage 11 |
| Shared frontend shell | Stage 12 |
| Classes and learners | Stage 13 |
| Assessment lifecycle | Stage 14 |
| Marking workflow | Stage 15 |
| Teacher and student progress | Stage 16 |
| Cross-page polish and deployment | Stage 17 |

## Approved page-map decisions

The page map is approved as the Stage 9 wireframing baseline:

1. Every must-have MVP journey has a defined public, teacher or student path.
2. Child experiences may become tabs or steps rather than separate full pages when usability testing supports that decision.
3. The teacher and student navigation remain deliberately different in complexity and language.
4. The two-minute employer route remains the primary demonstration path.
5. System states are part of the designed experience rather than implementation afterthoughts.
6. Route names remain provisional implementation details while the page responsibilities are fixed requirements.
7. Learner detail is the curriculum-wide progress page; topic detail is a separate drill-down page.
8. Primary interface wording uses exact result counts and limited-history explanations instead of an opaque evidence-confidence score.
9. Class curriculum breadth is labelled **Topics assessed: X of Y**, where Y comes from the verified tier catalogue.
10. The approved dark-purple wireframes and their decision record are preserved in `docs/wireframes/` and `docs/phase-2-wireframe-decisions.md`.

## Stage boundary

This page map defines planned navigation and content. It is not evidence that routes, pages or frontend components have been implemented.
