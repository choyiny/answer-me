CREATE TABLE players (
        player_id SERIAL NOT NULL,
        player_email TEXT NOT NULL,
        score INTEGER NOT NULL,
        PRIMARY KEY (player_id)
);