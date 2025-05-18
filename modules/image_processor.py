import os
from time import time
from PIL import Image, ImageOps
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.config_loader import PauseManager, TimeTracker
from modules.logger_utils import LoggerManager, SummaryLogger
from modules.image_padder import ImagePadder



class ImageProcessor:
    def __init__(self, config, time_tracker=None, logger=None):
        self.config = config
        self.time_tracker = time_tracker or TimeTracker()
        self.logger = logger or LoggerManager()

        self.color_string = self.config.get("padding_color", "white").lower()
        self.custom_colors = {
            k.lower(): tuple(v) for k, v in self.config.get("custom_named_colors", {}).items()
        }
        self.padding_color_rgb = ImagePadder.parse_color_string(self.color_string, self.custom_colors)

    def resize_image(self, image_path, output_folder, sizes, pbar=None):
        img = Image.open(image_path)
        filename = os.path.basename(image_path)
        file_base, ext = os.path.splitext(filename)
        start_time = time()

        #padding_color = self.config.get("padding_color", "white")
        #color_map = {"white": (255, 255, 255), "black": (0, 0, 0)}
        #padding_color_rgb = color_map.get(padding_color.lower(), padding_color)

        for size in sizes:
            img_resized = ImageOps.contain(img, (size, size), method=Image.LANCZOS)
            img_padded = ImageOps.pad(img_resized, (size, size), method=Image.LANCZOS, color=self.padding_color_rgb)           


            size_folder = os.path.join(output_folder, f"img_{size}")
            os.makedirs(size_folder, exist_ok=True)

            output_filename = f"{file_base}_{size}{ext}"
            output_path = os.path.join(size_folder, output_filename)
            img_padded.save(output_path)
            self.logger.log(f"Padded with color and saved: {output_path}")

        if pbar:
            pbar.update(1)

        processing_time = time() - start_time
        self.time_tracker.update_time(processing_time)
        self.time_tracker.increment_images()
        self.logger.log(f"Time taken for {filename}: {processing_time:.2f} seconds")
        return image_path

    def find_images(self, input_folder, supported_formats=(".jpg", ".png", ".jpeg", ".tiff", ".nef")):
        image_files = []
        for root, dirs, files in os.walk(input_folder):
            for file in files:
                if file.lower().endswith(supported_formats):
                    image_files.append(os.path.join(root, file))
        return image_files

    def process_resizing_parallel(self, bin_folder, output_folder, sizes, max_workers):
        image_files = self.find_images(bin_folder)
        if not image_files:
            self.logger.log("No images found in the bin folder.")
            return

        self.logger.log(f"Found {len(image_files)} images in the bin folder for processing.")
        pbar = tqdm(total=len(image_files), desc="Processing images", unit="image")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.resize_image, path, output_folder, sizes, pbar) for path in image_files]
            for future in as_completed(futures):
                future.result()

        pbar.close()
        self.logger.log("Image processing completed.")

        if self.time_tracker.total_images > 0:
            avg_time = self.time_tracker.average_time()
            self.logger.log(f"Total images processed: {self.time_tracker.total_images}")
            self.logger.log(f"Total wall-clock time: {self.time_tracker.total_time:.2f} seconds")
            self.logger.log(f"Average time per image: {avg_time:.2f} seconds")
        else:
            self.logger.log("No images were processed.")

        SummaryLogger().write_summary(self.time_tracker)

    def process_resizing_in_batches(self, bin_folder, output_folder, sizes, batch_size):
        image_files = self.find_images(bin_folder)
        if not image_files:
            self.logger.log("No images found in the bin folder.")
            return

        for i in range(0, len(image_files), batch_size):
            batch = image_files[i:i + batch_size]
            self.logger.log(f"Processing batch {i // batch_size + 1} of {len(image_files) // batch_size + 1}")

            for image_path in batch:
                relative_path = os.path.relpath(os.path.dirname(image_path), bin_folder)
                self.resize_image(image_path, output_folder, sizes)

        if self.time_tracker.total_images > 0:
            avg_time = self.time_tracker.average_time()
            self.logger.log(f"Total images processed: {self.time_tracker.total_images}")
            self.logger.log(f"Total time for all images: {self.time_tracker.total_time:.2f} seconds")
            self.logger.log(f"Average time per image: {avg_time:.2f} seconds")
        else:
            self.logger.log("No images were processed.")