import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class RestartHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.start_process()

    def start_process(self):
        print("\n🚀 Starting Dia...\n")
        self.process = subprocess.Popen(["python", "main.py"])

    def restart_process(self):
        if self.process:
            print("\n🔁 Restarting Dia...\n")
            self.process.terminate()
            self.process.wait()
        self.start_process()

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            self.restart_process()


if __name__ == "__main__":
    path = "."
    event_handler = RestartHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
    observer.join()
