from flask import Flask, session
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for

from src.api.update import get_updates
from src.api.database import get_queries
from src.api.database import get_repositories
from src.api.database import add_query as dadd_query
from src.api.database import remove_query_by_id

from src.web import utils


app = Flask(__name__)
app.secret_key = "super secret key"


@app.route('/')
def index():
    # session['url'] = url_for('/')
    return render_template('base.html')


@app.route("/updates")
def updates():
    search_query = request.args.get('search_query', '')
    max_updates = int(request.args.get('max_updates', 1))

    session['url'] = url_for('updates')
    if request.args.get('search_query', None) is not None:
        session['url'] = url_for('updates', **request.args)

    updates, num_updates = get_updates(max_updates=max_updates, mark_as_seen=False, search_query=search_query)
    queries = get_queries()
    utils.prepare_updates_for_html(updates)
    return render_template('updates.html',
            num_updates=num_updates,
            updates=updates,
            queries=queries,
            search_query=search_query)


@app.route("/queries")
def queries():
    session['url'] = url_for('queries')
    queries = get_queries()
    utils.queries_results_unseen_count(queries)
    utils.queries_results_count(queries)
    return render_template('queries.html', queries=queries)


@app.route("/repositories")
def repositories():
    session['url'] = url_for('repositories')
    repositories = get_repositories()
    utils.prepare_repositories_for_html(repositories)
    return render_template('repositories.html', repositories=repositories)


@app.route('/seen', methods=['GET'])
def seen():
    id_repository = int(request.args.get('id_repository', None))
    utils.seen(id_repository)
    return redirect(session['url'])


@app.route('/unseen', methods=['GET'])
def unseen():
    id_repository = int(request.args.get('id_repository', None))
    utils.unseen(id_repository)
    return redirect(session['url'])


@app.route('/share_and_seen', methods=['GET'])
def share():
    id_request = int(request.args.get('id_request', None))
    utils.share(id_request)
    id_repository = int(request.args.get('id_repository', None))
    utils.seen(id_repository)
    return redirect(session['url'])


@app.route('/add_query', methods=['GET'])
def add_query():
    query_name = request.args.get('query_name', None)
    dadd_query(query_name)
    return redirect(session['url'])


@app.route('/remove_query', methods=['GET'])
def remove_query():
    id_query = int(request.args.get('id_query', None))
    remove_query_by_id(id_query)
    return redirect(session['url'])


@app.route('/search_updates', methods=['GET'])
def search_updates():
    search_query = request.args.get('search_query', None)
    return redirect(url_for('updates', search_query=search_query))


def serve_web(host, port):
    app.run(host=host, port=port)
