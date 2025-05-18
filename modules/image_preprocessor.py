import os
import cv2
from modules.config_loader import PauseManager
from modules.logger_utils import LoggerManager
from modules.image_processor import ImageProcessor
from modules.whitespace_processor import WhitespaceProcessor


class ImagePreprocessor:
    def __init__(self, config, processor=None, logger=None, pause_manager=None):
        self.config = config
        self.output_folder = self.config.get("output_folder", "./data/processed")
        self.gray_threshold = self.config.get("gray_threshold", 200)
        self.whitespace_folder = self.config.get("whitespace_folder", "./data/whitespace_removed_archive")
        self.sizes = self.config.get("resize_sizes", [512])
        self.whitespace_sizes=self.config.get("whitespace_sizes", [512])
        self.skip_processed = self.config.get("skip_processed_images", True)
        self.logger = logger or LoggerManager()
        self.processor = processor or ImageProcessor(config, logger=self.logger)
        self.whitespace_util = WhitespaceProcessor(config, logger=self.logger)
        self.pause_manager = pause_manager
       

    def process_folders(self, folders):
        option = self.config.get("whitespace_option", "remove").lower()
        for folder in folders:
            for image_path in self.processor.find_images(folder):
                self.pause_manager.pause_if_needed()
                if option == "remove":
                    self._remove_whitespace(image_path)
                    
                elif option == "add":
                    self._add_padding(image_path)
    
    def _remove_whitespace(self, image_path):
        if not self.whitespace_util.safety_process():
            return  # Skip processing if removal is disabled
        output_filename = os.path.basename(image_path)
        output_path = os.path.join(self.whitespace_folder, output_filename)

        if self.skip_processed and os.path.exists(output_path):
            self.logger.log(f"Skipping already processed image: {output_filename}")
            return

        image = cv2.imread(image_path)
        if image is None:
            self.logger.log(f"Error reading image: {image_path}", level="error")
            return
        
        
        result = self.whitespace_util.remove_whitespace_and_resize(image, self.whitespace_sizes, self.gray_threshold)

        os.makedirs(self.whitespace_folder, exist_ok=True)
        cv2.imwrite(output_path, result)
        self.logger.log(f"Whitespace removed and resized, saved to: {output_path}")
   
    def _add_padding(self, image_path):
        filename = os.path.basename(image_path)

        for size in self.sizes:
            folder = os.path.join(self.output_folder, f"img_{size}")
            output_path = os.path.join(folder, filename)

            if self.skip_processed and os.path.exists(output_path):
                self.logger.log(f"Skipping already processed image: {output_path}")
                continue

            self.processor.resize_image(image_path, self.output_folder, [size])
