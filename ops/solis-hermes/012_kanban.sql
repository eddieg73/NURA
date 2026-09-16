-- 012_kanban.sql
-- OPERATOR REQUIREMENT (2026-09-15):
--   "a board for the community paramedic and population with an alert on Kanban
--    to start seeing a patient"
--
-- Two boards: Community Paramedic (MIH field work) and Population Health.
-- An ALERT is raised when a member crosses into "should be seen now" — that is
-- the operator's "start seeing a patient" trigger. Alerts are durable rows, not
-- transient notifications, so nothing depends on a UI being open to notice.

CREATE TABLE IF NOT EXISTS kanban_boards (
    board_code  TEXT PRIMARY KEY,
    board_label TEXT NOT NULL,
    owner_role  TEXT NOT NULL,
    description TEXT,
    sort_order  INTEGER NOT NULL DEFAULT 100
);
INSERT INTO kanban_boards (board_code, board_label, owner_role, description, sort_order) VALUES
    ('COMMUNITY_PARAMEDIC', 'Community Paramedic (MIH)', 'community_paramedic',
     'Field worklist for the mobile integrated health team. Alerts fire when a member '
     'meets criteria to start being seen.', 1),
    ('POPULATION_HEALTH', 'Population Health', 'care_manager',
     'Panel-level work: care gaps, plan alignment, outreach, RAF capture.', 2)
ON CONFLICT (board_code) DO UPDATE
    SET board_label = EXCLUDED.board_label, owner_role = EXCLUDED.owner_role,
        description = EXCLUDED.description, sort_order = EXCLUDED.sort_order;

CREATE TABLE IF NOT EXISTS kanban_columns (
    board_code  TEXT NOT NULL REFERENCES kanban_boards (board_code) ON DELETE CASCADE,
    column_code TEXT NOT NULL,
    column_label TEXT NOT NULL,
    is_terminal BOOLEAN NOT NULL DEFAULT false,
    sort_order  INTEGER NOT NULL DEFAULT 100,
    PRIMARY KEY (board_code, column_code)
);
INSERT INTO kanban_columns (board_code, column_code, column_label, is_terminal, sort_order) VALUES
    ('COMMUNITY_PARAMEDIC','ALERTED',   'Alerted — start seeing', false, 1),
    ('COMMUNITY_PARAMEDIC','SCHEDULED', 'Scheduled',              false, 2),
    ('COMMUNITY_PARAMEDIC','EN_ROUTE',  'En route',               false, 3),
    ('COMMUNITY_PARAMEDIC','SEEN',      'Seen',                   false, 4),
    ('COMMUNITY_PARAMEDIC','FOLLOWUP',  'Needs follow-up',        false, 5),
    ('COMMUNITY_PARAMEDIC','CLOSED',    'Closed',                 true,  6),
    ('POPULATION_HEALTH','NEW',         'New',                    false, 1),
    ('POPULATION_HEALTH','OUTREACH',    'Outreach',               false, 2),
    ('POPULATION_HEALTH','AWAITING_PROVIDER','Awaiting provider', false, 3),
    ('POPULATION_HEALTH','DONE',        'Done',                   true,  4)
ON CONFLICT (board_code, column_code) DO UPDATE
    SET column_label = EXCLUDED.column_label,
        is_terminal = EXCLUDED.is_terminal, sort_order = EXCLUDED.sort_order;

CREATE TABLE IF NOT EXISTS kanban_cards (
    id            BIGSERIAL PRIMARY KEY,
    board_code    TEXT NOT NULL REFERENCES kanban_boards (board_code) ON DELETE CASCADE,
    column_code   TEXT NOT NULL,
    member_number TEXT NOT NULL,
    payer_code    TEXT,
    title         TEXT NOT NULL,
    reason        TEXT,
    priority      TEXT NOT NULL DEFAULT 'MEDIUM',
    assigned_to   TEXT,
    due_on        DATE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at     TIMESTAMPTZ,
    FOREIGN KEY (board_code, column_code) REFERENCES kanban_columns (board_code, column_code)
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_kanban_open_card
    ON kanban_cards (board_code, member_number) WHERE closed_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_kanban_board_col ON kanban_cards (board_code, column_code);

-- ------------------------------------------------------------- the ALERT ------
CREATE TABLE IF NOT EXISTS kanban_alerts (
    id            BIGSERIAL PRIMARY KEY,
    board_code    TEXT NOT NULL REFERENCES kanban_boards (board_code) ON DELETE CASCADE,
    member_number TEXT NOT NULL,
    alert_type    TEXT NOT NULL,
    severity      TEXT NOT NULL DEFAULT 'MEDIUM',
    headline      TEXT NOT NULL,
    detail        TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by TEXT,
    CONSTRAINT kanban_alerts_uniq UNIQUE (board_code, member_number, alert_type)
);
CREATE INDEX IF NOT EXISTS idx_kanban_alerts_open
    ON kanban_alerts (board_code, acknowledged_at, severity);

-- Alert rules — data, not code, so thresholds are tunable by staff.
CREATE TABLE IF NOT EXISTS alert_rules (
    rule_code   TEXT PRIMARY KEY,
    board_code  TEXT NOT NULL REFERENCES kanban_boards (board_code),
    alert_type  TEXT NOT NULL,
    severity    TEXT NOT NULL,
    condition   TEXT NOT NULL,
    headline    TEXT NOT NULL,
    enabled     BOOLEAN NOT NULL DEFAULT true
);
INSERT INTO alert_rules (rule_code, board_code, alert_type, severity, condition, headline) VALUES
    ('MIH_DISCHARGE',      'COMMUNITY_PARAMEDIC','DISCHARGE_FOLLOWUP','HIGH',
     'member discharged from inpatient within 7 days and no MIH visit recorded',
     'Post-discharge: start seeing this patient'),
    ('MIH_HIGH_RISK',      'COMMUNITY_PARAMEDIC','HIGH_RISK_VISIT','HIGH',
     'member has 2+ open care gaps AND a HIGH plan exception',
     'High utilizer with open gaps: start seeing this patient'),
    ('MIH_NO_FOLLOWUP',    'COMMUNITY_PARAMEDIC','NO_FOLLOWUP','MEDIUM',
     'member flagged discharged with no follow-up scheduled',
     'No follow-up scheduled: start seeing this patient'),
    ('MIH_OVERDUE_MEASURE','COMMUNITY_PARAMEDIC','OVERDUE_MEASURES','MEDIUM',
     'member has 3+ OVERDUE preventive measures',
     'Multiple overdue preventive measures: start seeing this patient'),
    ('PH_PLAN_MISMATCH',   'POPULATION_HEALTH', 'PLAN_MISMATCH','HIGH',
     'open plan exception where severity = HIGH',
     'Plan mismatch: member may be on the wrong plan'),
    ('PH_OFF_PLAN',        'POPULATION_HEALTH', 'OFF_PLAN','MEDIUM',
     'any open plan exception',
     'Member is off their qualifying plan')
ON CONFLICT (rule_code) DO UPDATE
    SET board_code = EXCLUDED.board_code, alert_type = EXCLUDED.alert_type,
        severity = EXCLUDED.severity, condition = EXCLUDED.condition,
        headline = EXCLUDED.headline;

CREATE OR REPLACE VIEW v_kanban_board AS
SELECT c.board_code, b.board_label, c.column_code, k.column_label, k.sort_order,
       c.member_number, c.payer_code, c.title, c.priority, c.assigned_to, c.due_on,
       (SELECT count(*) FROM kanban_alerts a
         WHERE a.member_number = c.member_number
           AND a.board_code = c.board_code
           AND a.acknowledged_at IS NULL) AS open_alerts
FROM kanban_cards c
JOIN kanban_boards  b ON b.board_code = c.board_code
JOIN kanban_columns k ON k.board_code = c.board_code AND k.column_code = c.column_code
ORDER BY c.board_code, k.sort_order, c.priority DESC;

CREATE OR REPLACE VIEW v_open_alerts AS
SELECT a.id, a.board_code, a.member_number, a.alert_type, a.severity,
       a.headline, a.detail, a.created_at,
       (current_date - a.created_at::date) AS age_days
FROM kanban_alerts a
WHERE a.acknowledged_at IS NULL
ORDER BY (a.severity = 'HIGH') DESC, a.created_at;
