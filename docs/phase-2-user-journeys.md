# TutorPulse Phase 2 Personas and User Journeys

## Document status

- Stage: 9 - Define the Phase 2 product and user experience
- GitHub issue: #18
- Status: Approved planning baseline; page map and wireframes still pending
- Baseline: TutorPulse V0.2.0
- Implementation status: Not started

This document defines the people represented by the TutorPulse demonstration and the journeys that the future interface must support. Every identity, class, assessment and result described here is fictional.

## How to read this document

A **persona** is a deliberately simplified description of a user type. It helps the project make consistent design decisions; it is not a claim that every teacher or student behaves the same way.

A **user journey** describes the outcome a person is trying to achieve and the steps the product should support. It is not yet a screen design or technical implementation.

A later feature should be challenged if it cannot be connected to one of the agreed journeys or a necessary safety, accessibility or engineering requirement.

## Audience and role separation

TutorPulse must distinguish three concepts:

1. **Portfolio visitor** - the real person evaluating the project.
2. **Demo Teacher** - a fictional role the visitor can explore.
3. **Demo Student** - a fictional role the visitor can explore.

The initial demonstration does not provide real public accounts. A visitor chooses a clearly labelled fictional role and explores prepared synthetic information.

## Persona 1: Portfolio visitor

### Description

The portfolio visitor may be a technical employer, recruiter, mathematics teacher, tutor or non-technical reviewer. They have not used TutorPulse before and may only spend a few minutes deciding whether it is understandable and credible.

### Goals

- Understand the purpose of TutorPulse quickly.
- See a polished product rather than starting with API documentation.
- Explore a realistic teacher or student workflow without registering.
- Understand what is functional, what is simulated and what remains experimental.
- Find technical evidence when they want more detail.

### Likely frustrations

- Unfamiliar terms such as endpoints, payloads, inference and model artifacts.
- Long setup instructions before anything meaningful appears.
- Empty dashboards with no obvious starting action.
- Claims that sound stronger than the available synthetic evidence.
- A free-hosting delay that looks like a broken page.

### Design implications

- The landing page must explain the product in plain language.
- A primary action must open the demonstration without an account.
- Teacher and student roles must be clearly distinguished.
- The interface must contain useful synthetic data immediately.
- Cold-start, demonstration and synthetic-data notices must be concise and visible.
- Technical architecture, repository and API links should remain available without dominating the main journey.

## Persona 2: Demo Teacher

### Description

The Demo Teacher represents a mathematics teacher or tutor responsible for a fictional class. They need to understand what has been taught, record assessment evidence, identify topics that may need attention and make the final decision about support.

### Goals

- See the current state of a class without manually combining spreadsheets.
- Find a learner and understand their recent evidence quickly.
- Organise curriculum topics at the correct tier.
- Create and assign a valid assessment.
- Record marks efficiently.
- Understand how topic-level progress has been calculated.
- Review a model-supported signal without surrendering professional judgment.

### Likely frustrations

- Re-entering the same class or learner information.
- Assessment forms that allow inconsistent totals or topic selections.
- Dashboards that show colours without explaining the underlying evidence.
- Risk labels that appear definitive or stigmatising.
- Interfaces that require a mouse for repetitive marking.
- Important actions hidden behind technical terminology.

### Safety expectations

- All information is clearly fictional and synthetic.
- The teacher can inspect the evidence behind any progress state or support signal.
- A prediction never creates an intervention automatically.
- Uncertainty and limited evidence are visible.
- Destructive actions require clear confirmation.
- Public demonstration changes cannot corrupt a shared permanent dataset.

## Persona 3: Demo Student

### Description

The Demo Student represents a fictional learner viewing their own assigned work and progress. The experience should be encouraging, limited to that student and understandable without knowledge of statistics or machine learning.

### Goals

- See assigned or recently completed assessments.
- Understand performance by mathematics topic.
- Identify strengths and topics to revisit.
- See progress over time in plain language.
- Understand a suggested next step without being labelled by a model.

### Likely frustrations

- Dense teacher-oriented tables.
- Unexplained percentages, thresholds or confidence values.
- Red warning-heavy interfaces that feel punitive.
- Comparisons with other students.
- Seeing internal teacher notes or model terminology.

### Safety expectations

- The student sees only their fictional profile.
- No ranking or public comparison is shown.
- Support language focuses on evidence and next steps rather than ability.
- Internal teacher judgments and raw model outputs are not exposed as student labels.
- Sparse evidence is described honestly rather than converted into false certainty.

## Primary journey A: First-time portfolio visitor

### Desired outcome

Understand TutorPulse and enter a meaningful fictional demonstration in less than two minutes.

### Planned steps

1. The visitor opens the TutorPulse landing page.
2. A short statement explains that TutorPulse explores mathematics assessment evidence, topic-level progress and teacher-reviewed support signals.
3. The page states that the demonstration uses fictional data and is not a production school service.
4. The visitor selects **Explore teacher demo** or **Explore student demo**.
5. A brief role explanation appears before the appropriate dashboard opens.
6. Prepared synthetic information is already visible; no setup or account creation is required.
7. Optional links lead to the project story, responsible-use limitations, repository and technical API evidence.

### Successful journey

- The visitor can explain the purpose of TutorPulse in their own words.
- They know which fictional role they are exploring.
- They understand that the information is synthetic.
- They reach a useful dashboard without using Swagger UI or copying JSON.

### Important states

- **Cold start:** explain that the free demonstration is waking up and continue checking automatically.
- **Backend unavailable:** show an honest retry option and retain a clear explanation of the project.
- **Small screen:** stack content without hiding the primary demonstration actions.

## Primary journey B: Teacher reviews a class and learner

### Desired outcome

Move from a class overview to the evidence behind one learner's topic-level progress and decide whether further human review is appropriate.

### Planned steps

1. The visitor enters the Demo Teacher experience.
2. The teacher dashboard summarises fictional classes, recent assessments, unmarked work and items requiring review.
3. The visitor opens a prepared mathematics class.
4. The class page lists fictional learners and summarises recent evidence without ranking them.
5. The visitor opens one learner profile.
6. The learner page shows topic-level progress, recent assessments and recorded interventions.
7. The visitor chooses one topic to inspect.
8. A detail view explains which assessment results contributed to the displayed progress state.
9. If a support-risk prediction is shown, the interface explains the probability, threshold, evidence limits and mandatory human review.
10. The visitor may record a fictional teacher judgment or proposed next step only if the later demonstration architecture provides safe isolated or resettable writes.

### Successful journey

- The visitor can move from class to learner to topic without losing context.
- Every summary can be traced to understandable evidence.
- Current progress and historical evidence are visually distinct.
- The support signal is presented as one input to teacher judgment.
- No automatic intervention is created.

### Important states

- No assessment evidence for the selected topic.
- Too little evidence for a confident progress summary.
- Model unavailable while ordinary assessment information remains usable.
- Forbidden information or action for the selected role.
- Failed request with a safe retry action.

## Primary journey C: Teacher creates and assigns an assessment

### Desired outcome

Create a valid fictional mathematics assessment and assign it to the intended class without inconsistent marks, topics or recipients.

### Planned steps

1. The teacher opens **Assessments** and chooses **Create assessment**.
2. They enter a clear title and select the relevant mathematics tier.
3. They add questions and allocate marks.
4. Each question is mapped to one or more curriculum topics using an explicit rule defined in Stage 10.
5. A running total displays the available marks.
6. Validation identifies missing topics, invalid marks or incomplete questions before publication.
7. The teacher previews the assessment summary.
8. They publish the assessment and select a fictional class or learners.
9. A confirmation view states exactly who received the assignment and when it is due.

### Successful journey

- The assessment cannot be published with invalid totals or incomplete mappings.
- The selected tier and topics remain visible during creation.
- Assignment recipients are explicit before confirmation.
- The visitor can distinguish draft, published and assigned states.

### Important states

- Empty assessment draft.
- Unsaved changes.
- Invalid or zero marks.
- Topic or tier mismatch.
- No eligible learners.
- Accidental navigation away from a draft.

## Primary journey D: Teacher records marks

### Desired outcome

Record fictional marks quickly, accurately and with a clear audit trail.

### Planned steps

1. The teacher opens an assigned assessment awaiting marking.
2. The marking view presents learners and questions in a keyboard-friendly order.
3. The teacher enters awarded marks while maximum marks remain visible.
4. Invalid values are rejected beside the affected field.
5. Progress is saved deliberately, with a clear saved or unsaved state.
6. The teacher reviews a summary before finalising the results.
7. Finalised evidence updates the relevant fictional progress views.

### Successful journey

- Repetitive entry can be completed without relying on a mouse.
- Awarded marks cannot exceed maximum marks.
- The teacher can identify unsaved and invalid fields immediately.
- Finalisation is separate from ordinary editing.
- The resulting topic evidence is traceable to the assessment and question.

### Important states

- Partially marked assessment.
- Invalid score.
- Save failure.
- Attempt to finalise incomplete required marks.
- Previously finalised assessment requiring a controlled correction.

## Primary journey E: Student reviews progress

### Desired outcome

Understand recent fictional mathematics progress and identify one constructive next step.

### Planned steps

1. The visitor enters the Demo Student experience.
2. The student dashboard shows current assignments, recent results and a concise progress summary.
3. The visitor opens **My progress**.
4. Topics are grouped clearly, with accessible labels in addition to colour.
5. The visitor selects a topic.
6. The topic page explains recent evidence, change over time and evidence confidence in plain language.
7. The page presents a constructive next step, such as revisiting a topic or discussing it with the teacher.
8. The visitor can return to the dashboard without entering teacher-only areas.

### Successful journey

- The student view is simpler than the teacher view.
- The visitor can identify a strength and a topic to revisit.
- Progress language does not label fixed ability.
- Colour is never the only way meaning is communicated.
- No other learner's information or internal teacher note is visible.

### Important states

- No completed assessments.
- Only one result, so a trend cannot be claimed.
- Mixed recent evidence.
- Teacher-only route attempted.
- Data temporarily unavailable.

## Navigation implications

The journeys suggest the following initial navigation groups.

### Public navigation

- Home
- Explore demo
- How it works
- Responsible use
- Project evidence

### Demo Teacher navigation

- Dashboard
- Classes
- Learners
- Curriculum
- Assessments
- Marking
- Progress

### Demo Student navigation

- Dashboard
- My assessments
- My results
- My progress

These labels remain provisional until the Stage 9 page map and wireframes are reviewed.

## Cross-journey design rules

- Keep the current role visible throughout the demonstration.
- Provide a clear way to leave or reset the fictional demo.
- Do not require visitors to understand API terminology.
- Use plain-language labels followed by optional technical detail.
- Show the evidence behind summaries and predictions.
- Never rely on colour alone.
- Make keyboard focus and validation states visible.
- Preserve useful context when moving from class to learner to topic.
- Treat loading, empty, error and forbidden states as designed experiences.
- Clearly distinguish implemented functionality from explanatory mock or planned content.

## Approved Stage 9 decisions

The following decisions were approved after reviewing the initial personas and journeys:

1. The primary two-minute demonstration is **Teacher dashboard -> class -> learner -> topic evidence -> teacher-reviewed support signal**.
2. Assessment creation and keyboard-friendly marking remain part of the initial Phase 2 scope.
3. The initial Demo Student can view assignments, results and progress but does not complete assessments online.
4. Public demonstration interactions must not modify the permanent shared dataset. The eventual implementation must use an isolated, resettable, temporary or client-side approach.
5. Visitors select **Teacher demo** or **Student demo** from the landing page without creating an account.

These choices follow the Phase 2 learning journey and memory checkpoint. They are product requirements rather than completed functionality.

## Decisions still open

- Exact fictional class, teacher and student seed scenario.
- Whether public demo mutations are session-local, reset periodically or simulated only in the browser.
- Whether role selection opens the dashboard immediately or first presents a short optional guided-tour introduction.
- Exact names and grouping of navigation items.
- Which teacher journey should be the default two-minute demonstration.
- How progress confidence and teacher judgment are expressed visually.
- The exact content and layout of the read-only student assessment and result views.

## Next review questions

During the remaining Stage 9 work, confirm:

1. Which exact pages are required to support the approved journeys?
2. Which capabilities belong in the MVP and which should be deferred?
3. What visual structure best explains progress, confidence and teacher judgment?
4. Which demonstration-data isolation strategy is proportionate for the portfolio release?
5. Which states must appear in the low-fidelity wireframes before implementation begins?

## Stage boundary

These journeys are planned requirements. No page, account, class, assessment workflow or frontend component described here has been implemented yet.
