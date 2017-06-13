INSERT INTO source
select
	s.rowid, d.*
from
	sport s,
	(
		SELECT 'NumberFire', 'NF', 'stato.scrapers', 'number_fire', 'get_mlb_data'
		UNION SELECT 'RotoGrinders', 'RG', 'stato.scrapers', 'roto_grinders', 'get_mlb_data'
		UNION SELECT 'RotoWire', 'RW', 'stato.scrapers', 'roto_wire', 'get_mlb_data'
		UNION SELECT 'DFCafe', 'DFC', 'stato.scrapers', 'daily_fantasy_cafe', 'get_mlb_data'
	) d
WHERE s.name = 'MLB';