CREATE TABLE IF NOT EXISTS team
(
    id SERIAL PRIMARY KEY,
    name TEXT,
    coach TEXT
);

CREATE TABLE IF NOT EXISTS player
(
    id SERIAL PRIMARY KEY,
    team INT,
    name TEXT,
    player_number INT,
    FOREIGN KEY (team) REFERENCES team(id)
);

CREATE TABLE IF NOT EXISTS match
(
    id SERIAL PRIMARY KEY,
    ts TIMESTAMP,
    domicile INT,
    exterieur INT,
    stadium TEXT,
    config TEXT,
    FOREIGN KEY (domicile) REFERENCES team(id),
    FOREIGN KEY (exterieur) REFERENCES team(id)
);

CREATE TABLE IF NOT EXISTS event
(
    id SERIAL PRIMARY KEY,
    code INT NOT NULL,
    ts TIMESTAMP,
    minute_number INT,
    match_minute INT,
    team INT,
    player INT,
    offending_player INT,
    victim_player INT,
    out_player INT,
    in_player INT,
    detail TEXT,
    match INT,
    FOREIGN KEY (team) REFERENCES team(id),
    FOREIGN KEY (player) REFERENCES player(id),
    FOREIGN KEY (offending_player) REFERENCES player(id),
    FOREIGN KEY (victim_player) REFERENCES player(id),
    FOREIGN KEY (out_player) REFERENCES player(id),
    FOREIGN KEY (in_player) REFERENCES player(id),
    FOREIGN KEY (match) REFERENCES match(id)
);
