import os
import sys
import datetime
import traceback

class Logger:
    def __init__(self, log_dir):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"log_{timestamp}.txt")
        self.file = open(self.log_file, "a", encoding="utf-8")
        
        # Redirect stdout/stderr
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.stdout = self
        sys.stderr = self
        
        print(f"Logger initialized: {self.log_file}")

    def write(self, message):
        self.stdout.write(message)
        try:
            self.file.write(message)
            self.file.flush()
        except:
            pass

    def flush(self):
        self.stdout.flush()
        self.file.flush()

    def log_exception(self, e):
        print(f"EXCEPTION: {e}")
        traceback.print_exc(file=self)

    def get_log_files(self):
        files = [f for f in os.listdir(self.log_dir) if f.startswith("log_") and f.endswith(".txt")]
        files.sort(reverse=True)
        return files

    def get_log_content(self, filename):
        path = os.path.join(self.log_dir, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        return "Log file not found."
