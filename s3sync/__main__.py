from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import boto3

def push_to_s3(filename, data):
    """
    """

    s3_object_key = filename
    s3_client = boto3.client("s3")
    s3_bucket_name = "treasuryields"
    s3_client.put_object(Bucket=s3_bucket_name, Key=s3_object_key, Body=data)

class EventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # Check if file still exists.
        # Push to S3
        pass

if __name__ == "__main__":
    path = './x'
    event_handler = EventHandler()
    
    observer = Observer()

    for file in file
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    try:
        # Allow the observer to run indefinitely until KeyboardInterrupt
        observer.join()
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
