CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matricule TEXT UNIQUE NOT NULL,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    fonction TEXT,
    nationalite TEXT,
    email TEXT,
    telephone TEXT
);

CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    nom_fichier TEXT NOT NULL,
    type_document TEXT NOT NULL,
    date_depot TEXT,
    date_expiration TEXT,
    FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

CREATE TABLE qualifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    type_aeronef TEXT NOT NULL,
    date_obtention TEXT,
    date_expiration TEXT,
    FOREIGN KEY(employee_id) REFERENCES employees(id) ON DELETE CASCADE
);
