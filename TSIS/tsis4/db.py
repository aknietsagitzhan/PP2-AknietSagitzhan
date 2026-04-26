import psycopg2


DB_NAME = "tsis4"
DB_USER = "aknietramazan"
DB_HOST = "localhost"
DB_PORT = "5432"


def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        host=DB_HOST,
        port=DB_PORT
    )


def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS game_sessions (
            id SERIAL PRIMARY KEY,
            player_id INTEGER REFERENCES players(id) ON DELETE CASCADE,
            score INTEGER NOT NULL,
            level_reached INTEGER NOT NULL,
            played_at TIMESTAMP DEFAULT NOW()
        );
    """)

    conn.commit()

    # Clean old duplicates so that only the best result remains for each player
    cleanup_duplicates()

    cur.close()
    conn.close()


def cleanup_duplicates():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT player_id, MAX(score) AS best_score
        FROM game_sessions
        GROUP BY player_id;
    """)

    rows = cur.fetchall()

    for player_id, best_score in rows:
        cur.execute("""
            SELECT id, score, level_reached, played_at
            FROM game_sessions
            WHERE player_id = %s AND score = %s
            ORDER BY level_reached DESC, played_at ASC
            LIMIT 1;
        """, (player_id, best_score))

        best_row = cur.fetchone()
        if best_row is None:
            continue

        keep_id = best_row[0]

        cur.execute("""
            DELETE FROM game_sessions
            WHERE player_id = %s AND id <> %s;
        """, (player_id, keep_id))

    conn.commit()
    cur.close()
    conn.close()


def get_or_create_player(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM players WHERE username = %s;", (username,))
    row = cur.fetchone()

    if row:
        player_id = row[0]
    else:
        cur.execute(
            "INSERT INTO players (username) VALUES (%s) RETURNING id;",
            (username,)
        )
        player_id = cur.fetchone()[0]
        conn.commit()

    cur.close()
    conn.close()
    return player_id


def save_result(username, score, level_reached):
    player_id = get_or_create_player(username)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, score, level_reached
        FROM game_sessions
        WHERE player_id = %s
        ORDER BY score DESC, level_reached DESC, played_at ASC
        LIMIT 1;
    """, (player_id,))
    row = cur.fetchone()

    if row is None:
        cur.execute("""
            INSERT INTO game_sessions (player_id, score, level_reached)
            VALUES (%s, %s, %s);
        """, (player_id, score, level_reached))
    else:
        session_id, old_score, old_level = row

        if score > old_score or (score == old_score and level_reached > old_level):
            cur.execute("""
                UPDATE game_sessions
                SET score = %s,
                    level_reached = %s,
                    played_at = NOW()
                WHERE id = %s;
            """, (score, level_reached, session_id))

        cur.execute("""
            DELETE FROM game_sessions
            WHERE player_id = %s AND id <> %s;
        """, (player_id, session_id))

    conn.commit()
    cur.close()
    conn.close()


def get_top_10():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT p.username, g.score, g.level_reached, g.played_at
        FROM game_sessions g
        JOIN players p ON g.player_id = p.id
        ORDER BY g.score DESC, g.level_reached DESC, g.played_at ASC
        LIMIT 10;
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_personal_best(username):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT MAX(g.score)
        FROM game_sessions g
        JOIN players p ON g.player_id = p.id
        WHERE p.username = %s;
    """, (username,))

    row = cur.fetchone()
    cur.close()
    conn.close()

    return row[0] if row and row[0] is not None else 0