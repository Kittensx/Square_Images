import os
import shutil
import logging
import multiprocessing
import psutil
import queue
from datetime import datetime
from tqdm import tqdm
from PIL import Image, ImageOps

from modules.image_processing import resize_image, process_resizing_parallel
from modules.custom_logging import setup_logging, log_message
from modules.config_loader import ConfigLoader
from modules.globals_vars import total_time, total_images
from modules.utils import update_total_time


class ImageResizer:
    def __init__(self, config):
        setup_logging()
        self.config = config

        self.progress_bar_enabled = self.config.get("progress_bar", True)
        self.max_workers = self._get_max_workers()
        self.batch_size = self.config.get("batch_size", 10)
        self.output_folder = self.config.get("output_folder", "./data/processed")
        self.copy_delete = self.config.get("copy_delete", 0)
        self.image_queue = queue.Queue()

        log_message("Starting image resizing process...")
        log_message(f"Using max_workers: {self.max_workers}")

    def _get_max_workers(self):
        user_defined_workers = self.config.get("max_workers", None)
        recommended_workers = self._get_recommended_workers()
        return user_defined_workers if user_defined_workers is not None else recommended_workers

    @staticmethod
    def _get_recommended_workers():
        cpu_count = multiprocessing.cpu_count()
        available_memory = psutil.virtual_memory().available / (1024 ** 3)

        if available_memory < 4:
            return max(2, cpu_count // 2)
        elif available_memory > 16:
            return min(cpu_count * 2, cpu_count + 4)
        return cpu_count

    def send_to_queue(self, image_path):
        self.image_queue.put(image_path)
        log_message(f"Image added to queue: {image_path}")

    def process_queue(self, output_folder, sizes):
        while not self.image_queue.empty():
            image_path = self.image_queue.get()
            resize_image(image_path, output_folder, sizes, self.config)
            self.image_queue.task_done()
            log_message(f"Processed image: {image_path}")

        if self.config.get("enable_queue", True):
            self.process_queue(output_folder, sizes)
        else:
            process_resizing_parallel(self.config["input_folders"][0], output_folder, sizes, self.max_workers)

    def copy_original_images(self, bin_folder, originals_folder):
        if not os.path.exists(originals_folder):
            os.makedirs(originals_folder, exist_ok=True)

        image_files = []
        for root, _, files in os.walk(bin_folder):
            for file in files:
                if file.lower().endswith((".png", ".jpg", ".jpeg", ".tiff", ".nef")):
                    image_files.append(os.path.join(root, file))

        for image_path in image_files:
            relative_path = os.path.relpath(image_path, bin_folder)
            target_path = os.path.join(originals_folder, relative_path)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.copy2(image_path, target_path)
            log_message(f"Copied {relative_path} to originals folder.")

        log_message(f"Finished copying {len(image_files)} images to the originals folder.")

    def log_summary(self):
        current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_file = f'summary_{current_datetime}.log'
        summary_path = os.path.join('./logs', summary_file)

        with open(summary_path, 'w') as summary:
            if total_images > 0:
                avg_time = total_time / total_images
                summary.write(f"Total images processed: {total_images}\n")
                summary.write(f"Total time for all images: {total_time:.2f} seconds\n")
                summary.write(f"Average time per image: {avg_time:.2f} seconds\n")
            else:
                summary.write("No images were processed.\n")

        tqdm.write(f"Summary written to {summary_path}")
