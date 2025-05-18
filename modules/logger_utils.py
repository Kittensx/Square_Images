import os
import logging
from datetime import datetime
import re
from modules.config_loader import ConfigLoader


class LoggerManager:
    """
    Handles setup and usage of logging.
    """
    def __init__(self, log_dir='./logs', log_file='image_processing.log'):
        
        self.log_path = os.path.join(log_dir, log_file)
        os.makedirs(log_dir, exist_ok=True)

        logging.basicConfig(
            filename=self.log_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def log(self, message, level="info"):
        if level == "info":
            logging.info(message)
        elif level == "error":
            logging.error(message)
        elif level == "debug":
            logging.debug(message)

        print(message)  # Also print to console


class SummaryLogger:
    """
    Writes a summary log for a single run.
    """
    def __init__(self, log_dir='./logs'):
        
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

    def write_summary(self, time_tracker):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'summary_{timestamp}.log'
        path = os.path.join(self.log_dir, filename)

        with open(path, 'w') as f:
            if time_tracker.total_images > 0:
                avg = time_tracker.average_time()
                f.write(f"Total images processed: {time_tracker.total_images}\n")
                f.write(f"Total time for all images: {time_tracker.total_time:.2f} seconds\n")
                f.write(f"Average time per image: {avg:.2f} seconds\n")
            else:
                f.write("No images were processed.\n")

        print(f"Summary written to {filename}")


class DailyAggregator:
    """
    Aggregates all summary logs by day and writes a daily summary file.
    """
    def __init__(self, summary_dir='./logs'):        
        self.summary_dir = summary_dir

    def analyze(self):
        files = [f for f in os.listdir(self.summary_dir) if f.startswith('summary_') and f.endswith('.log')]
        data_by_day = {}

        for file in files:
            match = re.match(r'summary_(\d{8})_\d{6}\.log', file)
            if match:
                date = match.group(1)
                if date not in data_by_day:
                    data_by_day[date] = {'total_images': 0, 'total_time': 0.0}

                with open(os.path.join(self.summary_dir, file), 'r') as f:
                    for line in f:
                        if line.startswith('Total images processed:'):
                            data_by_day[date]['total_images'] += int(line.split(':')[1].strip())
                        elif line.startswith('Total time for all images:'):
                            data_by_day[date]['total_time'] += float(line.split(':')[1].strip().replace(' seconds', ''))

        for date, data in data_by_day.items():
            if data['total_images'] > 0:
                avg = data['total_time'] / data['total_images']
                file_name = f'daily_summary_{date}.log'
                with open(os.path.join(self.summary_dir, file_name), 'w') as f:
                    f.write(f"Summary for {date}:\n")
                    f.write(f"Total images processed: {data['total_images']}\n")
                    f.write(f"Total time for all images: {data['total_time']:.2f} seconds\n")
                    f.write(f"Average time per image: {avg:.2f} seconds\n")
                print(f"Daily summary written to {file_name}")
