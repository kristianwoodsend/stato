CREATE TABLE sports (
    name VARCHAR(16)
)

CREATE TABLE source (
    sport_id INT,
    name VARCHAR(255),
    code VARCHAR(255),
    parsing_module VARCHAR(255),
    parsing_class VARCHAR(255)
);

CREATE TABLE contest (
    sport_id INT,
    description VARCHAR(255)
);

CREATE TABLE player_projection (
    contest_id INT,
    name TEXT,
    team_code TEXT,
    position TEXT,
    salary INT,
);

CREATE TABLE game_player_projection (
    player_id INTEGER PRIMARY KEY,
    source_id INT,
    projected_score FLOAT
);
