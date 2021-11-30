from time import sleep

from api.update import update_database, clean_database
from database.constants import update_config


def serve_api():
    while True:
        update_database()
        clean_database()
        sleep(update_config['update_interval'])
