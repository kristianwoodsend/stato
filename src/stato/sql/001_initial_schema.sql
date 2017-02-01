CREATE TABLE sport (
    name VARCHAR(16)
);

CREATE TABLE source (
    sport_id INT,
    name VARCHAR(255),
    code VARCHAR(255),
    parsing_package VARCHAR(255),
    parsing_module VARCHAR(255),
    parsing_method VARCHAR(255)
);

CREATE TABLE slate (
    sport_id INT,
    name VARCHAR(255)
);

CREATE TABLE slate_player (
    slate_id INT,
    name TEXT,
    team_code TEXT,
    position TEXT,
    salary INT
);

CREATE TABLE slate_player_projection (
    player_id INT,
    source_id INT,
    projected_score FLOAT,
    logged_date DATETIME
);
