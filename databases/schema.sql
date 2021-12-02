CREATE TABLE IF NOT EXISTS boxes (
    name TEXT PRIMARY KEY,
    color TEXT NOT NULL,
    author TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS things (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thing TEXT NOT NULL,
    amount TEXT NOT NULL,
    box TEXT NOT NULL
);