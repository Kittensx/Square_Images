import os
import cv2
import numpy as np
import shutil
from PIL import Image, ImageChops
from modules.logger_utils import LoggerManager



class WhitespaceProcessor:
    def __init__(self, config, logger=None):
        self.config=config
        self.logger = logger or LoggerManager()
        self.whitespace_sizes=self.config.get("whitespace_sizes", [512])
        self.gray_threshold = self.config.get("gray_threshold", 200)
        raw_sizes = self.config.get("whitespace_sizes", [])
        self.use_original_size = False
        if isinstance(raw_sizes, str):
            raw_sizes = [raw_sizes]

        if isinstance(raw_sizes, list):
            raw_sizes = [str(s).lower() for s in raw_sizes]
            self.use_original_size = "original" in raw_sizes
            self.whitespace_sizes = [int(s) for s in raw_sizes if s != "original"]
        else:
            self.whitespace_sizes = [raw_sizes]
        
        
    def safety_process(self):
        
        if not self.config.get("enable_whitespace_removal", False):
            if self.config.get("debug_enabled", False):
                self.logger.log("Whitespace removal is disabled in config.")
            return

        return True

    def remove_whitespace_and_resize(self, image, image_path, size):
        ''' Experimental process
        '''  
       
        if not self.safety_process():
            return None
            
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary_mask = cv2.threshold(gray, self.gray_threshold, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if cv2.countNonZero(binary_mask) < 10:  # Almost no content found
            self.logger.log(f"Skipping whitespace crop for flat image: {image_path}")
            return cv2.resize(image, (size, size), interpolation=cv2.INTER_AREA)

        if contours:
            x, y, w, h = cv2.boundingRect(contours[0])
            image_cropped = image[y:y + h, x:x + w]
            return cv2.resize(image_cropped, (size, size), interpolation=cv2.INTER_AREA)
        else:
            return cv2.resize(image, (size, size), interpolation=cv2.INTER_AREA)

    def remove_whitespace_process(self, image_path, output_folder, archive_folder, skip_processed=False, copy_to_archive=True):
       
        output_filename = os.path.basename(image_path)
        image = cv2.imread(image_path)
        
        
        if image is None:
            self.logger.log(f"Error reading image: {image_path}", level="error")
            return False
            
        if not self.safety_process():
            return None

        
        sizes = []
        if self.use_original_size:
            sizes.append(max(image.shape[:2]))
        sizes += self.whitespace_sizes


        # Step 1: Crop whitespace once (once we get this working every time
        cropped_image = self.remove_whitespace_and_resize(image)

        # Step 2: Resize it to each target size
        for size in sizes:
            size_folder = os.path.join(output_folder, f"img_{size}")
            output_path = os.path.join(size_folder, output_filename)
            
           
            if self.skip_processed and os.path.exists(output_path):
                self.logger.log(f"Skipping already processed image: {output_path}")
                continue
            resized_image = cv2.resize(cropped_image, (size, size), interpolation=cv2.INTER_AREA)

            # Save to subfolder
            size_folder = os.path.join(output_folder, f"img_{size}")
            os.makedirs(size_folder, exist_ok=True)
           
            cv2.imwrite(output_path, resized_image)
            self.logger.log(f"Whitespace removed and resized to {size}, saved to: {output_path}")

            if copy_to_archive:
                os.makedirs(archive_folder, exist_ok=True)
                archive_path = os.path.join(archive_folder, output_filename)
                shutil.copy(output_path, archive_path)
                self.logger.log(f"Copied image to archive: {archive_path}")
