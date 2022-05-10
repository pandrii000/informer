import os
from os.path import exists
from collections import OrderedDict
from datetime import datetime
import logging

from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    TextField,
    IntegerField,
    BooleanField,
    ForeignKeyField,
    FloatField,
    DateTimeField,
    fn,
)

from src.config.config import PROJECT_PATH, DB_PATH, CONFIG


# logging.basicConfig(filename=PROJECT_PATH / 'log.log', level=logging.INFO)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


database = SqliteDatabase(DB_PATH, pragmas={"foreign_keys": 1})


# ====== MODELS ======


class BaseModel(Model):
    class Meta:
        database = database


class Metainfo(BaseModel):
    id = IntegerField(primary_key=True)
    updating_flag = BooleanField()


class Query(BaseModel):
    id = IntegerField(primary_key=True)
    value = TextField()


class Repository(BaseModel):
    id = IntegerField(primary_key=True)
    name = TextField()
    seen = BooleanField()


class RepositoryFoundByQuery(BaseModel):
    id = IntegerField(primary_key=True)
    id_repository = ForeignKeyField(Repository, "id", on_delete="CASCADE")
    id_query = ForeignKeyField(Query, "id", on_delete="CASCADE")


class RepositoryRequestInfo(BaseModel):
    id = IntegerField(primary_key=True)
    id_repository = ForeignKeyField(Repository, "id", on_delete="CASCADE")
    id_query = ForeignKeyField(Query, "id", on_delete="CASCADE")

    name = TextField()
    html_url = TextField()
    author = TextField()
    size = FloatField()

    request_datetime = DateTimeField()

    description = TextField(null=True)
    homepage = TextField(null=True)
    project_page = TextField(null=True)
    files_tree = TextField(null=True)
    readme_text = TextField(null=True)

    # fields from github API, should not be null
    watchers_count = IntegerField()
    subscribers_count = IntegerField()
    stargazers_count = IntegerField()
    forks_count = IntegerField()
    open_issues_count = IntegerField()
    network_count = IntegerField()
    has_issues = IntegerField()
    created_at = DateTimeField()
    pushed_at = DateTimeField()


# =====================


def initialize_database(insert_default_queries: bool = True):
    if not exists(DB_PATH):
        with database:
            database.create_tables(
                [
                    Metainfo,
                    Query,
                    Repository,
                    RepositoryFoundByQuery,
                    RepositoryRequestInfo,
                ]
            )

        add_default_metainfo()

        if insert_default_queries:
            with open(PROJECT_PATH / "storage" / "queries" / "default.txt") as f:
                queries = [line.strip() for line in f.readlines()]

            for query in queries:
                add_query(query)
    else:
        set_updating_flag(False)


def add_default_metainfo():
    assert not Metainfo.select().exists(), "Default configuration was already set!"
    (Metainfo.insert(updating_flag=False).execute())


def add_repository(name: str, seen: bool):
    Repository.insert(name=name, seen=seen).execute()
    logger.info("Added new Repository to database: %s, seen=%s" % (name, seen))


def add_query(value: str):
    Query.insert(value=value).execute()
    logger.info("Added new Query to database: %s" % value)


def add_repository_request_info(attrs: dict):
    RepositoryRequestInfo.insert(attrs).execute()
    logger.info("Added new RepositoryRequestInfo to database: %s" % attrs)


def add_repository_found_by_query(id_repository: int, id_query: int):
    RepositoryFoundByQuery.insert(
        id_repository=id_repository, id_query=id_query
    ).execute()
    logger.info(
        "Added new RepositoryFoundByQuery to database: id_repository=%s, id_query=%s"
        % (id_repository, id_query)
    )


def get_all_query():
    r = Query.select()
    return list(r.dicts()) if r.exists() else []


def get_all_repository():
    r = Repository.select()
    return list(r.dicts()) if r.exists() else []


def get_all_repository_request_info():
    r = RepositoryRequestInfo.select()
    return list(r.dicts()) if r.exists() else []


def get_all_repository_found_by_query():
    r = RepositoryFoundByQuery.select()
    return list(r.dicts()) if r.exists() else []


def get_query(id: int = None, value: str = None):
    if id is not None:
        r = Query.select().where(Query.id == id)
    elif name is not None:
        r = Query.select().where(Query.value == value)
    else:
        raise Exception("No information provided for Query search!")

    if r.exists():
        o = list(r.dicts())
        assert len(o) == 1, "Found duplicates: %s" % str(list(r.dicts()))
        return o[0]
    else:
        return None


def get_repository(id: int = None, name: str = None):
    if id is not None:
        r = Repository.select().where(Repository.id == id)
    elif name is not None:
        r = Repository.select().where(Repository.name == name)
    else:
        raise Exception("No information provided for Repository search!")

    if r.exists():
        o = list(r.dicts())
        assert len(o) == 1, "Found duplicates: %s" % str(list(r.dicts()))
        return o[0]
    else:
        return None


def get_repository_request_info(id: int):
    r = RepositoryRequestInfo.select().where(RepositoryRequestInfo.id == id)

    if r.exists():
        o = list(r.dicts())
        assert len(o) == 1, "Found duplicates: %s" % str(list(r.dicts()))
        return o[0]
    else:
        return None


def get_updates():
    unseen = Repository.select(Repository.id).where(Repository.seen == False)

    last_requests = RepositoryRequestInfo.select(
        RepositoryRequestInfo.id_repository,
        fn.MAX(RepositoryRequestInfo.request_datetime),
    ).group_by(RepositoryRequestInfo.id_repository)

    dates = (
        [d["request_datetime"] for d in list(last_requests.dicts())]
        if last_requests.exists()
        else []
    )
    results = RepositoryRequestInfo.select().where(
        RepositoryRequestInfo.id_repository.in_(unseen)
        & RepositoryRequestInfo.request_datetime.in_(dates)
    )

    return list(results.dicts()) if results.exists() else []


def get_queries_for_repository(id_repository: int):
    r = Query.select().where(
        Query.id.in_(
            RepositoryFoundByQuery.select(RepositoryFoundByQuery.id_query).where(
                RepositoryFoundByQuery.id_repository == id_repository
            )
        )
    )
    return list(r.dicts()) if r.exists() else []


def get_repositories_for_query(id_query: int):
    r = Repository.select().where(
        Repository.id.in_(
            RepositoryFoundByQuery.select(RepositoryFoundByQuery.id_repository).where(
                RepositoryFoundByQuery.id_query == id_query
            )
        )
    )
    return list(r.dicts()) if r.exists() else []


def update_repository(property_name, property_value, id: int = None, name: str = None):
    if id is not None:
        Repository.update({property_name: property_value}).where(
            Repository.id == id
        ).execute()
    elif name is not None:
        Repository.update({property_name: property_value}).where(
            Repository.name == name
        ).execute()
    else:
        raise Exception("No information provided for Repository update!")

    logger.info(
        "Updated Repository id=%s, name=%s, %s=%s"
        % (id, name, property_name, property_value)
    )


def delete_repository(id: int = None, name: str = None):
    if id is not None:
        Repository.delete().where(Repository.id == id).execute()
    elif name is not None:
        Repository.delete().where(Repository.name == name).execute()
    else:
        raise Exception("No information provided for Repository delete!")

    logger.info("Deleted Repository id=%s, name=%s" % (id, name))


def delete_query(id: int = None, value: str = None):
    if id is not None:
        Query.delete().where(Query.id == id).execute()
    elif value is not None:
        Query.delete().where(Query.value == value).execute()
    else:
        raise Exception("No information provided for Query delete!")

    logger.info("Deleted Query id=%s, value=%s" % (id, value))


def delete_seen_repository_request_info():
    seen_repositories = Repository.select(Repository.id).where(Repository.seen == True)
    seen_repositories = (
        [d["id"] for d in list(seen_repositories.dicts())]
        if seen_repositories.exists()
        else []
    )

    (
        RepositoryRequestInfo.delete()
        .where(RepositoryRequestInfo.id_repository.in_(seen_repositories))
        .execute()
    )


def delete_old_repository_request_info():
    leave = RepositoryRequestInfo.select(
        RepositoryRequestInfo.id,
        RepositoryRequestInfo.id_repository,
        fn.MIN(RepositoryRequestInfo.request_datetime),
    ).group_by(RepositoryRequestInfo.id_repository)
    leave = [d["id"] for d in list(leave.dicts())] if leave.exists() else []

    (RepositoryRequestInfo.delete().where(RepositoryRequestInfo.id.not_in(leave)))


def has_repository_found_by_query(id_repository: int, id_query: int):
    return (
        RepositoryFoundByQuery.select()
        .where(
            RepositoryFoundByQuery.id_query
            == id_query & RepositoryFoundByQuery.id_repository
            == id_repository
        )
        .exists()
    )


def is_updating():
    return list(Metainfo.select().dicts())[0].get("updating_flag")


def set_updating_flag(state: bool):
    (Metainfo.update({"updating_flag": state}).execute())

    logger.info("Metainfo updating_flag is %s" % state)
