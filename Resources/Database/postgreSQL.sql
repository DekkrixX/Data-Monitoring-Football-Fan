CREATE TABLE IF NOT EXISTS event
(
    id SERIAL PRIMARY KEY,
    code INT NOT NULL,
    team TEXT,
    event_time TIMESTAMP,
    minute INT
);
