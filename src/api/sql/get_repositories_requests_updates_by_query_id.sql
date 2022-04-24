WITH unseen (id) AS (SELECT t1.id FROM repositories t1 WHERE t1.seen = 0),
     last_requests (id_repository, request_datetime) AS (SELECT t2.id_repository, MAX(t2.request_datetime) FROM repositories_requests t2  WHERE t2.id_query == (?) GROUP BY t2.id_repository)
        SELECT t3.* FROM repositories_requests t3
            WHERE (
                   t3.id_repository IN unseen
                   AND
                   t3.request_datetime IN (SELECT t4.request_datetime FROM last_requests t4)
                   )
