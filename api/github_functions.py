import base64
import re
from time import sleep
from github import Github
from github.GithubException import UnknownObjectException
from itertools import cycle
from datetime import datetime, timedelta

from database.constants import GITHUB_API_TOKENS, update_config
from utils.time import datetime2str


g_list = cycle([Github(token) for token in GITHUB_API_TOKENS.values()])
query_template='''
{query_name} language:python in:readme in:title in:description stars:>={minimal_stars} created:>={last_time_pushed}
'''

def search_repositories(query: dict, max_results: int = None):
    # 30 search requests / minute
    # https://docs.github.com/en/rest/reference/search

    g = next(g_list)

    sleep_interval = 2 / len(GITHUB_API_TOKENS) + 0.001
    last_time_pushed = datetime2str(datetime.now() - timedelta(**update_config['last_time_pushed_interval']))

    sleep(sleep_interval)
    num_results = 0

    for repo in g.search_repositories(query=query_template.format(
            query_name=query['value'],
            minimal_stars=update_config['minimal_stars'],
            last_time_pushed=last_time_pushed,
        )):

        yield repo

        g = next(g_list)
        sleep(sleep_interval)

        num_results += 1
        if num_results >= max_results:
            return


def find_project_page_url(text):
    pattern = '\[project page\]\((?P<url>[^)]+)'
    m = re.search(pattern, text.lower())
    if m is None or 'url' not in m.groupdict():
        return None

    slice_project_page_url = slice(m.start(1), m.end(1))
    project_page_url = text[slice_project_page_url]
    return project_page_url


def search_project_page(html_url):
    g = next(g_list)

    # https://github.com/ken2576/nelf -> ken2576/nelf
    repo_full_name = '/'.join(html_url.rsplit('/')[-2:])
    repo = g.get_repo(repo_full_name)
    contents = repo.get_contents("")

    for content in contents:
        if content.path.lower() == 'readme.md':
            text = base64.b64decode(content.content)
            text = text.decode('utf-8')
            project_page_url = find_project_page_url(text)
            return project_page_url

    return None


def get_readme_text(html_url):
    g = next(g_list)

    # https://github.com/ken2576/nelf -> ken2576/nelf
    repo_full_name = '/'.join(html_url.rsplit('/')[-2:])

    try:
        repo = g.get_repo(repo_full_name)
    except UnknownObjectException:
        return None

    contents = repo.get_contents("")

    for content in contents:
        if content.path.lower().split('.')[0] == 'readme':
            text = base64.b64decode(content.content)
            text = text.decode('utf-8')
            return text

    return None
