from multiprocessing import Process
from flask import (
    Flask,
    session,
    request,
    render_template,
    redirect,
    url_for,
)

from src.api.updates import get_updates, update_database
from src.api import database
from src.web import utils


app = Flask(__name__)
app.secret_key = "super secret key"


@app.route("/")
def index():
    return render_template("base.html")


@app.route("/updates")
def updates():
    search_query = str(request.args.get("search_query", ""))
    max_updates = int(request.args.get("max_updates", 1))

    session["url"] = url_for("updates")

    if request.args.get("search_query", None) is not None:
        session["url"] = url_for("updates", **request.args)

    updates, num_updates = get_updates(
        max_updates=max_updates,
        mark_as_seen=False,
        search_query=search_query,
    )

    queries = database.get_all_query()
    utils.prepare_updates_for_html(updates)

    return render_template(
        "updates.html",
        updating=database.is_updating(),
        num_updates=num_updates,
        updates=updates,
        queries=queries,
        search_query=search_query,
    )


@app.route("/queries")
def queries():
    session["url"] = url_for("queries")
    queries = database.get_all_query()
    utils.update_queries_results_unseen_count(queries)
    utils.update_queries_results_count(queries)
    return render_template(
        "queries.html", updating=database.is_updating(), queries=queries
    )


@app.route("/repositories")
def repositories():
    session["url"] = url_for("repositories")
    repositories = database.get_all_repository()
    utils.prepare_repositories_for_html(repositories)
    return render_template(
        "repositories.html", updating=database.is_updating(), repositories=repositories
    )


@app.route("/seen", methods=["GET"])
def seen():
    id_repository = int(request.args.get("id_repository", None))
    utils.mark_as_seen(id_repository)
    return redirect(session["url"])


@app.route("/unseen", methods=["GET"])
def unseen():
    id_repository = int(request.args.get("id_repository", None))
    utils.mark_as_unseen(id_repository)
    return redirect(session["url"])


@app.route("/share_and_seen", methods=["GET"])
def share():
    id_request = int(request.args.get("id_request", None))
    id_repository = int(request.args.get("id_repository", None))
    utils.share(id_request)
    utils.mark_as_seen(id_repository)
    return redirect(session["url"])


@app.route("/add_query", methods=["GET"])
def add_query():
    query_name = request.args.get("query_name", None)
    database.add_query(query_name)
    return redirect(session["url"])


@app.route("/remove_query", methods=["GET"])
def remove_query():
    id_query = int(request.args.get("id_query", None))
    database.delete_query(id=id_query)
    return redirect(session["url"])


@app.route("/search_updates", methods=["GET"])
def search_updates():
    search_query = request.args.get("search_query", None)
    return redirect(
        url_for("updates", updating=database.is_updating(), search_query=search_query)
    )


@app.route("/start_updating", methods=["GET"])
def start_updating():
    Process(target=update_database).start()
    return redirect(session["url"])


def serve_web(host, port):
    app.run(host=host, port=port)
