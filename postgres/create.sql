CREATE TABLE questions (
        question_id SERIAL NOT NULL, 
        question TEXT NOT NULL, 
        correct_answer TEXT NOT NULL, 
        wrong_answer1 TEXT NOT NULL, 
        wrong_answer2 TEXT NOT NULL, 
        wrong_answer3 TEXT NOT NULL,
        wrong_answer4 TEXT NOT NULL,
        asked BOOLEAN, 
        PRIMARY KEY (question_id)
);

CREATE TABLE quick_questions (
        question_id SERIAL NOT NULL,
        question TEXT NOT NULL,
        asked BOOLEAN,
        PRIMARY KEY (question_id)
);

CREATE TABLE players (
        player_id SERIAL NOT NULL,
        player_name TEXT NOT NULL,
        nickname TEXT,
        score BIGINT,
        is_admin BOOLEAN NOT NULL,
        PRIMARY KEY (player_id),
        UNIQUE (nickname)
);
