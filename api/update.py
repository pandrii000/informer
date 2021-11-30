from tqdm import tqdm
from datetime import datetime
from collections import OrderedDict

from database import functions as database
from api.github_functions import search_repositories, search_project_page
from utils.time import datetime2str


def clean_database():
    database.clean_seen_repositories_requests()


def update_database():
    for query in tqdm(database.get_queries()):
        for repo in search_repositories(query, 100):
            attrs = OrderedDict()

            attrs['id_repository'] = None
            attrs['id_query'] = None
            attrs['name'] = repo.name
            attrs['description'] = repo.description
            attrs['html_url'] = repo.html_url
            attrs['size'] = repo.size
            attrs['homepage'] = repo.homepage
            attrs['watchers_count'] = repo.watchers_count
            attrs['subscribers_count'] = repo.subscribers_count
            attrs['stargazers_count'] = repo.stargazers_count
            attrs['forks_count'] = repo.forks_count
            attrs['open_issues_count'] = repo.open_issues_count
            attrs['network_count'] = repo.network_count
            attrs['has_issues'] = repo.has_issues
            attrs['created_at'] = repo.created_at
            attrs['pushed_at'] = repo.pushed_at
            attrs['project_page'] = None
            attrs['request_datetime'] = None

            attrs['id_query'] = query['id']
            attrs['id_repository'] = database.get_repository_id(attrs['html_url'])

            if attrs['id_repository'] is None:
                database.add_repository(attrs['html_url'], False)
                attrs['id_repository'] = database.get_repository_id(attrs['html_url'])

            else:
                seen = database.get_repository_by_id(attrs['id_repository'])['seen']
                if seen == 1:
                    continue

            attrs['project_page'] = search_project_page(attrs['html_url'])
            attrs['request_datetime'] = datetime2str(datetime.now(), time=True)

            database.add_repositories_requests(attrs)


def get_updates(max_updates: int = None, mark_as_seen=True):
    repositories = database.get_repositories_requests_updates()
    num_updates = len(repositories)

    repositories = sorted(repositories,
            key=lambda r: -(r['stargazers_count'] + r['subscribers_count'] + r['forks_count'] +
                r['open_issues_count'] + r['network_count'])
    )

    if max_updates is not None:
        repositories = repositories[:max_updates]

    if mark_as_seen:
        for r in repositories:
            database.update_repository_property(r['html_url'], 'seen', True)

    return repositories, num_updates


if __name__ == '__main__':
    print(get_updates(mark_as_seen=False))
