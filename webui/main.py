from wsgiref.simple_server import make_server
from urllib.parse import urlparse, parse_qs
import telegram
import markdown
from bs4 import BeautifulSoup

from api.update import get_updates
from database.constants import PROJECT_PATH, FORWARD_CHAT_ID
from database import functions as database
from api.github_functions import get_readme_text

from bot.functions import get_updater
from bot.utils import create_message


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


with open(PROJECT_PATH + 'webui/styles.css') as f:
    STYLE = f.read()

# COLUMNS = ['id', 'id_repository', 'id_query', 'name', 'description', 'html_url', 'size', 'homepage',
#       'watchers_count', 'subscribers_count', 'stargazers_count', 'forks_count', 'open_issues_count',
#       'network_count', 'has_issues', 'created_at', 'pushed_at', 'project_page', 'request_datetime']
COLUMNS = ['name', 'description', 'html_url', 'query', 'size', 'homepage', 'project_page',
      'watchers_count', 'subscribers_count', 'stargazers_count', 'forks_count', 'open_issues_count',
      'network_count', 'has_issues', 'created_at', 'pushed_at', 'request_datetime']


def share(id_request):
    updater = get_updater()
    update = database.get_repository_request_by_id(id_request)
    update_query_name(update)
    message = create_message(update)
    updater.bot.sendMessage(chat_id=FORWARD_CHAT_ID, text=message, parse_mode=telegram.ParseMode.HTML)


def update_query_name(update):
    query_name = [q['value'] for q in database.get_queries() if q['id'] == update['id_query']][0]
    update.update({'query': query_name})


def format_update(update):
    update['name'] = "<a href={}><h2 style='text-align: center'>{}</h2></a>".format(update['html_url'], update['name'])
    update['size'] = '{} MB'.format('%.2f' % (update['size'] / 1024))


def updates_to_html(updates, num_updates):
    html = '<h1>Updates</h1>'
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

    else:
        updates, num_updates = get_updates(max_updates=1, mark_as_seen=False)
        html = updates_to_html(updates, num_updates)
        response_body = HTML.format(body=html, style=STYLE).encode()
        status = '200 OK'
        headers = [('Content-type', 'text/html'),
                   ('Content-Length', str(len(response_body)))]
        start_response(status, headers)
        return [response_body]


def serve_web(ip, port):
    """Start the server."""
    httpd = make_server(ip, port, app_updates)
    httpd.serve_forever()


if __name__ == "__main__":
    serve_web('0.0.0.0', 8050)
