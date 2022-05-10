from time import sleep
from tqdm import tqdm
import random
from datetime import datetime
from collections import OrderedDict

from src.config.config import CONFIG

from src.api import database
from src.api.github_functions import search_repositories, parse_github_repo


def datetime2str(dt: datetime, time=False):
    return dt.strftime("%Y-%m-%d_%H-%M-%S") if time else dt.strftime("%Y-%m-%d")


def clean_database():
    database.delete_seen_repository_request_info()
    database.delete_old_repository_request_info()


def update_database():
    database.set_updating_flag(True)
    queries = database.get_all_query()
    random.shuffle(queries)
    for query in tqdm(queries, desc="Queries", total=len(queries)):
        clean_database()
        for repo in tqdm(
            search_repositories(query, CONFIG["github"]["update"]["max_results"]),
            desc=query["value"],
            total=CONFIG["github"]["update"]["max_results"],
        ):

            attrs = dict()

            attrs["request_datetime"] = datetime2str(datetime.now(), time=True)

            attrs["id_query"] = query["id"]

            # github attributes
            attrs["name"] = repo.name
            attrs["description"] = repo.description
            attrs["html_url"] = repo.html_url
            attrs["size"] = repo.size
            attrs["homepage"] = repo.homepage
            attrs["watchers_count"] = repo.watchers_count
            attrs["subscribers_count"] = repo.subscribers_count
            attrs["stargazers_count"] = repo.stargazers_count
            attrs["forks_count"] = repo.forks_count
            attrs["open_issues_count"] = repo.open_issues_count
            attrs["network_count"] = repo.network_count
            attrs["has_issues"] = repo.has_issues
            attrs["created_at"] = repo.created_at
            attrs["pushed_at"] = repo.pushed_at

            repo_in_db = database.get_repository(name=attrs["html_url"])
            if repo_in_db:
                attrs["id_repository"] = database.get_repository(
                    name=attrs["html_url"]
                )["id"]
                if not database.has_repository_found_by_query(
                    attrs["id_repository"], attrs["id_query"]
                ):
                    database.add_repository_found_by_query(
                        attrs["id_repository"], attrs["id_query"]
                    )
                continue

            database.add_repository(name=attrs["html_url"], seen=False)
            attrs["id_repository"] = database.get_repository(name=attrs["html_url"])[
                "id"
            ]

            database.add_repository_found_by_query(
                attrs["id_repository"], attrs["id_query"]
            )

            parsed = parse_github_repo(attrs["html_url"])
            attrs["author"] = parsed["author"]
            attrs["project_page"] = parsed["project_page"]
            attrs["files_tree"] = parsed["files_tree"]
            attrs["readme_text"] = parsed["readme_text"]

            database.add_repository_request_info(attrs)

    database.set_updating_flag(False)


def get_updates(max_updates: int = None, mark_as_seen=True, search_query=None):
    repositories = database.get_updates()
    num_updates = len(repositories)

    repositories = sorted(
        repositories,
        key=lambda r: -(
            r["stargazers_count"]
            + r["subscribers_count"]
            + r["forks_count"]
            + r["open_issues_count"]
            + r["network_count"]
        ),
    )

    if search_query is not None:
        query_id_to_name = {q["id"]: q["value"] for q in database.get_all_query()}
        query_name_to_id = {q["value"]: q["id"] for q in database.get_all_query()}
        possible_query_id = (
            query_name_to_id[search_query] if search_query in query_name_to_id else ""
        )
        searched_repositories = []
        for r in repositories:
            if (
                (search_query.lower() in str(r["name"]).lower())
                or (search_query.lower() in str(r["html_url"]).lower())
                or (search_query.lower() in str(r["description"]).lower())
                or (search_query.lower() in query_id_to_name[r["id_query"]])
                or (
                    search_query.lower()
                    in "".join(
                        [
                            q["value"]
                            for q in database.get_queries_for_repository(
                                r["id_repository"]
                            )
                        ]
                    )
                )
                or (possible_query_id == r["id_query"])
            ):
                searched_repositories.append(r)
        repositories = searched_repositories
        num_updates = len(repositories)

    if max_updates is not None:
        repositories = repositories[:max_updates]

    if mark_as_seen:
        for r in repositories:
            database.update_repository("seen", True, name=r["html_url"])

    return repositories, num_updates


def serve_autoupdate():
    while True:
        update_database()
        sleep(CONFIG["github"]["update"]["interval"])


if __name__ == "__main__":
    print(get_updates(mark_as_seen=False))
