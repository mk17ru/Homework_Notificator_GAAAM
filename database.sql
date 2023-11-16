DROP TABLE IF EXISTS google_sheets_follows cascade;
DROP TABLE IF EXISTS deadline_follows cascade;
DROP TABLE IF EXISTS deadlines1 cascade;
DROP TABLE IF EXISTS subjects cascade;
DROP TABLE IF EXISTS users cascade;
DROP TABLE IF EXISTS activities cascade;

CREATE TABLE IF NOT EXISTS users (
    chat_id INTEGER,
    is_admin BOOL,
    username VARCHAR PRIMARY KEY 
);

CREATE TABLE IF NOT EXISTS subjects (
    id SERIAL NOT NULL PRIMARY KEY,
    name VARCHAR UNIQUE
);

CREATE TABLE IF NOT EXISTS activities (
    id SERIAL NOT NULL PRIMARY KEY,
    subject_id INTEGER,
    name VARCHAR,
    UNIQUE (subject_id, name),
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);



CREATE TABLE IF NOT EXISTS deadlines (
    id SERIAL NOT NULL PRIMARY KEY,
    activity_id INTEGER UNIQUE,
    deadline TIMESTAMP,
    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS deadline_follows (
    id SERIAL NOT NULL PRIMARY KEY,
    following_chat_id INTEGER,
    subject_id INTEGER,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS google_sheets_follows (
    id SERIAL NOT NULL PRIMARY KEY,
    following_chat_id INTEGER,
    cells_range VARCHAR,
    range_hash VARCHAR,
    prev_value VARCHAR,
    table_id VARCHAR
);