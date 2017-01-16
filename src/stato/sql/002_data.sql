INSERT INTO sport VALUES
    ('NFL'), ('NBA'), ('NHL'), ('MLB'), ('UCL'), ('EPL');

INSERT INTO source
SELECT rowid, 'FanDuel', 'FD', '', '', ''  FROM sport;

INSERT INTO source
select
	s.rowid, d.*
from
	sport s,
	(
		SELECT 'NumberFire', 'NF', 'stato.scrapers', 'number_fire', 'get_nfl_data'
		UNION SELECT 'RotoGrinders', 'RG', 'stato.scrapers', 'roto_grinders', 'get_nfl_data'
		UNION SELECT 'RotoWire', 'RW', 'stato.scrapers', 'roto_wire', 'get_nfl_data'
		UNION SELECT 'DFCafe', 'DFC', 'stato.scrapers', 'daily_fantasy_cafe', 'get_nfl_data'
	) d
WHERE s.name = 'NFL';