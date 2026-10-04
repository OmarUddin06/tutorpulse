-- Add fictional development data to the TutorPulse database.
-- None of the records in this file represent real people.

BEGIN;

INSERT INTO learners (display_name)
VALUES
    ('Learner 001'),
    ('Learner 002'),
    ('Learner 003'),
    ('Learner 004');

INSERT INTO assessments (title, assessment_date)
VALUES
    ('Autumn Diagnostic', DATE '2026-09-15'),
    ('Fractions Checkpoint', DATE '2026-09-29');

INSERT INTO topics (name, description)
VALUES
    ('Algebra', 'Using symbols and equations to represent relationships.'),
    ('Fractions', 'Understanding and calculating with fractional values.'),
    ('Geometry', 'Working with shapes, measurements and spatial reasoning.');

INSERT INTO assessment_results (
    learner_id,
    assessment_id,
    topic_id,
    score,
    maximum_score
)
SELECT
    learners.id,
    assessments.id,
    topics.id,
    sample.score,
    sample.maximum_score
FROM (
    VALUES
        ('Learner 001', 'Autumn Diagnostic', 'Algebra', 16.00, 20.00),
        ('Learner 001', 'Autumn Diagnostic', 'Fractions', 14.00, 20.00),
        ('Learner 001', 'Autumn Diagnostic', 'Geometry', 17.00, 20.00),

        ('Learner 002', 'Autumn Diagnostic', 'Algebra', 11.00, 20.00),
        ('Learner 002', 'Autumn Diagnostic', 'Fractions', 8.00, 20.00),
        ('Learner 002', 'Autumn Diagnostic', 'Geometry', 13.00, 20.00),

        ('Learner 003', 'Autumn Diagnostic', 'Algebra', 18.00, 20.00),
        ('Learner 003', 'Autumn Diagnostic', 'Fractions', 16.00, 20.00),
        ('Learner 003', 'Autumn Diagnostic', 'Geometry', 15.00, 20.00),

        ('Learner 004', 'Autumn Diagnostic', 'Algebra', 9.00, 20.00),
        ('Learner 004', 'Autumn Diagnostic', 'Fractions', 7.00, 20.00),
        ('Learner 004', 'Autumn Diagnostic', 'Geometry', 10.00, 20.00),

        ('Learner 001', 'Fractions Checkpoint', 'Fractions', 16.00, 20.00),
        ('Learner 002', 'Fractions Checkpoint', 'Fractions', 11.00, 20.00),
        ('Learner 003', 'Fractions Checkpoint', 'Fractions', 18.00, 20.00),
        ('Learner 004', 'Fractions Checkpoint', 'Fractions', 9.00, 20.00)
) AS sample (
    learner_name,
    assessment_title,
    topic_name,
    score,
    maximum_score
)
JOIN learners
    ON learners.display_name = sample.learner_name
JOIN assessments
    ON assessments.title = sample.assessment_title
JOIN topics
    ON topics.name = sample.topic_name;

INSERT INTO interventions (
    learner_id,
    topic_id,
    summary,
    status,
    created_at,
    completed_at
)
SELECT
    learners.id,
    topics.id,
    sample.summary,
    sample.status,
    sample.created_at,
    sample.completed_at
FROM (
    VALUES
        (
            'Learner 002',
            'Fractions',
            'Provide weekly guided fractions practice.',
            'active',
            TIMESTAMPTZ '2026-09-30 09:00:00+01',
            NULL::TIMESTAMPTZ
        ),
        (
            'Learner 004',
            NULL::TEXT,
            'Arrange a general progress review with the learner.',
            'planned',
            TIMESTAMPTZ '2026-10-01 10:00:00+01',
            NULL::TIMESTAMPTZ
        ),
        (
            'Learner 003',
            'Algebra',
            'Complete an additional algebra problem set.',
            'completed',
            TIMESTAMPTZ '2026-09-20 14:00:00+01',
            TIMESTAMPTZ '2026-09-27 14:00:00+01'
        )
) AS sample (
    learner_name,
    topic_name,
    summary,
    status,
    created_at,
    completed_at
)
JOIN learners
    ON learners.display_name = sample.learner_name
LEFT JOIN topics
    ON topics.name = sample.topic_name;

COMMIT;