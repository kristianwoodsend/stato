create view latest_projection_dates as
select
    player_id,
    source_id,
    max(logged_date) latest_logged_date
from
    slate_player p
    join slate_player_projection pp on pp.player_id = p.rowid
group by
    player_id, source_id;


create view latest_slate_player_projection as
select
    p.*
from
    slate_player_projection p
    join latest_projection_dates lpd on lpd.player_id = p.player_id
        and lpd.source_id = p.source_id
        and lpd.latest_logged_date = p.logged_date;