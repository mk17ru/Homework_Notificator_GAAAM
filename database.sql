DROP TABLE IF EXISTS google_sheets_follows;
DROP TABLE IF EXISTS deadline_follows;
DROP TABLE IF EXISTS follows;
DROP TABLE IF EXISTS deadlines;
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS users;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    tgname VARCHAR
);

CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY,
    name VARCHAR
);

CREATE TABLE IF NOT EXISTS deadlines (
    id INTEGER PRIMARY KEY,
    subject_id INTEGER,
    deadline DATE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

CREATE TABLE IF NOT EXISTS follows (
    id INTEGER PRIMARY KEY,
    following_user_id INTEGER,
    type VARCHAR,
    FOREIGN KEY (following_user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS deadline_follows (
    id INTEGER,
    subject_id INTEGER,
    FOREIGN KEY (id) REFERENCES follows(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

CREATE TABLE IF NOT EXISTS google_sheets_follows (
    id INTEGER,
    field VARCHAR,
    description VARCHAR,
    FOREIGN KEY (id) REFERENCES follows(id)
);