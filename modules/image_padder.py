import os
from PIL import Image, ImageOps
from modules.logger_utils import LoggerManager



class ImagePadder:
    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger or LoggerManager()
        self.padding_method = self.config.get("padding_method", "color")    
        
        self.color_file_path = self.config.get("named_color_file", "./colors.txt")
        self.custom_colors = self._load_named_colors(self.color_file_path)
        
        self.padding_color = self.parse_color_string(
            self.config.get("padding_color", "white"), 
            self.custom_colors
        )

           
    def _load_named_colors(self, filepath):
        ''' Loads custom colors from a .txt file '''
        colors = {}
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                for line in f:
                    if ':' in line:
                        name, rgb = line.strip().split(':', 1)
                        try:
                            colors[name.strip().lower()] = tuple(map(int, rgb.strip().split(',')))
                        except ValueError:
                            print(f"Invalid color format in {filepath}: {line}")
        return colors


    
    @staticmethod
    def parse_color_string(color_string, custom_colors={}):
        try:
            # 1. Named colors from config
            if color_string.lower() in custom_colors:
                return tuple(custom_colors[color_string.lower()])

            # 2. Comma-separated RGB string: "255,255,255"
            if ',' in color_string and not color_string.strip().lower().startswith('rgb'):
                return tuple(map(int, color_string.strip().split(',')))

            # 3. Hex format: "#ffffff"
            if color_string.startswith('#'):
                hex_color = color_string.lstrip('#')
                if len(hex_color) == 6:
                    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                elif len(hex_color) == 3:
                    return tuple(int(hex_color[i]*2, 16) for i in range(3))
                else:
                    raise ValueError(f"Invalid hex color: {color_string}")

            # 4. CSS color, rgb(), rgba(), and other web formats
            from PIL import ImageColor
            return ImageColor.getrgb(color_string)

        except Exception as e:
            raise ValueError(f"Invalid color format '{color_string}': {e}")





    def pad_with_color(self, image_path, output_folder):
        try:
            img = Image.open(image_path)
            width, height = img.size

            if width < height:
                padding = ((height - width) // 2, 0, (height - width + 1) // 2, 0)
            else:
                padding = (0, (width - height) // 2, 0, (width - height + 1) // 2)

            padded_img = ImageOps.expand(img, padding, fill=self.padding_color)

            os.makedirs(output_folder, exist_ok=True)
            output_filename = os.path.basename(image_path)
            output_path = os.path.join(output_folder, output_filename)
            padded_img.save(output_path)
            self.logger.log(f"Padded with color and saved: {output_path}")

        except Exception as e:
            self.logger.log(f"Error padding {image_path}: {e}", level="error")

    def pad_with_ai(self, image_path, output_folder):
        self.logger.log(f"AI padding feature for {image_path} not yet implemented.")

    def process_folder(self, bin_folder, output_folder):
        image_files = [f for f in os.listdir(bin_folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))]

        if not image_files:
            self.logger.log("No images found in the bin folder.")
            return

        for image_file in image_files:
            image_path = os.path.join(bin_folder, image_file)

            if self.padding_method == "ai":
                self.pad_with_ai(image_path, output_folder)
            else:
                self.pad_with_color(image_path, output_folder)
