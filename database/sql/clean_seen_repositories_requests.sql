WITH seen_repositories AS (SELECT t1.id FROM repositories t1 WHERE t1.seen = 1)
	DELETE FROM repositories_requests WHERE id_repository IN seen_repositories;
