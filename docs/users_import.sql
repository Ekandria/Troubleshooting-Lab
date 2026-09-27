 sqlite app.db                    

sqlite> CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
);

sqlite> INSERT INTO users (name, email)
VALUES ('Tony', 'tony@example.com'), ('Mary', 'mary@example.com'), ('Charlotte', 'charlotte@example.com'), ('Andrew', 'andrew@example.com'), ('Gus', 'gus@example.com'), ('Stefanie', 'stefanie@example.com'), ('Penelope', 'penelope@example.com');
sqlite> SELECT * FROM users;
