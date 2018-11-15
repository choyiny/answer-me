CREATE TABLE players (
        player_id SERIAL NOT NULL,
        player_name TEXT NOT NULL,
        nickname TEXT,
        score INTEGER NOT NULL,
        PRIMARY KEY (player_id)
);

CREATE TABLE questions (
        question_id SERIAL NOT NULL,
        question TEXT NOT NULL,
        correct_answer TEXT NOT NULL,
        wrong_answer1 TEXT NOT NULL,
        wrong_answer2 TEXT NOT NULL,
        wrong_answer3 TEXT NOT NULL,
        asked BOOLEAN NOT NULL,
        PRIMARY KEY (question_id)
);