import base64
import re
import json
from time import sleep
from github import Github
from github.GithubException import UnknownObjectException
from itertools import cycle, islice
from datetime import datetime, timedelta

from src.config.config import CONFIG


def datetime2str(dt: datetime, time=False):
    return dt.strftime("%Y-%m-%d_%H-%M-%S") if time else dt.strftime("%Y-%m-%d")


# 30 search requests / minute
# https://docs.github.com/en/rest/reference/search
G_LIST = cycle([Github(token) for token in CONFIG["github"]["tokens"].values()])
SLEEP_INTERVAL = 2 / len(CONFIG["github"]["tokens"]) + 0.001
QUERY_TEMPLATE = """
{query_name} language:python in:readme in:title in:description stars:>={minimal_stars} created:>={last_time_pushed}
"""


def search_repositories(query: dict, max_results: int):
    g = next(G_LIST)

    last_time_pushed = datetime.now() - timedelta(
        **CONFIG["github"]["update"]["query"]["last_time_pushed_interval"]
    )
    last_time_pushed = datetime2str(last_time_pushed)

    sleep(SLEEP_INTERVAL)
    num_results = 0

    for repo in g.search_repositories(
        query=QUERY_TEMPLATE.format(
            query_name=query["value"],
            minimal_stars=CONFIG["github"]["update"]["query"]["minimal_stars"],
            last_time_pushed=last_time_pushed,
        )
    ):

        yield repo

        g = next(G_LIST)
        sleep(SLEEP_INTERVAL)

        num_results += 1
        if num_results >= max_results:
            return


def parse_github_repo(html_url):
    g = next(G_LIST)

    # https://github.com/ken2576/nelf -> ken2576/nelf
    repo_full_name = "/".join(html_url.rsplit("/")[-2:])

    parsed = dict()
    parsed["author"] = repo_full_name.rsplit("/")[0]
    parsed["files_tree"] = None
    parsed["readme_text"] = None
    parsed["project_page"] = None

    repo = g.get_repo(repo_full_name)
    contents = repo.get_contents("")

    parsed["files_tree"] = []
    for content in islice(contents, 10):
        parsed["files_tree"].append(content.path)

        if content.path.lower() == "readme.md":
            readme_text = base64.b64decode(content.content)
            readme_text = readme_text.decode("utf-8")
            parsed["readme_text"] = readme_text
            project_page = regex_find_project_page(readme_text)
            parsed["project_page"] = project_page

        # sleep(SLEEP_INTERVAL * len(CONFIG['github']['tokens']))

    parsed["files_tree"] = json.dumps(parsed["files_tree"])

    return parsed


def regex_find_project_page(text):
    pattern = "\[project page\]\((?P<url>[^)]+)"
    m = re.search(pattern, text.lower())
    if m is None or "url" not in m.groupdict():
        return None

    slice_project_page_url = slice(m.start(1), m.end(1))
    project_page = text[slice_project_page_url]
    return project_page
