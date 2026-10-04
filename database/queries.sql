-- TutorPulse reporting and validation queries.
-- These queries are read-only and can be executed repeatedly.

-- Query 1: List every learner alphabetically.
SELECT
    id,
    display_name,
    created_at
FROM learners
ORDER BY display_name;


-- Query 2: List assessments from newest to oldest.
SELECT
    id,
    title,
    assessment_date
FROM assessments
ORDER BY assessment_date DESC, title;


-- Query 3: Show every topic result with its calculated percentage.
SELECT
    learners.display_name,
    assessments.title AS assessment,
    topics.name AS topic,
    assessment_results.score,
    assessment_results.maximum_score,
    ROUND(
        100 * assessment_results.score
        / assessment_results.maximum_score,
        2
    ) AS percentage
FROM assessment_results
JOIN learners
    ON learners.id = assessment_results.learner_id
JOIN assessments
    ON assessments.id = assessment_results.assessment_id
JOIN topics
    ON topics.id = assessment_results.topic_id
ORDER BY
    learners.display_name,
    assessments.assessment_date,
    topics.name;


-- Query 4: Calculate each learner's overall percentage.
SELECT
    learners.display_name,
    ROUND(
        100 * SUM(assessment_results.score)
        / SUM(assessment_results.maximum_score),
        2
    ) AS overall_percentage
FROM learners
JOIN assessment_results
    ON assessment_results.learner_id = learners.id
GROUP BY learners.id, learners.display_name
ORDER BY overall_percentage DESC;


-- Query 5: Find learners whose overall percentage is below 60%.
SELECT
    learners.display_name,
    ROUND(
        100 * SUM(assessment_results.score)
        / SUM(assessment_results.maximum_score),
        2
    ) AS overall_percentage
FROM learners
JOIN assessment_results
    ON assessment_results.learner_id = learners.id
GROUP BY learners.id, learners.display_name
HAVING
    100 * SUM(assessment_results.score)
    / SUM(assessment_results.maximum_score) < 60
ORDER BY overall_percentage ASC;


-- Query 6: Calculate the average performance for every topic.
SELECT
    topics.name AS topic,
    ROUND(
        100 * SUM(assessment_results.score)
        / SUM(assessment_results.maximum_score),
        2
    ) AS average_percentage
FROM topics
JOIN assessment_results
    ON assessment_results.topic_id = topics.id
GROUP BY topics.id, topics.name
ORDER BY average_percentage DESC;


-- Query 7: Identify the topic with the lowest average performance.
SELECT
    topics.name AS weakest_topic,
    ROUND(
        100 * SUM(assessment_results.score)
        / SUM(assessment_results.maximum_score),
        2
    ) AS average_percentage
FROM topics
JOIN assessment_results
    ON assessment_results.topic_id = topics.id
GROUP BY topics.id, topics.name
ORDER BY average_percentage ASC
LIMIT 1;


-- Query 8: Calculate the average performance for every assessment.
SELECT
    assessments.title,
    assessments.assessment_date,
    ROUND(
        100 * SUM(assessment_results.score)
        / SUM(assessment_results.maximum_score),
        2
    ) AS average_percentage
FROM assessments
JOIN assessment_results
    ON assessment_results.assessment_id = assessments.id
GROUP BY
    assessments.id,
    assessments.title,
    assessments.assessment_date
ORDER BY assessments.assessment_date DESC;


-- Query 9: List planned and active interventions with learner and topic details.
SELECT
    learners.display_name,
    topics.name AS topic,
    interventions.summary,
    interventions.status,
    interventions.created_at
FROM interventions
JOIN learners
    ON learners.id = interventions.learner_id
LEFT JOIN topics
    ON topics.id = interventions.topic_id
WHERE interventions.status IN ('planned', 'active')
ORDER BY interventions.created_at;


-- Query 10: Find learners who do not currently have an intervention.
SELECT
    learners.id,
    learners.display_name
FROM learners
LEFT JOIN interventions
    ON interventions.learner_id = learners.id
WHERE interventions.id IS NULL
ORDER BY learners.display_name;


-- Query 11: Compare each learner's fractions results across assessments.
SELECT
    learners.display_name,
    MAX(
        CASE
            WHEN assessments.title = 'Autumn Diagnostic'
            THEN ROUND(
                100 * assessment_results.score
                / assessment_results.maximum_score,
                2
            )
        END
    ) AS diagnostic_percentage,
    MAX(
        CASE
            WHEN assessments.title = 'Fractions Checkpoint'
            THEN ROUND(
                100 * assessment_results.score
                / assessment_results.maximum_score,
                2
            )
        END
    ) AS checkpoint_percentage,
    MAX(
        CASE
            WHEN assessments.title = 'Fractions Checkpoint'
            THEN ROUND(
                100 * assessment_results.score
                / assessment_results.maximum_score,
                2
            )
        END
    )
    -
    MAX(
        CASE
            WHEN assessments.title = 'Autumn Diagnostic'
            THEN ROUND(
                100 * assessment_results.score
                / assessment_results.maximum_score,
                2
            )
        END
    ) AS percentage_point_change
FROM learners
JOIN assessment_results
    ON assessment_results.learner_id = learners.id
JOIN assessments
    ON assessments.id = assessment_results.assessment_id
JOIN topics
    ON topics.id = assessment_results.topic_id
WHERE topics.name = 'Fractions'
GROUP BY learners.id, learners.display_name
HAVING COUNT(DISTINCT assessments.id) = 2
ORDER BY percentage_point_change DESC;


-- Query 12: Count interventions in each status.
SELECT
    status,
    COUNT(*) AS intervention_count
FROM interventions
GROUP BY status
ORDER BY status;