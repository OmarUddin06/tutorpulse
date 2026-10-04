# TutorPulse Initial Database Design

## Purpose

TutorPulse will store fictional and anonymised learner assessment data so that tutors can monitor performance, identify topic-level learning gaps and record support interventions.

This document describes the proposed initial design. It may be refined before the database migration is implemented.

## Questions the database should answer

The database should eventually make it possible to answer questions such as:

- Which assessments has a learner completed?
- What result did a learner achieve for each topic?
- Which topics have the lowest average results?
- Which learners may require additional support?
- Which interventions have been recorded for a learner?
- Is an intervention associated with a particular topic?
- Which interventions are still active or have been completed?

## Scope

The initial database will contain:

- Fictional, anonymised learners
- Assessments
- Curriculum topics
- Topic-level assessment results
- Learner interventions

The initial database will not contain:

- Real student names or personal information
- Authentication or password data
- Tutor accounts
- Attendance information
- Uploaded files
- Email or messaging features

These features may be considered later but are outside the initial scope.

## Proposed entities

### Learners

Represents an anonymised learner whose progress is being monitored.

Proposed fields:

- `id` — unique identifier and primary key
- `display_name` — fictional or anonymised name used in the application
- `created_at` — date and time the learner record was created

A learner can have many assessment results and many interventions.

### Assessments

Represents a test, quiz, assignment or other assessed activity.

Proposed fields:

- `id` — unique identifier and primary key
- `title` — descriptive assessment title
- `assessment_date` — date on which the assessment occurred
- `created_at` — date and time the assessment record was created

An assessment can produce many topic-level results.

### Topics

Represents an area of knowledge that can be measured in an assessment.

Proposed fields:

- `id` — unique identifier and primary key
- `name` — unique topic name
- `description` — optional explanation of the topic
- `created_at` — date and time the topic record was created

A topic can appear in many assessment results and may be connected to many interventions.

### Assessment results

Represents one learner's result for one topic within one assessment.

Proposed fields:

- `id` — unique identifier and primary key
- `learner_id` — foreign key referencing `learners`
- `assessment_id` — foreign key referencing `assessments`
- `topic_id` — foreign key referencing `topics`
- `score` — points achieved by the learner
- `maximum_score` — maximum available points
- `created_at` — date and time the result was recorded

The combination of `learner_id`, `assessment_id` and `topic_id` should be unique. This prevents the same topic result from being recorded twice for the same learner and assessment.

The percentage can be calculated from `score` and `maximum_score` instead of being stored separately. This avoids storing two values that could become inconsistent.

### Interventions

Represents additional support or action recorded for a learner.

Proposed fields:

- `id` — unique identifier and primary key
- `learner_id` — foreign key referencing `learners`
- `topic_id` — optional foreign key referencing `topics`
- `summary` — description of the support being provided
- `status` — whether the intervention is planned, active or completed
- `created_at` — date and time the intervention was created
- `completed_at` — optional completion date and time

Every intervention belongs to one learner. An intervention may optionally target one topic.

## Proposed relationships

- One learner can have many assessment results.
- Each assessment result belongs to one learner.
- One assessment can have many assessment results.
- Each assessment result belongs to one assessment.
- One topic can appear in many assessment results.
- Each assessment result refers to one topic.
- One learner can have many interventions.
- Each intervention belongs to one learner.
- One topic can be associated with many interventions.
- An intervention may be associated with zero or one topic.

## Important design rules

- All learner data must be fictional or anonymised.
- Primary keys uniquely identify individual records.
- Foreign keys connect related records in different tables.
- Scores must not be negative.
- `maximum_score` must be greater than zero.
- A score must not exceed its maximum score.
- Topic names should be unique.
- Duplicate results for the same learner, assessment and topic must be prevented.
- Intervention status should use a controlled set of accepted values.
- A completed intervention may have a completion date.
- Percentages should be calculated from the stored score values.

## Assumptions requiring validation

The initial design assumes that:

- Assessments can measure more than one topic.
- A learner receives one result per topic within an assessment.
- An intervention always belongs to a learner.
- Associating an intervention with a topic is optional.
- Authentication and tutor accounts are not needed in the initial database.

These assumptions should be reviewed before the SQL migration is implemented.
