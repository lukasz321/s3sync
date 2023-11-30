import os
import pathlib
from typing import List
import time

import boto3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .const import *

try:
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ.get("aws_access_key_id"),
        aws_secret_access_key=os.environ.get("aws_secret_access_key"),
    )
except KeyError:
    print("Have you exported your AWS credentials?")
    print("")
    print("Expected env variables:")
    print(" - aws_access_key_id")
    print(" - aws_secret_access_key")
    print("")
    print("If you're running this via default systemd service,")
    print("these env vars are expected in ~/.s3sync.aws/credentials")
    exit(1)


def push_to_s3(file_path: pathlib.Path):
    s3_object_key = file_path.name
    s3_bucket_name = "s3sync-public"

    try:
        s3.upload_file(str(file_path), s3_bucket_name, s3_object_key)
    except FileNotFoundError:
        print(f"The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    else:
        print(
            f"File '{file_path}' uploaded to '{s3_bucket_name}/{s3_object_key}' successfully."
        )


class EventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return

        path = pathlib.Path(event.src_path)

        push_to_s3(path)


if __name__ == "__main__":
    try:
        with open(WATCHLIST_PATH, "r+") as f:
            files: List = [pathlib.Path(l.replace("\n", "")) for l in f.readlines()]
    except FileNotFoundError:
        WATCHLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(WATCHLIST_PATH, "a+") as f:
            pass

        files = []

    event_handler = EventHandler()
    observer = Observer()

    num_watching = 0
    for file in files:
        if not file.exists():
            print(f"Skipping {file} as it does not exist!")
            continue
        elif not file.is_file():
            print(f"Skipping {file} as it not a file!")
            continue

        num_watching = +1
        observer.schedule(event_handler, file, recursive=False)
        observer.start()

    print(f"Observing {num_watching} files.")

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
