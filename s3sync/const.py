import pathlib

HOME_DIR: pathlib.Path = pathlib.Path("~").expanduser()
WATCHLIST_PATH: pathlib.Path = HOME_DIR / pathlib.Path(".local/share/s3sync/watchlist")
