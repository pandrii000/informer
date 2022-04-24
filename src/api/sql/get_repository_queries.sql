SELECT t.* FROM queries t
WHERE t.id IN (SELECT t1.id_query FROM repositories_queries t1 WHERE t1.id_repository = (?));
