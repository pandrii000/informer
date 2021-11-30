from datetime import datetime


def datetime2str(dt: datetime, time=False):
    return dt.strftime('%Y-%m-%d_%H-%M-%S') if time else dt.strftime('%Y-%m-%d')

