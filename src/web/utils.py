import telegram
import markdown
from urllib.parse import parse_qs
from bs4 import BeautifulSoup

from src.api import database
from src.api.update import get_updates
from src.config.config import PROJECT_PATH
from src.config.config import CONFIG
from src.api.github_functions import get_readme_text
from src.api.github_functions import get_tree

from src.bot.functions import get_updater
from src.bot.utils import create_message


def prepare_update_for_html(update):
    # queries
    queries = ' + '.join([q['value'] for q in database.get_repository_queries(update['id_repository'])])
    update.update({'queries': queries})

    # size
    update['size'] = '{} MB'.format('%.2f' % (update['size'] / 1024))

    # readme
    readme_text = get_readme_text(update['html_url'])
    if readme_text is not None:
        readme_text = ''.join(BeautifulSoup(markdown.markdown(readme_text)).findAll(text=True))[:1000]
        update['readme_text'] = readme_text
    else:
        update['readme_text'] = 'None'

    # files tree
    files_tree = get_tree(update['html_url'])
    update['files_tree'] = files_tree if files_tree else []

    if update['project_page'] is None:
        del update['project_page']

    if update['homepage'] is None:
        del update['homepage']


def prepare_updates_for_html(updates):
    for update in updates:
        prepare_update_for_html(update)


def prepare_repository_for_html(repository):
    repository['seen'] = 'True' if repository['seen'] else 'False'


def prepare_repositories_for_html(repositories):
    for repository in repositories:
        prepare_repository_for_html(repository)


def seen(id_repository):
    database.update_repository_property_by_id(id_repository, 'seen', True)


def unseen(id_repository):
    database.update_repository_property_by_id(id_repository, 'seen', False)


def share(id_request):
    updater = get_updater()
    update = database.get_repository_request_by_id(id_request)
    update_query_name(update)
    message = create_message(update)
    updater.bot.sendMessage(chat_id=CONFIG['telegram']['chat_to_forward'],
            text=message, parse_mode=telegram.ParseMode.HTML)


def query_results_unseen_count(query, updates):
    results_unseen_count = sum([u['id_query'] == query['id'] for u in updates])
    query['results_unseen_count'] = results_unseen_count


def queries_results_unseen_count(queries):
    updates = database.get_repositories_requests_updates()
    for query in queries:
        query_results_unseen_count(query, updates)


def query_results_count(query):
    results_count = len(database.get_repositories_query(query['id']))
    query['results_count'] = results_count


def queries_results_count(queries):
    for query in queries:
        query_results_count(query)


HTML = '''
<!DOCTYPE HTML>
<html>
    <head>
        <title>Home</title>
        <meta charset="utf-8">
        <style>{style}</style>
    </head>
    <body>
        {body}
    </body>
</html>
'''


with open(PROJECT_PATH / 'src' / 'web' / 'static' / 'style.css') as f:
    STYLE = f.read()

# COLUMNS = ['id', 'id_repository', 'id_query', 'name', 'description', 'html_url', 'size', 'homepage',
#       'watchers_count', 'subscribers_count', 'stargazers_count', 'forks_count', 'open_issues_count',
#       'network_count', 'has_issues', 'created_at', 'pushed_at', 'project_page', 'request_datetime']
COLUMNS = ['name', 'description', 'html_url', 'query', 'size', 'homepage', 'project_page',
      'watchers_count', 'subscribers_count', 'stargazers_count', 'forks_count', 'open_issues_count',
      'network_count', 'has_issues', 'created_at', 'pushed_at', 'request_datetime']




def update_query_name(update):
    query_name = [q['value'] for q in database.get_queries() if q['id'] == update['id_query']]
    if len(query_name) > 0:
        # query_name = query_name[0]
        query_name = ' + '.join([q['value'] for q in
            database.get_repository_queries(update['id_repository'])])
    else:
        query_name = ''
    update.update({'query': query_name})


def format_update(update):
    update['name'] = "<a href={}><h2 style='text-align: center'>{}</h2></a>".format(update['html_url'], update['name'])
    update['size'] = '{} MB'.format('%.2f' % (update['size'] / 1024))


def generate_query_filter():
    html = '''
    <form action='query_filter' method='get'>
        <select name="id_queries">'''

    html += '<option selected value=""></option>'
    for q in database.get_queries():
        html += '<option value="{}">{}</option>'.format(q['id'], q['value'])

    html += '''
        </select>
       <input type="submit">
    </form>'''
    return html


def updates_to_html(updates, num_updates):
    html = ''
    html += generate_query_filter()
    html += '<h1>Updates</h1>'
    html += '<br>'
    html += '<h2>Total: {}</h2>'.format(num_updates)

    for update in updates:
        update_query_name(update)
        format_update(update)

        update_html = ''

        update_html += update['name'] + '<br>'
        if update['description']:
            update_html += '<b>Description:</b> ' + str(update['description']) + '<br>'
        update_html += '<b>Size:</b> ' + update['size'] + '<br>'
        update_html += '<b>Query:</b> ' + update['query'] + '<br>'

        update_html += "<p>"
        update_html += "<table style='width: 100%'>"
        row1 = ['watchers_count', 'subscribers_count', 'stargazers_count', 'forks_count', 'open_issues_count', 'network_count']
        row2 = [update[c] for c in row1]
        update_html += "<tr>"
        for c in range(len(row1)):
            update_html += "<td>"
            update_html += row1[c]
            update_html += "</td>"
        update_html += "</tr>"
        update_html += "<tr>"
        for c in range(len(row1)):
            update_html += "<td>"
            update_html += str(row2[c])
            update_html += "</td>"
        update_html += "</tr>"
        update_html += "</table>"
        update_html += "</p>"

        if update['project_page']:
            project_page_href = "<a href={}>{}</a>".format(update['project_page'], update['project_page'])
            update_html += "<b>Project Page:</b> " + project_page_href + '<br>'

        update_html += "<table>"
        update_html += "<tr>"

        update_html += "<td>"

        update_html += "<p>"
        update_html += "<form action='seen' method='post'>"
        update_html += "<input type='hidden' name='id_repository' value='{}'>".format(update['id_repository'])
        update_html += "<input type='hidden' name='id_request' value='{}'>".format(update['id'])
        update_html += "<input type='submit' value='Seen'>"
        update_html += '</form>'
        update_html += "</p>"

        update_html += "</td>"
        update_html += "<td>"

        update_html += "<p>"
        update_html += "<form action='share' method='post'>"
        update_html += "<input type='hidden' name='id_repository' value='{}'>".format(update['id_repository'])
        update_html += "<input type='hidden' name='id_request' value='{}'>".format(update['id'])
        update_html += "<input type='submit' value='Share & Seen'>"
        update_html += '</form>'
        update_html += "</p>"

        update_html += "</td>"

        update_html += "</tr>"
        update_html += "</table>"

        readme_text = get_readme_text(update['html_url'])
        if readme_text is not None:
            readme_text = ''.join(BeautifulSoup(markdown.markdown(readme_text)).findAll(text=True))[:1000]
            update_html += "<div style='font-size: 0.7em'>"
            update_html += readme_text
            update_html += "</div>"

        tree = get_tree(update['html_url'])
        if tree is not None:
            update_html += '<br>'
            update_html += '<b>Content:</b><br>'
            text = '\n'.join(tree)
            update_html += "<div style='font-size: 0.7em'>"
            for el in tree:
                update_html += f'- {el}<br>'
            update_html += "</div>"

        html += '<hr>' + update_html

    return html


def app_updates(environ, start_response):
    path   = environ['PATH_INFO']
    method = environ['REQUEST_METHOD']

    print(path, method)

    if method == 'POST' and path == '/seen':
        request_body_size = int(environ['CONTENT_LENGTH'])
        request_body = environ['wsgi.input'].read(request_body_size).decode()
        request_body_dict = parse_qs(request_body)

        id_repository = int(request_body_dict['id_repository'][0])
        database.update_repository_property_by_id(id_repository, 'seen', True)

        start_response('302 Found', [('Location', '/')])
        return []

    elif method == 'POST' and path == '/share':
        request_body_size = int(environ['CONTENT_LENGTH'])
        request_body = environ['wsgi.input'].read(request_body_size).decode()
        request_body_dict = parse_qs(request_body)

        id_request = int(request_body_dict['id_request'][0])
        share(id_request)

        print('Shared', id_request)

        id_repository = int(request_body_dict['id_repository'][0])
        database.update_repository_property_by_id(id_repository, 'seen', True)

        start_response('302 Found', [('Location', '/')])
        return []

    elif method == 'GET' and path == '/query_filter':
        # print(*sorted(environ.items()), sep='\n')
        request_body_dict = parse_qs(environ['QUERY_STRING'])
        id_queries = [int(request_body_dict['id_queries'][0])]
        updates, num_updates = get_updates(max_updates=1, mark_as_seen=False, filter_queries=id_queries)
        html = updates_to_html(updates, num_updates)
        response_body = HTML.format(body=html, style=STYLE).encode()
        status = '200 OK'
        headers = [('Content-type', 'text/html'),
                   ('Content-Length', str(len(response_body)))]
                   # ('Location', '/query_filter?id_queries={}'.format(','.join(map(str, id_queries))))]
        start_response(status, headers)
        return [response_body]

    else:
        updates, num_updates = get_updates(max_updates=1, mark_as_seen=False)
        html = updates_to_html(updates, num_updates)
        response_body = HTML.format(body=html, style=STYLE).encode()
        status = '200 OK'
        headers = [('Content-type', 'text/html'),
                   ('Content-Length', str(len(response_body)))]
        start_response(status, headers)
        return [response_body]
