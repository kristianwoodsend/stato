DELETE FROM source WHERE sport_id IN (
    SELECT rowid FROM sport WHERE name IN ('UCL', 'EPL')
);

INSERT INTO sport VALUES ('SOC');

INSERT INTO source SELECT rowid, 'FanDuel', 'FD', '', '', ''  FROM sport WHERE name = 'SOC';