# TutorPulse Phase 2 MVP Scope

## Document status

- Stage: 9 - Define the Phase 2 product and user experience
- GitHub issue: #18
- Status: Approved Stage 9 baseline
- Baseline: TutorPulse V0.2.0
- Implementation status: Not started

This document defines the minimum viable product for the first TutorPulse Phase 2 interactive release. It prevents attractive but non-essential ideas from delaying the complete teacher and student demonstration.

## What MVP means for TutorPulse

For this portfolio project, the MVP is not the smallest collection of pages that can be displayed. It is the smallest complete and credible demonstration of the planned product story.

The MVP must allow a visitor to understand the problem, enter a fictional role, follow a coherent assessment-to-progress workflow and inspect the evidence behind a teacher-reviewed support signal.

The MVP does not need the operational features required by a real school service.

## Intended release posture

Phase 2 is a portfolio demonstration of how TutorPulse could work as an interactive product. It is not a launch to teachers, schools or the general public as an operational educational service.

The interface may contain complete fictional teacher and student workflows, but their purpose is to demonstrate product design and engineering capability. TutorPulse must not invite real schools to onboard, request real learner information or imply that the model has been validated for educational use.

Potential real-world adoption belongs to a separately scoped future phase after appropriate legal, safeguarding, security, accessibility, educational-validation, operational-support and representative-data work.

## Cost boundary

The first Phase 2 release must be buildable and demonstrable for **£0 of additional required infrastructure cost**.

- Prefer open-source frontend, testing, charting, icon and accessibility tools.
- Keep the existing free Render backend and Neon database while they remain suitable.
- Use free static frontend hosting without requiring a custom domain.
- Use standard GitHub-hosted runners for the public repository.
- Do not require a paid design tool, authentication provider, email provider, analytics service or asset licence.
- Do not add a payment method or enable automatic infrastructure upgrades as a project requirement.
- Prefer temporary suspension or reduced availability over an unexpected charge if a free limit is reached.
- Recheck current provider terms and usage before the Phase 2 release because free plans may change.

This boundary concerns required project infrastructure. It does not account for optional AI subscriptions already used during development, the developer's computer or internet connection.

## Prioritisation rules

Capabilities are grouped as:

- **Must have** - required for the first Phase 2 release to tell a complete story.
- **Should have** - valuable when the must-have journey is stable, but removable without breaking the central demonstration.
- **Could have** - optional polish that must not delay testing or release.
- **Will not have in this release** - explicitly deferred to control scope, safety or cost.

Any new proposal must identify which approved journey it supports, its stage dependency and what existing item would be delayed by adding it.

## Must-have capabilities

### Public product introduction

- A polished landing page explaining TutorPulse in plain language.
- A concise statement that the project uses fictional synthetic data.
- Clearly separated **Explore teacher demo** and **Explore student demo** actions.
- A visible but secondary route to the technical repository and API evidence.
- Honest free-hosting, experimental-product and responsible-use information.

### Demonstration identity and role boundary

- Preconfigured fictional teacher and student identities.
- No public signup or collection of personal information.
- A persistent indication of the active fictional role.
- Backend-enforced separation between teacher and student permissions.
- A clear way to leave or reset the demonstration.

### Teacher dashboard and class workflow

- A teacher dashboard summarising classes, recent assessments, marking work and review items.
- A class list and class detail page.
- A fictional learner list without competitive ranking.
- Learner search or filtering appropriate to the small demonstration dataset.
- A learner detail page connecting results, topics and recorded interventions.

### Curriculum representation

- A verified initial GCSE mathematics curriculum structure for one selected exam-board specification.
- Clear Foundation and Higher tier behaviour.
- Curriculum areas, topics and teachable units organised consistently.
- Topic coverage visible during class, learner and assessment workflows.
- The source and version of the curriculum recorded in documentation.

### Assessment creation and assignment

- Assessment list with visible draft, published and assigned states.
- A guided assessment-creation workflow.
- Title, tier, questions, marks and curriculum-topic mappings.
- Running total marks and clear validation.
- Preview before publication.
- Assignment to a fictional class or selected fictional learners.
- Explicit confirmation of recipients and due information.

### Keyboard-friendly marking

- A marking queue showing work that requires attention.
- Efficient keyboard navigation through learners and questions.
- Visible maximum marks and immediate validation.
- Clear saved, unsaved, incomplete and finalised states.
- A deliberate review step before finalisation.
- Topic-level evidence traceable to the assessment and question.

### Teacher progress and judgment

- Class and learner progress views.
- Topic-level progress with labels as well as colour.
- A transparent explanation of the evidence contributing to each summary.
- Honest low-evidence or mixed-evidence states.
- A teacher-reviewed support signal that preserves the frozen V0.2.0 model contract.
- Clear separation between model probability, decision threshold, academic support threshold and teacher judgment.
- No automatic intervention or educational decision.

### Student experience

- A simpler student dashboard.
- Read-only assigned-assessment information.
- Read-only recent results.
- Topic-level progress and evidence explanations written in supportive language.
- Constructive next steps without fixed-ability labels.
- No access to another learner's information, internal teacher notes or raw risk labels.

### Product quality

- Responsive layouts for desktop, tablet and mobile widths.
- Keyboard-operable navigation and workflows.
- Visible focus, labels, validation and error messages.
- Meaning never communicated through colour alone.
- Loading, empty, error, unavailable and forbidden states.
- Automated frontend, API, authorization and end-to-end tests proportionate to risk.
- A deployed interactive demonstration and documented evidence.

## Should-have capabilities

These may be included after the must-have journeys work reliably:

- A short optional guided tour for first-time visitors.
- Dashboard filtering by class, assessment or curriculum area.
- A timeline combining recent assessment and intervention evidence.
- A fictional teacher note or planned-support action using the approved safe demo-write strategy.
- Printable or exportable learner-progress summary without personal information.
- Carefully limited motion and transitions that respect reduced-motion preferences.
- A concise in-product explanation of how progress is calculated.
- A demonstration reset action when the selected data strategy requires one.

## Could-have capabilities

These are polish rather than release requirements:

- Theme selection, including a dark theme.
- Richer chart transitions.
- Customisable dashboard-card ordering.
- A presentation or guided-demo mode for interviews.
- Additional fictional classes and student profiles.
- Non-essential charts that do not add new decision evidence.
- A downloadable demonstration report.

## Explicitly deferred from the first Phase 2 release

### Accounts and organisations

- Public self-service registration.
- Real teacher or student accounts.
- Verified email, password recovery or multi-factor authentication.
- Parent or guardian accounts.
- School administrator accounts.
- Multiple schools, organisations or teacher collaboration.
- Production identity-provider integration.

### Commercial and operational functionality

- Payments, subscriptions, invoices or pricing plans.
- Custom domains or paid infrastructure as a requirement.
- Production support tooling or service-level guarantees.
- Marketing automation, analytics or behavioural tracking.
- Real email, SMS or push notifications.

### Data and integrations

- Real learner, teacher, parent or school information.
- CSV roster imports.
- Management-information-system integrations.
- Multiple subjects or exam boards.
- Large-scale data migration.
- Live production monitoring of educational outcomes.

### Learning-platform expansion

- Students completing assessments online.
- Automatic marking of student answers.
- Question banks generated by artificial intelligence.
- Lesson planning, homework delivery or content authoring.
- Messaging between teachers and students.
- Gamification, leaderboards or student comparison.

### Model expansion

- Retraining or retuning the V0.2.0 model.
- Changing the frozen 18-feature request contract.
- Changing the `0.38` decision threshold.
- Automated intervention creation.
- Prescriptive educational recommendations.
- Claims of real-world accuracy, fairness or educational effectiveness.

## MVP journey traceability

| Approved journey | Minimum supporting capability | Planned stage |
|---|---|---|
| Visitor understands the project | Landing page, limitations and role selection | Stages 12 and 17 |
| Teacher reviews class and learner | Roles, classes, learners and topic evidence | Stages 11, 13 and 16 |
| Teacher creates and assigns assessment | Curriculum, assessment builder and assignment | Stages 10 and 14 |
| Teacher records marks | Question-level structure and marking workflow | Stages 10 and 15 |
| Student reviews progress | Role isolation, results and student progress view | Stages 11 and 16 |
| Visitor sees a governed support signal | Existing model contract, evidence explanation and teacher judgment | Stages 16 and 17 |

## Public demonstration boundary

The first Phase 2 release may feel interactive, but it must not permit anonymous visitors to corrupt a permanent shared dataset.

Before any demonstration write is implemented, a later stage must choose and test one of these approaches:

1. session-isolated temporary backend data;
2. periodically reset synthetic demo data with abuse controls;
3. browser-only simulated changes that never reach the shared database; or
4. another documented design offering equivalent isolation and recovery.

The existing V0.2.0 public API remains read-only until that decision has been implemented and verified. Visual mockups must not be mistaken for proof that secure writes exist.

## MVP release test

The Phase 2 MVP is complete only when an external reviewer can:

1. open the product without an account;
2. understand that it uses synthetic data;
3. enter the teacher demonstration;
4. move from a class to a learner and inspect topic evidence;
5. understand how a teacher-reviewed support signal relates to that evidence;
6. understand the planned assessment and marking workflow through working, safely isolated functionality;
7. enter the student demonstration and understand assignments, results and progress;
8. complete the journeys using a keyboard and at mobile width;
9. encounter clear failure states rather than unexplained blank screens; and
10. distinguish implemented behaviour from project limitations and future ambitions.

## Scope-change rule

An idea discovered during implementation is not automatically added to the MVP. Record it first, classify it as must, should, could or deferred, and assess its effect on the agreed journeys, safety controls, stage order and release date.

The default decision is to defer an idea unless omitting it would break a must-have journey, privacy control, accessibility requirement or verified data contract.

## Approved scope decisions

The Stage 9 MVP scope is approved with the following interpretation:

1. All must-have capabilities are retained to create the complete portfolio demonstration described in the Phase 2 plan.
2. Assessment creation and keyboard-friendly marking remain must-have product workflows.
3. The initial student experience remains read-only for assignments, results and progress.
4. Recording a fictional support action remains should-have rather than release-critical.
5. Deferred features are not necessary for the first Phase 2 release.
6. New ideas are deferred by default unless they are necessary for an approved journey, safety requirement, accessibility requirement or verified data contract.
7. The release remains a fictional portfolio demonstration and does not encourage teachers or schools to adopt it operationally.
8. No listed must-have capability requires paid infrastructure for the planned portfolio-scale release.

## Stage boundary

This scope is a product-planning decision. No listed capability is complete merely because it appears in this document.
