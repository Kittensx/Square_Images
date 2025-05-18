# 📦 Square Image Processor (Alpha)

#### Square Images is a Python-based image processing tool for batch resizing and padding images into multiple square formats. It uses YAML-based configuration, supports CSS color names and custom color maps, and outputs to structured folders. Ideal for preparing assets for models, datasets, or media workflows. Alpha-stage features include multithreading, optional pause flags, and experimental whitespace removal.
---

## ✅ Current Features (Alpha)

- Resize input images to multiple square dimensions (`resize_sizes`)
- Apply padding using named colors, hex values, or custom RGB mappings
- Skip already-processed images (`skip_processed_images`)
- Multi-core processing with optional worker control
- Progress bar with per-image feedback
- Configurable cleanup options (`remove_empty_folders`)
- Optional keyboard pause/resume (experimental)

---

## ⚙️ Configuration (`config.yaml`)

Only tested and stable options are exposed in this file. For additional functionality (e.g. whitespace removal or advanced thresholds), edit the code directly.

### 🗂 Paths
```yaml
input_folders:
  - ./data/input
output_folder: ./data/processed
originals_folder: ./data/originals
padding_folder: ./data/padding_added_archive
named_color_file: "./config/colors.txt"
```
#### Tips for YAML formatting:

##### Windows Path Tips
Use single quotes ('C:\path') or forward slashes ("C:/path") to avoid escape issues in YAML.
Avoid raw double-quoted Windows paths unless you double the backslashes ("C:\\\path").

---

Use ./folder_name to refer to paths relative to the project root

Use quotes ("" or '') when:

Paths contain special characters

You're referencing color codes like #ffffff

Use consistent slashes (/) even on Windows

Avoid trailing slashes in folder names

#### 🖼 Resizing & Padding

resize_sizes: [768, 1024, 320, 640, 1280]
padding_color: "#ffffff"  # white padding
You can specify the padding color in one of the following ways:

#### ✅ Standard CSS names
white, black, red, lightblue, gray, etc.

#### ✅ Hex values
Use quotes for YAML compatibility:

"#00abcf"    # blue-cyan
"#fff"       # shorthand for white

#### ✅ Comma-separated RGB

```yaml
"255,255,255"  # white
"204,51,255"   # purple-ish

```

#### ✅ Custom named colors
Define your own names in a separate text file (e.g., colors.txt):
```txt
soft_gold: 218,165,32
cool_silver: 192,192,192
```

And reference them by name in your config:

```yaml
padding_color: soft_gold
```

---

## ⚙️ Behavior Toggles
```yaml
enable_pause_resume: false  # Currently disabled in alpha
enable_queue: false         # Placeholder for future support
remove_empty_folders: true  # Clean up folders after processing
```
---

### ⚠️ Known Limitations
enable_pause_resume prints pause/resume prompts but does not pause mid-processing reliably.

copy_bin was deprecated due to inconsistent behavior and is no longer included in the config.

gray_threshold and whitespace_sizes are available internally but not exposed in this release.

When running the program multiple times in a row using the same settings, it will overwrite existing files with the new color. If you want to keep all of the pictures, you will want to move them from the output folder before running the program again. In a future update I may add a feature to move finished files automatically. Until then, move them manually.

---
#### Install

```bash
pip install -r requirements.txt
```
---

#### ▶️ Running the Tool
To run:

```bash
python image_square_processor.py
```

This will:

Look inside all input_folders

Process all supported image formats (.jpg, .png, .jpeg, .tiff, .nef)

Output resized/padded results to folders like:

```bash

./data/processed/img_512/
./data/processed/img_768/

...
📁 Suggested Project Structure
your_project/
├── config/
│   ├── config.yaml
│   └── colors.txt
├── data/
│   ├── input/
│   ├── originals/
│   ├── processed/
│   └── padding_added_archive/
├── logs/
├── modules/
│   └── [*.py files]
└── image_square_processor.py
```
---

## 🧪 Development Notes
This is an alpha-stage tool. Some parts (like whitespace removal and pause manager) are intentionally restricted until they're stabilized. If you're comfortable editing Python, you can enable or tweak hidden features directly.

---

## Test Pictures
I've added test pictures in the .data/processed folder with sample images that have been used when the program ran. In the img_1280 folder I showed a few different colors. I just typed randomly for the green and the purple colors (random hex). Ensure that if you do use hex, you enclose them in single quotation marks, otherwise the "#" sign will make what you type after it as a comment. "#05bc13f" example. For color names that are two words or more - use a hex. This version does not currently support colors longer than one word. Sorry :*(. 

I've also included a test image that shows the program when it runs. Even when creating multiple sizes it still runs very fast.

## 🧑‍💻 License
MIT-style license for personal or internal use. Use at your own risk. If it eats your cat pictures, we're not liable.
