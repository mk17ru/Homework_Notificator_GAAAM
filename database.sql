DROP TABLE IF EXISTS google_sheets_follows cascade;
DROP TABLE IF EXISTS deadline_follows cascade;
DROP TABLE IF EXISTS follows cascade;
DROP TABLE IF EXISTS deadlines cascade;
DROP TABLE IF EXISTS subjects cascade;
DROP TABLE IF EXISTS users cascade;
DROP TABLE IF EXISTS activities cascade;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL NOT NULL PRIMARY KEY,
    tgname VARCHAR
);

CREATE TABLE IF NOT EXISTS subjects (
    id SERIAL NOT NULL PRIMARY KEY,
    name VARCHAR
);

CREATE TABLE IF NOT EXISTS activities (
    id SERIAL NOT NULL PRIMARY KEY,
    subject_id INTEGER,
    name VARCHAR,
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

CREATE TABLE IF NOT EXISTS deadlines (
    id SERIAL NOT NULL PRIMARY KEY,
    activity_id INTEGER,
    deadline DATE,
    FOREIGN KEY (activity_id) REFERENCES activities(id)
);

CREATE TABLE IF NOT EXISTS follows (
    id SERIAL NOT NULL PRIMARY KEY,
    following_user_id INTEGER,
    type VARCHAR,
    FOREIGN KEY (following_user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS deadline_follows (
    id SERIAL NOT NULL,
    subject_id INTEGER,
    FOREIGN KEY (id) REFERENCES follows(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

CREATE TABLE IF NOT EXISTS google_sheets_follows (
    id SERIAL NOT NULL,
    field VARCHAR,
    description VARCHAR,
    FOREIGN KEY (id) REFERENCES follows(id)
);