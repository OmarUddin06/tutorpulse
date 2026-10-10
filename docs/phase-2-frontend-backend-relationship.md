# TutorPulse Phase 2 Frontend and Backend Relationship

## Document status

- Stage: 9 - Define the Phase 2 product and user experience
- GitHub issue: #18
- Status: Approved architecture handoff
- Baseline: TutorPulse V0.2.0
- Implementation status: Not started

This document records how the planned Phase 2 frontend will relate to the existing FastAPI application. It defines responsibilities and reuse boundaries without implementing new application code.

## Architecture decision

Phase 2 will add a separate React and TypeScript single-page frontend. The frontend will be deployed as static web assets and will communicate with TutorPulse through versioned HTTPS JSON endpoints provided by FastAPI.

FastAPI remains the trusted application boundary. The browser must never connect directly to PostgreSQL, receive database credentials, load the model artifact or reproduce authorization decisions.

```text
Visitor browser
    |
    | HTTPS
    v
React and TypeScript frontend
    |
    | JSON API requests
    v
FastAPI application
    |                 |
    | SQLAlchemy      | governed inference
    v                 v
Neon PostgreSQL    frozen V0.2.0 model artifact
```

The frontend and API may use different free-hosting origins. The API must therefore allow only the exact approved frontend origins through CORS. A wildcard origin must not be combined with credentialed requests.

## Responsibility boundary

### Frontend responsibilities

- Present the approved public, teacher and student experiences.
- Maintain page, filter, sorting and unsaved-form state.
- Perform immediate usability validation while treating API validation as authoritative.
- Display loading, empty, unavailable, forbidden and validation states.
- Use accessible labels, focus behaviour and responsive layouts.
- Display only information permitted for the active fictional role.
- Avoid storing secrets, database URLs or privileged configuration.

### FastAPI responsibilities

- Validate every request independently of the browser.
- Enforce role and resource authorization.
- Read and write PostgreSQL data through controlled services and transactions.
- Apply assessment lifecycle rules and mark constraints.
- Calculate or return progress summaries from traceable stored records.
- Build governed model inputs from trusted stored history where possible.
- Serve the frozen model and preserve its existing inference contract.
- Return stable, typed error responses that the frontend can explain safely.
- Enforce the selected public-demonstration isolation strategy.

### PostgreSQL responsibilities

- Preserve relationships, constraints and chronological records.
- Store only synthetic demonstration information in the public portfolio environment.
- Remain inaccessible from browser code.

## Existing V0.2.0 capabilities and planned reuse

| Existing capability | Phase 2 decision | Reason or required change |
|---|---|---|
| `GET /health` | Reuse unchanged | Basic API liveness remains useful. |
| `GET /ready` | Reuse unchanged | Already verifies database and model readiness. |
| `GET /model/health` | Reuse unchanged | Already exposes safe model metadata and readiness. |
| `POST /predictions/support-risk` | Preserve for compatibility | The frozen 18-feature contract remains valid, but the product frontend should not ask visitors to construct it manually. |
| Learner read endpoints | Reuse foundation, extend representation | Existing fictional learner identity is useful; class membership and role-scoped access are missing. |
| Topic read endpoints | Replace or extend with verified curriculum structure | Existing topics lack specification version, hierarchy and Foundation/Higher eligibility. |
| Assessment endpoints | Extend substantially | Existing assessments have a title and assessment date but no tier, lifecycle, declared total, questions or assignments. |
| Assessment-result endpoints | Migrate or extend | Existing results are one aggregate learner-topic score per assessment; Phase 2 needs question-level marks and traceability. |
| Intervention endpoints | Reuse concept, add role scope | Existing status and completion rules are useful; teacher ownership and safe demo-write behaviour are missing. |
| Read-only demo middleware | Preserve until a safer write strategy is implemented | It currently protects the shared public database from anonymous mutation. |

Existing endpoints must not be removed merely to suit the new interface. Where contracts change incompatibly, introduce versioned or additive Phase 2 endpoints and keep V0.2.0 independently referencable.

## New backend capabilities required later

Later stages must design and implement:

- fictional demo identities and server-enforced teacher/student roles;
- classes and class membership;
- verified Edexcel curriculum domains, topics, units and tier eligibility;
- assessment lifecycle states;
- questions, maximum marks, difficulty and question-topic mappings;
- assignment recipients for whole-class or selected-learner assignment;
- question-level marking and finalisation;
- learner and class progress summaries;
- exact result-history metadata;
- teacher support-review queries; and
- role-filtered student results and progress.

The frontend should receive page-oriented response objects where that reduces excessive browser requests, but the backend must keep the underlying domain rules independent of any one page layout.

## Model integration decision

The frozen V0.2.0 model remains a backend service. Phase 2 does not retrain it, alter its 18-feature contract or change the `0.38` decision threshold.

The existing public prediction endpoint accepts a complete feature payload for technical verification. The planned teacher product should instead request a prediction for an authorised fictional learner and topic, with FastAPI deriving the feature payload from trusted chronological records. The response must still expose the probability, decision threshold, model name, artifact schema version and `human_review_required` value.

A model failure must not prevent the teacher from viewing ordinary assessment results.

## Progress calculation boundary

The coloured topic percentage is a transparent assessment-progress calculation, not the machine-learning probability.

FastAPI should eventually calculate it from question marks, difficulty weights and question-topic allocation rules defined and tested in later stages. The API response must include enough explanation for the frontend to display:

- percentage;
- progress band;
- contributing-result count;
- latest-result date;
- provisional or not-yet-assessed state; and
- source assessment and question references.

## Demonstration writes

The existing hosted API remains read-only until a safe strategy is selected and verified. Phase 2 may later use session-isolated temporary data, resettable synthetic data, browser-only simulation or another documented approach.

Whichever approach is chosen must:

- prevent one public visitor from corrupting the shared demonstration;
- avoid real information;
- provide a predictable reset path;
- preserve teacher/student authorization boundaries; and
- remain within the project's free-cost boundary.

## Error and availability behaviour

- The frontend distinguishes API unavailable, model unavailable, forbidden, not found and validation failure.
- FastAPI never returns credentials, stack traces or internal infrastructure details to the browser.
- A Render cold start is explained without promising an exact wake time.
- Static landing-page information remains usable while the API wakes.
- Unsaved user input is preserved where safe after a recoverable request failure.

## Testing handoff

Later implementation stages must add:

- frontend component and accessibility tests;
- API contract tests for new endpoints;
- PostgreSQL integration tests for new constraints;
- role and resource-authorization tests;
- progress-calculation examples and boundary tests;
- end-to-end teacher and student journeys; and
- deployed smoke tests covering the frontend-to-API connection.

## Stage boundary

This document approves the relationship and reuse strategy. No React application, API endpoint, database migration, CORS configuration or authentication mechanism was implemented during Stage 9.
