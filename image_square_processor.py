import os
import cv2
from modules.config_loader import ConfigLoader
from modules.logger_utils import LoggerManager
from modules.image_processor import ImageProcessor
from modules.image_preprocessor import ImagePreprocessor
from modules.config_loader import PauseManager
from modules.whitespace_processor import WhitespaceProcessor
from modules.image_padder import ImagePadder


class ImageSquareProcessor:
    def __init__(self, config_path='./config/config.yaml'):
        self.config = ConfigLoader.load_config(config_path)
        self.logger = LoggerManager()

        self.bin_folder = os.path.abspath(self.config['input_folders'][0])
        self.additional_folders = [os.path.abspath(p) for p in self.config.get('input_folders', [])[1:]]
        self.output_folder = os.path.abspath(self.config.get("output_folder", "./data/processed"))
        self.originals_folder = os.path.abspath(self.config.get("originals_folder", "./data/originals"))
        self.whitespace_folder = os.path.abspath(self.config.get("whitespace_folder", "./data/whitespace_removed_archive"))
        self.padding_folder = os.path.abspath(self.config.get("padding_folder", "./data/padding_added_archive"))
        self.sizes = self.config.get("resize_sizes", [768, 1024, 320, 640, 1280])
             
        self.pause_manager=PauseManager(self.config, logger=self.logger)
        self.padder = ImagePadder(self.config, logger=self.logger)
        self.config["custom_named_colors"] = self.padder.custom_colors
        
        self.preprocessor = ImagePreprocessor(self.config, logger=self.logger, pause_manager=self.pause_manager)
        self.processor = ImageProcessor(self.config, logger=self.logger)
        self.whitespace_util = WhitespaceProcessor(self.config, logger=self.logger)
        

    def run(self):
        # Start listening for keyboard input in CMD
        PauseManager.start_keyboard_listener()
        
        all_folders = [self.bin_folder] + self.additional_folders

        # Run whitespace or padding preprocessing first
        self.preprocessor.process_folders(all_folders)

        # Resize using parallel processing
        self.processor.process_resizing_parallel(
            bin_folder=self.bin_folder,
            output_folder=self.output_folder,
            sizes=self.sizes,
            max_workers=self.config.get("max_workers") or os.cpu_count()
        )

        self.logger.log("Image processing completed.")

        if self.config.get("remove_empty_folders", True):
            self._remove_empty_dirs(self.bin_folder)

    def _remove_empty_dirs(self, folder):
        for root, dirs, _ in os.walk(folder, topdown=False):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                try:
                    os.rmdir(dir_path)
                    self.logger.log(f'Removed empty folder: {dir_path}')
                except OSError:
                    pass


if __name__ == '__main__':
    processor = ImageSquareProcessor(config_path='./config/config.yaml')
    processor.run()
    input("Done. Press Enter to exit.")
