# === DATABASE ===
PROJECT_PATH = None # PATH TO informer folder
DB_PATH = PROJECT_PATH + 'database.db'
SQL_PATH = PROJECT_PATH + 'database/sql/'

# === GITHUB ===
GITHUB_API_TOKENS = {
    # token_name: token_value
}
update_config = {
    'last_time_pushed_interval': {
        'days': 7,
    },
    'minimal_stars': 2,
    'update_interval': 60 * 30, # seconds
}

# === TELEGRAM ===
TELEGRAM_BOT_TOKEN = None
FORWARD_CHAT_ID = None
MY_CHAT_ID = None

HELP = '''
Commands available:
start - Start bot
help - Help
update - Update
analyse - Analyse
queries - Queries
clean_db - Clean database (auto-backup)
backup_db - Backup database
add_query - Add query
remove_query - Remove query
set_time_interval - Set time interval
get_time_interval - Get time interval
'''

