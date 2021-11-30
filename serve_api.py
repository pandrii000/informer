from database import functions as database
from api import functions as api


def main():
    database.initialize_database()
    api.serve_api()


if __name__ == '__main__':
    main()
