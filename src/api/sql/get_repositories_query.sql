SELECT t.* FROM repositories t
WHERE t.id IN (SELECT t1.id_repository FROM repositories_queries t1 WHERE t1.id_query = (?));
