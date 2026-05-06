import subprocess
import threading
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class RestartHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.restarting = False
        self.start_process()

    def start_process(self):
        print("\n🚀 Starting Dia...\n")
        self.process = subprocess.Popen(["python", "main.py"])

    def restart_process(self):
        if self.restarting:
            return

        self.restarting = True

        if self.process:
            print("\n🔁 Restarting Dia...\n")
            self.process.terminate()
            self.process.wait()

        self.start_process()

        time.sleep(1)
        self.restarting = False

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            self.restart_process()


def auto_pull(handler):
    while True:
        result = subprocess.run(["git", "pull"], capture_output=True, text=True)

        if result.returncode != 0:
            time.sleep(30)
            continue

        output = result.stdout.lower()

        if "already up to date" not in output and output.strip():
            print("\n⬇️ New updates found!\n")
            handler.restart_process()

        time.sleep(10)


if __name__ == "__main__":
    path = "."

    handler = RestartHandler()

    observer = Observer()
    observer.schedule(handler, path, recursive=True)
    observer.start()

    pull_thread = threading.Thread(target=auto_pull, args=(handler,), daemon=True)

    pull_thread.start()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()

        if handler.process:
            handler.process.terminate()

    observer.join()
