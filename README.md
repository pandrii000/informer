# informer

Simple python application, that parse, analyse, scrap anything new information about the latest researcher in machine learning related.

Currently it support 3 modules:
1. **api**: Updating information. Writes updates into simple sqlite3 database.
2. **bot**: Telegram bot, that send updates to your personal telegram account and support autopost to the telegram channel. Example: https://t.me/github_links.
3. **web**: Web UI, to visualise updates in readable form (screenshot below). 

![](./docs/2021-11-30_21-14.png)