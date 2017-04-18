UPDATE
    source
SET
    parsing_package = 'stato.scrapers',
    parsing_module = 'fanduel',
    parsing_method = 'parse_players_csv'
WHERE
    name = 'FanDuel'
    AND sport_id IN (SELECT rowid FROM sport WHERE name != 'SOC');

UPDATE
    source
SET
    parsing_package = 'stato.scrapers',
    parsing_module = 'fanduel',
    parsing_method = 'scrape_uk_soc_players'
WHERE
    name = 'FanDuel'
    and sport_id IN (SELECT rowid FROM sport WHERE name = 'SOC');