from time import sleep

from src.config.config import CONFIG
from src.api.update import update_database
from src.api.update import clean_database


def serve_autoupdate():
    while True:
        try:
            update_database()
            clean_database()
        except Exception as e:
            print(e)
        finally:
            sleep(CONFIG['github']['update']['interval'])
