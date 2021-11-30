from database import functions as database
from bot import functions as bot


def main():
    database.initialize_database()
    bot.serve_bot()


if __name__ == '__main__':
    main()
