# TutorPulse Modelling Scope

## Purpose

This document defines the modelling question, prediction point, target, permitted features, leakage controls and evaluation split for TutorPulse.

It acts as a contract for the data-preparation work completed during Stage 5. Model training is outside the scope of this stage and will take place during Stage 6.

## Modelling question

Using only a learner's assessment history and intervention information available before a future assessment, can TutorPulse predict whether the learner's next assessment result for a topic will fall below the agreed support threshold?

The prediction is intended to help tutors identify learners who may benefit from additional support. It must not be used as an automatic or punitive decision.

## Prediction unit

One modelling row represents one learner-assessment-topic result.

For example, if one learner completes an assessment covering Algebra, Fractions and Geometry, the dataset may contain three rows for that learner and assessment: one row for each topic.

## Prediction point

The prediction point is immediately before the target assessment takes place.

Because the current database records an assessment date but not an assessment time, only information from an earlier calendar date is considered available.

This means:

- historical results must have an `assessment_date` earlier than the target `assessment_date`;
- results from the same assessment date are excluded from the feature history;
- interventions must have a `created_at` date earlier than the target `assessment_date`;
- information created on or after the target assessment date is excluded.

Using a strict earlier-date rule prevents accidental leakage when the order of events within one day is unknown.

## Target definition

The raw result percentage is calculated as:

`result_percentage = (score / maximum_score) * 100`

The binary target is called `needs_support`.

- `needs_support = 1` when `result_percentage < 60`
- `needs_support = 0` when `result_percentage >= 60`

The 60% threshold is a transparent project assumption. It is not presented as a universal educational standard and should be configurable in future versions.

The target is used to frame the task as binary classification.

## Information permitted as features

Features may only be calculated from information available before the prediction point.

Potential permitted features include:

- the target topic treated as a categorical feature;
- the target assessment's maximum score, when known before the assessment;
- the number of previous assessment results;
- the learner's average previous result percentage;
- the learner's most recent previous result percentage;
- the learner's minimum and maximum previous percentages;
- the number of previous results below the support threshold;
- the proportion of previous results below the support threshold;
- previous performance in the same topic;
- the number of earlier assessments completed;
- the number of days since the learner's previous assessment;
- the number of interventions created before the target assessment;
- the number of earlier topic-specific interventions;
- whether an earlier intervention had already been completed before the target assessment.

Historical aggregates must be recalculated separately for every target row using only earlier records.

## Information prohibited as features

The following information must not be supplied to a model for the target row:

- the target result's score;
- the target result's calculated percentage;
- the `needs_support` target itself;
- the target result's `created_at` value;
- results from the same assessment date;
- results from future assessment dates;
- interventions created on or after the target assessment date;
- an intervention completion status that was only known after the prediction point;
- database primary keys used as numeric predictive signals;
- the learner's display name;
- information derived using the complete dataset before it is split.

Learner identifiers may be retained temporarily for grouping, ordering and validation, but they will not be used as predictive features.

Topic identifiers must be treated as categories rather than continuous numeric measurements.

## Leakage-safe splitting strategy

The prepared modelling dataset will be divided chronologically.

- The earliest assessment period will form the training set.
- A later period will form the validation set.
- The most recent period will form the test set.

A random row-level split will not be used because it could place future results in training while earlier results from the same learners appear in validation or testing.

The test period must remain untouched during feature selection, preprocessing decisions and model selection.

Any preprocessing that learns values from data must be fitted using the training set only.

## Current data audit

The initial TutorPulse seed data contains:

- 4 learners;
- 3 topics;
- 2 assessments;
- 16 assessment results;
- 3 interventions.

The two assessment dates are 15 September 2026 and 29 September 2026.

The observed result percentages range from 35% to 90%. Using the below-60% target definition, 7 of the 16 existing results are positive support cases.

The current dataset is useful for testing the database and API but is too small for meaningful exploratory modelling. It also has too few assessment dates to create separate chronological training, validation and test periods.

A reproducible synthetic-data generator is therefore required.

## Timestamp limitation

The seeded assessment records have `created_at` timestamps later than their stated `assessment_date` values because the records were inserted after the fictional assessments took place.

For modelling chronology:

- `assessments.assessment_date` is the authoritative event date for results;
- `assessment_results.created_at` is treated as database-entry metadata;
- `assessment_results.created_at` must not determine feature availability;
- `interventions.created_at` remains the event timestamp for interventions.

This decision prevents data-loading timestamps from being mistaken for real educational chronology.

## Synthetic-data requirements

The synthetic dataset must:

- contain only fictional learner identities;
- use a fixed random seed so that generation is reproducible;
- contain enough learners and assessment dates for chronological splitting;
- contain multiple topics;
- produce both support and non-support target cases;
- include realistic differences between learners and topics;
- contain performance patterns that change over time;
- respect all PostgreSQL constraints;
- avoid duplicate learner-assessment-topic results;
- keep scores between zero and the maximum score;
- produce valid intervention statuses and completion timestamps;
- be safe to regenerate without silently corrupting existing development data.

The generator must make its assumptions explicit and must not pretend that synthetic patterns represent real educational evidence.

## Database constraints that must be preserved

Generated data must obey the following rules:

- learner names cannot be blank;
- assessment titles cannot be blank;
- topic names must be unique and non-blank;
- scores cannot be negative;
- maximum scores must be greater than zero;
- scores cannot exceed their maximum scores;
- each learner-assessment-topic combination must be unique;
- intervention summaries cannot be blank;
- intervention status must be `planned`, `active` or `completed`;
- completed interventions require a completion timestamp;
- non-completed interventions must not have a completion timestamp.

## Ethical and practical limitations

TutorPulse currently uses synthetic and anonymised data. Results from this project do not demonstrate effectiveness with real learners.

A future production system would require:

- an appropriate lawful basis for processing educational data;
- security and access controls;
- monitoring for unfair differences between learner groups;
- human review of predictions;
- procedures for correcting inaccurate data;
- clear communication that predictions express uncertainty;
- evaluation using representative real-world data.

False negatives are particularly important because they represent learners who may need support but are not identified by the system. False positives also matter because unnecessary interventions can consume tutor time and affect learner trust.

## Stage 5 deliverables

Stage 5 will produce:

- a reproducible analysis environment;
- a documented modelling question and target;
- a reproducible synthetic-data generator;
- automated data-quality tests;
- an exploratory analysis;
- a leakage-safe feature-building process;
- chronological training, validation and test datasets;
- documentation of assumptions and limitations.

Stage 5 will not train, select or deploy a predictive model. Those activities belong to later TutorPulse stages.