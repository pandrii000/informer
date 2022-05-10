from src.api.updates import get_updates
from src.api import database


def create_message(update):
    message = '<b><a href="{}">{}</a></b>'.format(update["html_url"], update["name"])

    if update["description"]:
        message += "\n<b>Description:</b> {}".format(update["description"])

    if update["homepage"]:
        message += "\n<b>Homepage:</b> {}".format(update["homepage"])

    if update["project_page"]:
        message += "\n<b>Project page:</b> {}".format(update["project_page"])

    if update["size"]:
        message += "\n<b>Size:</b> {} MB".format("%.2f" % (update["size"] / 1024))

    # if update['created_at']:
    #     message += '\n<b>Created at:</b> {}'.format(update['created_at'])

    if update["query"]:
        message += "\n<b>Query:</b> {}".format(update["query"])

    return message


def update_query_name(update):
    query_name = [
        q["value"] for q in database.get_queries() if q["id"] == update["id_query"]
    ][0]
    update.update({"query": query_name})


def get_update_messages(max_updates=5):
    updates, num_updates = get_updates(max_updates=max_updates)
    messages = []
    for update in updates:
        update_query_name(update)
        message = create_message(update)
        messages.append(message)
    return messages, num_updates


def get_queries():
    queries = [q["value"] for q in database.get_queries()]
    return queries
