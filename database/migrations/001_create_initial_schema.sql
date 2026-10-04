-- Create the initial TutorPulse database schema.
-- All learner information used by TutorPulse must be fictional or anonymised.

BEGIN;

CREATE TABLE learners (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    display_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT learners_display_name_not_blank
        CHECK (BTRIM(display_name) <> '')
);

CREATE TABLE assessments (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    assessment_date DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT assessments_title_not_blank
        CHECK (BTRIM(title) <> '')
);

CREATE TABLE topics (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT topics_name_not_blank
        CHECK (BTRIM(name) <> '')
);

CREATE TABLE assessment_results (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    learner_id BIGINT NOT NULL,
    assessment_id BIGINT NOT NULL,
    topic_id BIGINT NOT NULL,
    score NUMERIC(7, 2) NOT NULL,
    maximum_score NUMERIC(7, 2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT assessment_results_learner_fk
        FOREIGN KEY (learner_id)
        REFERENCES learners (id)
        ON DELETE CASCADE,

    CONSTRAINT assessment_results_assessment_fk
        FOREIGN KEY (assessment_id)
        REFERENCES assessments (id)
        ON DELETE CASCADE,

    CONSTRAINT assessment_results_topic_fk
        FOREIGN KEY (topic_id)
        REFERENCES topics (id)
        ON DELETE RESTRICT,

    CONSTRAINT assessment_results_score_nonnegative
        CHECK (score >= 0),

    CONSTRAINT assessment_results_maximum_positive
        CHECK (maximum_score > 0),

    CONSTRAINT assessment_results_score_within_maximum
        CHECK (score <= maximum_score),

    CONSTRAINT assessment_results_unique_entry
        UNIQUE (learner_id, assessment_id, topic_id)
);

CREATE TABLE interventions (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    learner_id BIGINT NOT NULL,
    topic_id BIGINT,
    summary TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'planned',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,

    CONSTRAINT interventions_learner_fk
        FOREIGN KEY (learner_id)
        REFERENCES learners (id)
        ON DELETE CASCADE,

    CONSTRAINT interventions_topic_fk
        FOREIGN KEY (topic_id)
        REFERENCES topics (id)
        ON DELETE SET NULL,

    CONSTRAINT interventions_summary_not_blank
        CHECK (BTRIM(summary) <> ''),

    CONSTRAINT interventions_status_valid
        CHECK (status IN ('planned', 'active', 'completed')),

    CONSTRAINT interventions_completion_consistent
        CHECK (
            (status = 'completed' AND completed_at IS NOT NULL)
            OR
            (status <> 'completed' AND completed_at IS NULL)
        )
);

COMMIT;