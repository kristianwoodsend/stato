
from .match import match_player_ids
from .util import *
from .db import connect, select, select_one_column


def _get_source_id(source):
    return _get_rowid("source", ("name", str(source)))


def _get_sport_id(sport):
    return _get_rowid("sport", ("name", str(sport)))


def _get_slate_id(sport, name):
    return _get_rowid("slate", ("sport_id", _get_sport_id(sport)), ("name", name))


def _get_rowid(table, *keys):
    try:
        return select_one_column(
            "select rowid from {table} where {key}".format(
                table=table,
                key=' and '.join(["{}=?".format(key) for key, _ in keys])
            ),
            tuple(value for _, value in keys)
        )[0]
    except Exception as e:
        print e
        raise Exception("{} row not found for {}".format(
            table,
            '-'.join([str(value) for _, value in keys]))
        )


def create_slate(sport, name, players):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO slate
            SELECT rowid, ? FROM sport WHERE name = ?
            """, (str(name), sport)
        )
        slate_id = cursor.lastrowid

        for player in players:
            cursor.execute(
                """
                INSERT INTO slate_player VALUES (?, ?, ?, ?, ?)
                """,
                (slate_id, player.name, player.team_code, player.position, player.salary)
            )

    return slate_id


def list_slates(sport):
    return select_one_column("select name from slate where sport_id=?;", (_get_sport_id(sport),))


def create_slate_projections(sport, name, source, projections):
    with connect() as conn:
        cursor = conn.cursor()

        source_id = _get_source_id(source)
        slate_players = get_slate_players(sport, name)
        players = match_player_ids(slate_players, projections)

        for player in players:
            cursor.execute(
                """
                INSERT INTO slate_player_projection VALUES (?, ?, ?, datetime('now'))
                """,
                (player.id, source_id, player.fp)
            )

    return len(players)


def get_slate_players(sport, name):
    slate_id = _get_slate_id(sport, str(name))
    players = select(
        """
        select
            p.rowid, p.name, p.position, p.team_code, p.salary, round(avg(lp.projected_score), 2)
        from
            slate_player p
            left join latest_slate_player_projection lp on lp.player_id = p.rowid
        where
            slate_id = ?
        group by
            p.rowid, p.name, p.position, p.team_code, p.salary
        order by
            p.rowid
        """,
        (slate_id,)
    )

    return [
        Player(row[0], row[1], row[2], row[3], int(row[4]), float(row[5] or 0))
        for row in players
    ]


def get_slate_players_projections(sport, name):
    slate_id = _get_slate_id(sport, str(name))
    players = select(
        """
        select
            p.rowid, p.name, p.position, p.team_code, p.salary, lp.projected_score, s.name
        from
            slate_player p
            join latest_slate_player_projection lp on lp.player_id = p.rowid
            join source s on s.rowid = lp.source_id
        where
            slate_id = ?
        order by
            p.rowid
        """,
        (slate_id,)
    )

    projections = {}
    map(lambda row:
        projections.setdefault(row[6], []).append(
            Player(row[0], row[1], row[2], row[3], int(row[4]), float(row[5] or 0))
        ),
        players)
    return projections


def list_sources(sport):
    return select("select * from source where sport_id=?;", (_get_sport_id(sport),))
