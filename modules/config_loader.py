import os
import time
import json
import yaml
import threading


class ConfigLoader:
    """
    Handles loading of configuration files (YAML or JSON).
    """
    @staticmethod
    def load_config(config_path='./config/config.yaml'):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        ext = os.path.splitext(config_path)[-1].lower()
        with open(config_path, 'r') as f:
            if ext == '.yaml' or ext == '.yml':
                return yaml.safe_load(f)
            elif ext == '.json':
                return json.load(f)
            else:
                raise ValueError("Unsupported config file format. Use .yaml, .yml, or .json")


class PauseManager:
    """
    Handles pausing/resuming via a 'pause.flag' file.
    """
import os
import time
import threading
import msvcrt

class PauseManager:
    """
    Handles pausing/resuming via a 'pause.flag' file.
    """
    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger
        self._pause_event = threading.Event()  

    @classmethod
    def start_keyboard_listener(cls):
        def keyboard_loop():
            print("[P]ause / [R]esume")
            while True:
                if msvcrt.kbhit():
                    key = msvcrt.getch().lower()
                    if key == b'p':
                        with open("pause.flag", "w") as f:
                            f.write("paused")
                        print("[Paused]")
                    elif key == b'r':
                        if os.path.exists("pause.flag"):
                            os.remove("pause.flag")
                        print("[Resumed]")

        t = threading.Thread(target=keyboard_loop, daemon=True)
        t.start()

    def pause_if_needed(self):
        if self.config.get("enable_pause_resume", True):
            while os.path.exists('pause.flag'):
                self._pause_event.set()
                print("Paused... waiting to resume.")
                time.sleep(1)
            self._pause_event.clear()

    @staticmethod
    def create_pause_flag():
        with open('pause.flag', 'w') as f:
            f.write('Paused')
        print("Pause flag created.")

    @staticmethod
    def remove_pause_flag():
        if os.path.exists('pause.flag'):
            os.remove('pause.flag')
            print("Pause flag removed.")
        else:
            print("No pause flag to remove.")



class TimeTracker:
    """
    Thread-safe tracker for processing time and image count.
    """
    def __init__(self):
        self.total_time = 0.0
        self.total_images = 0
        self._lock = threading.Lock()

    def update_time(self, seconds: float):
        with self._lock:
            self.total_time += seconds

    def increment_images(self):
        with self._lock:
            self.total_images += 1

    def average_time(self):
        if self.total_images == 0:
            return 0.0
        return self.total_time / self.total_images
