# TutorPulse External Demonstration Feedback

## Purpose

This document records anonymised feedback from an external test of the Stage 8 TutorPulse portfolio deployment and the improvement made in response.

No tester name, contact details or other identifying information are recorded.

## Feedback scope

| Item | Value |
|---|---|
| Feedback date | 10 October 2026 |
| Tester | One anonymised external tester |
| Browser walkthrough | Completed |
| PowerShell walkthrough | Completed |
| Public service | Render Free Docker web service |
| Hosted database | Neon PostgreSQL |

The tester was asked to:

- open the interactive documentation;
- list the four fictional learners;
- submit the supplied fictional prediction request;
- run the technical readiness, learners and prediction commands;
- report anything unclear, slow or unreliable;
- recommend one improvement.

## Successful observations

The tester reported that:

- the interactive page opened successfully without errors;
- the initial free-tier cold start took approximately 30 to 40 seconds;
- the Render loading page made the delay understandable;
- the numbered browser instructions were easy to follow without technical experience;
- `GET /learners` returned four complete fictional learner records;
- the fictional prediction returned immediately after the service had warmed;
- the prediction contained the expected probability, logistic-regression metadata and human-review flag;
- all technical PowerShell commands completed without errors or timeouts;
- `/ready` reported that the application, database and model were ready;
- the use of a reusable `$baseUrl` and PowerShell hashtable kept the technical commands clear.

The feedback therefore supports the conclusion that the hosted API, database, model artifact, browser walkthrough and technical walkthrough are accessible and reliable within the documented free-tier limitation.

## Usability observations

The tester identified two documentation issues:

1. The prediction response was not sufficiently self-explanatory.
   - A probability of approximately `0.41` was returned.
   - The tester could infer that it exceeded the `0.38` decision threshold, but the guide did not explicitly explain that comparison.
   - The separate `60.0` support threshold was not defined alongside the response.
   - The reason `human_review_required` remains `true`, even when a probability is below `0.5`, was not explained.
2. In Windows PowerShell, piping a root JSON array directly into `ConvertTo-Json` can display a `value` wrapper and `Count` property. The tester correctly suspected this was PowerShell presentation rather than the API's response format, but the guide should avoid creating that ambiguity.

The tester also noted that all four learners share a creation timestamp. This is expected because the deterministic seed records were inserted in one batch, but a short explanation improves clarity.

## Prioritised improvement

The highest-value improvement is to explain the prediction response field by field.

This was prioritised because prediction interpretation is central to the purpose and governance of TutorPulse. A reviewer should not need to infer how the probability, decision threshold, academic support threshold and human-review requirement relate to one another.

## Action taken

The README browser walkthrough now:

- defines `support_probability` as a value between zero and one;
- explains that `0.4121` represents approximately 41.21%;
- explains that `predicted_needs_support` is `true` because `0.4121` is greater than the selected `0.38` decision threshold;
- explains that `0.5` is not the active decision threshold;
- distinguishes the model decision threshold from the `60.0` assessment-percentage threshold used to define the training target;
- explains that `human_review_required` is always `true` because TutorPulse provides decision support rather than automatic educational decisions;
- includes an explicit stopping point for non-technical testers.

The technical walkthrough now:

- assigns the learners response to a variable before formatting it;
- displays the learner records as a table;
- prints the actual collection count without the confusing JSON wrapper;
- explains the shared timestamp as a consequence of deterministic batch seeding;
- directs technical testers to the same response-field explanation;
- includes an explicit stopping point before local-development instructions.

## Regression-test decision

No new application regression test was added because the external test found no incorrect runtime behaviour. The improvement changes documentation and interpretation rather than application logic.

Existing automated tests already verify that:

- the decision threshold is returned;
- `predicted_needs_support` follows the probability threshold;
- the academic support threshold is returned;
- the model name and artifact version are returned;
- `human_review_required` is always `true`;
- the inference request and response schemas remain stable.

The README changes were checked for valid fenced-code structure and Git whitespace errors.

## Outcome

External feedback is complete and has been acted on.

The deployment behaved reliably, while the most important explanatory gap was corrected. The demonstration now shows not only that the model returns a result, but also how to interpret that result responsibly.
