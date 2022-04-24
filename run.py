from multiprocessing import Process

from src.config.config import CONFIG
from src.api.database import initialize_database


if __name__ == '__main__':
    initialize_database()

    if 'autoupdate' in CONFIG['modules']:
        from src.api.autoupdate import serve_autoupdate
        Process(target=serve_autoupdate).start()

    if 'web' in CONFIG['modules']:
        from src.web.app import serve_web
        Process(target=serve_web, args=(
            CONFIG['web']['host'],
            CONFIG['web']['port'],
        )).start()

    if 'bot' in CONFIG['modules']:
        from src.bot.functions import serve_bot
        Process(target=serve_bot).start()

