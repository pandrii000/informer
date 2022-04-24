WITH leave (id, id_repository, request_datetime) AS (
	SELECT t.id, t.id_repository, MIN(t.request_datetime) FROM repositories_requests t
	GROUP BY t.id_repository
	)
	DELETE FROM repositories_requests WHERE id NOT IN (SELECT ttt.id FROM leave ttt);
