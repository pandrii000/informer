from os.path import exists
from sqlite3 import connect
from collections import OrderedDict
from datetime import datetime

from database.constants import PROJECT_PATH, DB_PATH, SQL_PATH


def initialize_database():
    if not exists(DB_PATH):
        create_database()
        initialize_database_insert_queries()


def create_database():
    with open(SQL_PATH + 'create_table_queries.sql') as f:
        _create_table_queries = f.read()

    with open(SQL_PATH + 'create_table_repositories.sql') as f:
        _create_table_repositories = f.read()

    with open(SQL_PATH + 'create_table_repositories_requests.sql') as f:
        _create_table_repositories_requests = f.read()

    con = connect(DB_PATH)
    cur = con.cursor()
    cur.execute(_create_table_queries)
    con.commit()
    cur.execute(_create_table_repositories)
    con.commit()
    cur.execute(_create_table_repositories_requests)
    con.commit()
    con.close()


def add_query(query: str):
    with open(SQL_PATH + 'add_query.sql') as f:
        _add_query = f.read()

    con = connect(DB_PATH)
    cur = con.cursor()
    cur.execute(_add_query, [query])
    con.commit()
    con.close()


def get_query_id(query: str):
    with open(SQL_PATH + 'get_query_id.sql') as f:
        _get_query_id = f.read()

    con = connect(DB_PATH)
    cur = con.cursor()
    cur.execute(_get_query_id, [query])
    query_id = cur.fetchone()
    con.close()

    if query_id is None:
        return None
    else:
        return query_id[0]


def remove_query(query: str):
    with open(SQL_PATH + 'remove_query.sql') as f:
        _remove_query = f.read()

    con = connect(DB_PATH)
    cur = con.cursor()
    query_id = get_query_id(query)
    cur.execute(_remove_query, [query_id])
    con.commit()
    con.close()


def clean_seen_repositories_requests():
    with open(SQL_PATH + 'clean_seen_repositories_requests.sql') as f:
        _clean_seen_repositories_requests = f.read()

    con = connect(DB_PATH)
    cur = con.cursor()
    cur.execute(_clean_seen_repositories_requests)
    con.commit()
    con.close()


def get_queries():
    with open(SQL_PATH + 'get_queries.sql') as f:
        _get_queries = f.read()

    columns = ['id', 'value']

    con = connect(DB_PATH)
    cur = con.cursor()
    cur.execute(_get_queries)
    queries = cur.fetchall()
    con.commit()
    con.close()

    return list(map(lambda values: dict(zip(columns, values)), queries))


# def test_query():
#     initialize_database()
#     add_query('neural network')
#     print(get_query_id('neural network'))
#     # remove_query('neural network')
#     print(get_queries())


def add_repository(name: str, seen: bool):
    with open(SQL_PATH + 'add_repository.sql') as f:
        _add_repository = f.read()

    con = connect(DB_PATH)
    cur = con.cursor()
    cur.execute(_add_repository, [name, seen])
    con.commit()
    con.close()


def get_repository_id(name: str):
    with open(SQL_PATH + 'get_repository_id.sql') as f:
        _get_repository_id = f.read()

    con = connect(DB_PATH)
    cur = con.cursor()
    cur.execute(_get_repository_id, [name])
    repository_id = cur.fetchone()
    con.close()

    if repository_id is None:
        return None
    else:
        return repository_id[0]


def get_repository_by_id(id_repository: int):
    with open(SQL_PATH + 'get_repository_by_id.sql') as f:
        _get_repository_by_id = f.read()

    columns = ['id', 'name', 'seen']

    con = connect(DB_PATH)
    cur = con.cursor()
    cur.execute(_get_repository_by_id, [id_repository])
    repository = cur.fetchone()
    con.close()

    if repository is None:
        return None
    else:
        return dict(zip(columns, repository))


def update_repository_property(name: str, property_name, property_value):
    with open(SQL_PATH + 'update_repository_property.sql') as f:
        _update_repository_property = f.read()

    con = connect(DB_PATH)
    cur = con.cursor()
    repository_id = get_repository_id(name)
    cur.execute(_update_repository_property.format(property_name), [property_value, repository_id])
    con.commit()
    con.close()


def update_repository_property_by_id(repository_id: str, property_name, property_value):
    with open(SQL_PATH + 'update_repository_property.sql') as f:
        _update_repository_property = f.read()

    con = connect(DB_PATH)
    cur = con.cursor()
    cur.execute(_update_repository_property.format(property_name), [property_value, repository_id])
    con.commit()
    con.close()


def get_repositories():
    with open(SQL_PATH + 'get_repositories.sql') as f:
        _get_repositories = f.read()

    columns = ['id', 'name', 'seen']

    con = connect(DB_PATH)
    cur = con.cursor()
    cur.execute(_get_repositories)
    repositories = cur.fetchall()
    con.commit()
    con.close()

    return list(map(lambda values: dict(zip(columns, values)), repositories))


def remove_repository(name: str):
    with open(SQL_PATH + 'remove_repository.sql') as f:
        _remove_repository = f.read()

    con = connect(DB_PATH)
    cur = con.cursor()
    repository_id = get_repository_id(name)
    cur.execute(_remove_repository, [repository_id])
    con.commit()
    con.close()


# def test_repository():
#     initialize_database()
#     add_repository('asd/jfks-dfs', False)
#     print(get_repository_id('asd/jfks-dfs'))
#     update_repository_property('asd/jfks-dfs', 'seen', True)
#     print(get_repositories())
#     remove_repository('asd/jfks-dfs')


def add_repositories_requests(attrs: dict):
    with open(SQL_PATH + 'add_repositories_requests.sql') as f:
        _add_repositories_requests = f.read()

    con = connect(DB_PATH)
    cur = con.cursor()
    cur.execute(_add_repositories_requests, list(attrs.values()))
    con.commit()
    con.close()


def get_repositories_requests():
    with open(SQL_PATH + 'get_repositories_requests.sql') as f:
        _get_repositories_requests = f.read()

    columns = ['id', 'id_repository', 'id_query', 'name', 'description', 'html_url', 'size', 'homepage',
    'watchers_count', 'subscribers_count', 'stargazers_count', 'forks_count', 'open_issues_count',
    'network_count', 'has_issues', 'created_at', 'pushed_at', 'project_page', 'request_datetime']

    con = connect(DB_PATH)
    cur = con.cursor()
    cur.execute(_get_repositories_requests)
    repositories = cur.fetchall()
    con.commit()
    con.close()

    return list(map(lambda values: dict(zip(columns, values)), repositories))

def get_repositories_requests_updates():
    with open(SQL_PATH + 'get_repositories_requests_updates.sql') as f:
        _get_repositories_requests_updates = f.read()

    columns = ['id', 'id_repository', 'id_query', 'name', 'description', 'html_url', 'size', 'homepage',
    'watchers_count', 'subscribers_count', 'stargazers_count', 'forks_count', 'open_issues_count',
    'network_count', 'has_issues', 'created_at', 'pushed_at', 'project_page', 'request_datetime']

    con = connect(DB_PATH)
    cur = con.cursor()
    cur.execute(_get_repositories_requests_updates)
    repositories = cur.fetchall()
    con.commit()
    con.close()

    return list(map(lambda values: dict(zip(columns, values)), repositories))


def get_repository_request_by_id(id_request: int):
    with open(SQL_PATH + 'get_repository_request_by_id.sql') as f:
        _get_repository_request_by_id = f.read()

    columns = ['id', 'id_repository', 'id_query', 'name', 'description', 'html_url', 'size', 'homepage',
    'watchers_count', 'subscribers_count', 'stargazers_count', 'forks_count', 'open_issues_count',
    'network_count', 'has_issues', 'created_at', 'pushed_at', 'project_page', 'request_datetime']

    con = connect(DB_PATH)
    cur = con.cursor()
    cur.execute(_get_repository_request_by_id, [id_request])
    request = cur.fetchone()
    if request is not None:
        request = dict(zip(columns, request))
    con.commit()
    con.close()

    return request


def test_repositories_requests():
    initialize_database()
    add_repositories_requests(OrderedDict({
        'id_repository': 1,
        'id_query': 2,
        'name': 'some name',
        'description': 'some description',
        'html_url': 'some html_url',
        'size': 24.3,
        'homepage': 'some homepage',
        'watchers_count': 2,
        'subscribers_count': 4,
        'stargazers_count': 2,
        'forks_count': 2,
        'open_issues_count': 2,
        'network_count': 2,
        'has_issues': 2,
        'created_at': '2020-10-10 20:20:20',
        'pushed_at': '2021-11-11 23:23:23',
    }))
    # print(get_repository_id('asd/jfks-dfs'))
    # remove_repository('asd/jfks-dfs')


def get_repositories_requests_info_by_repository_id(id_repository: int):
    repositories_requests = [r for r in get_repositories_requests() if r['id_repository'] == id_repository]
    repositories_requests_info = max(repositories_requests,
            key=lambda r: datetime.strptime(r['request_datetime'], '%Y-%m-%d_%H-%M-%S').timestamp())
    return repositories_requests_info


def initialize_test_database():
    initialize_database()
    add_query('Image Recognition')
    print(get_queries())


def initialize_database_insert_queries():
    with open(PROJECT_PATH + 'database/queries_default.txt') as f:
        for line in f.readlines():
            line = line.strip()
            add_query(line)


if __name__ == '__main__':
    # test_query()
    # test_repository()
    # test_repository_request()
    # print(get_repositories_requests())

    # print(get_repositories_requests_updates())
    # print(get_repository_request_by_id(12000))
    print(get_repository_by_id(60))

    # initialize_database()
    # insert_queries()
    # update_repository_property('https://github.com/tatarenstas/ImageAI-Objects-Detection', 'seen', True)

    pass
