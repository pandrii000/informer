import telegram
import markdown
import json

from src.config.config import CONFIG
from src.api import database
from src.bot.functions import get_updater
from src.bot.utils import create_message


def prepare_updates_for_html(updates):
    for update in updates:
        # author
        update["author_url"] = f"https://github.com/{update['author']}"

        # queries
        queries = " + ".join(
            [
                q["value"]
                for q in database.get_queries_for_repository(update["id_repository"])
            ]
        )
        update.update({"queries": queries})

        # size
        update["size"] = "{} MB".format("%.2f" % (update["size"] / 1024))

        # readme
        if update["readme_text"] is None:
            del update["readme_text"]
        else:
            update["readme_text"] = markdown.markdown(update["readme_text"])

        # project page
        if update["project_page"] is None or len(update["project_page"]) == 0:
            del update["project_page"]

        # homepage
        if update["homepage"] is None or len(update["homepage"]) == 0:
            del update["homepage"]

        # files_tree
        if update["files_tree"] is None:
            del update["project_page"]
        else:
            update["files_tree"] = json.loads(str(update["files_tree"]))


def prepare_repositories_for_html(repositories):
    for repository in repositories:
        repository["seen"] = "True" if repository["seen"] else "False"


def mark_as_seen(id_repository):
    database.update_repository("seen", True, id=id_repository)


def mark_as_unseen(id_repository):
    database.update_repository("seen", False, id=id_repository)


def share(id_request):
    updater = get_updater()
    update = database.get_repository_request_info(id_request)
    update_query_name(update)
    message = create_message(update)
    updater.bot.sendMessage(
        chat_id=CONFIG["telegram"]["chat_to_forward"],
        text=message,
        parse_mode=telegram.ParseMode.HTML,
    )


def update_queries_results_unseen_count(queries):
    updates = database.get_updates()
    for query in queries:
        results_unseen_count = sum([u["id_query"] == query["id"] for u in updates])
        query["results_unseen_count"] = results_unseen_count


def update_queries_results_count(queries):
    for query in queries:
        results_count = len(database.get_repositories_for_query(query["id"]))
        query["results_count"] = results_count


def update_query_name(update):
    if database.get_query(id=update["id_query"]):
        query_name = database.get_query(id=update["id_query"])["value"]
    else:
        query_name = ""
    update.update({"query": query_name})
