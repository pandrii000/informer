CREATE TABLE repositories_queries (
    id INTEGER PRIMARY KEY,
    id_repository INTEGER,
    id_query INTEGER,
    FOREIGN KEY(id_repository) REFERENCES repositories(id),
    FOREIGN KEY(id_query) REFERENCES queries(id)
);
