'''
Utilities useful for data exploration
'''


# imports
import os
import requests
from tqdm import tqdm
import subprocess
from directory_tree import DisplayTree
from PIL import Image
import matplotlib.pyplot as plt
from pathlib import Path
import random


# build a filename from valid prefix, weather, and density
def build_filename(prefix, weather, density, VALID_PREFIX, VALID_WEATHER, VALID_DENSITY):
 
    prefix = prefix.lower()
    weather = weather.lower()
    density = density.lower()

    if prefix not in VALID_PREFIX:
        raise ValueError(f"Invalid prefix '{prefix}'. Valid: {sorted(VALID_PREFIX)}")

    if weather not in VALID_WEATHER:
        raise ValueError(f"Invalid weather code '{weather}'. Valid: {sorted(VALID_WEATHER)}")

    if density not in VALID_DENSITY:
        raise ValueError(f"Invalid scene type '{density}'. Valid: {sorted(VALID_DENSITY)}")

    return f"{prefix}_{weather}_{density}.7z"

# check if valid
def is_valid_download(path, file_type = '7z'):
    if not path.exists() or path.stat().st_size < 32:
        return False
    with path.open("rb") as f:
        if file_type == '7z':
            magic_number = b"\x37\x7A\xBC\xAF\x27\x1C" # these are the first 6 bytes for a 7-zip file
            return f.read(6) == magic_number
        else:
            raise ValueError(f"Unable to verify downloads for file type: {file_type}")


# download a file from a given URL
streaming_protection = True
file_type = '7z'

def download_file(DATA_DIR, DOWNLOAD_URL, FILENAME):

    # make the data directory if it doesn't exist
    DATA_DIR = Path(DATA_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    FILE_PATH = DATA_DIR / FILENAME
    #DOWNLOAD_URL = "{BASE_URL}/{FILENAME}"

    # simpler download without streaming protection (not recommended)
    if not streaming_protection:

        # check if file already exists
        if os.path.exists(FILE_PATH):
            print(f"A file already exists, skipping download:\n  {FILE_PATH}")
            return FILE_PATH

        # reach out to server 
        response = requests.get(DOWNLOAD_URL, stream=True)

        # retrieve the total file size from headers
        total_size = int(response.headers.get("content-length", 0))

        # download 
        with open(FILE_PATH, "wb") as file:
            for data in tqdm(
                response.iter_content(chunk_size=1024),
                total=total_size // 1024,
            ):
                file.write(data)

    else:

        file_path_temp = FILE_PATH.with_suffix(FILE_PATH.suffix + ".part")     # temporary file to store while streaming

        # if the path exists and is also valid, return the file
        if FILE_PATH.exists() and is_valid_download(FILE_PATH, file_type = file_type):
            print(f"A valid file already exists, skipping download:\n  {FILE_PATH}")
            return str(FILE_PATH)
        
        # if not, remove the invalid file
        if FILE_PATH.exists():
            print(f"Removing invalid file:\n  {FILE_PATH}")
            FILE_PATH.unlink()

        print(f"Downloading {FILENAME} at:\n  {DOWNLOAD_URL}")

        # do a safer download in chunks
        with requests.get(DOWNLOAD_URL, stream=True, timeout=60) as r:
            
            # let me know if it doesn't succeed
            r.raise_for_status()
            
            # get response size
            total_size = int(r.headers.get("content-length", 0))            
            
            # open the path
            with open(file_path_temp, "wb") as f:
                for chunk in tqdm(
                    r.iter_content(chunk_size=1024 * 1024),
                    total=(total_size // (1024 * 1024)) if total_size else None,
                    ):
                    if chunk:
                        f.write(chunk)

        # rename guarantees complete or nothing
        file_path_temp.replace(FILE_PATH) 

        if not is_valid_download(FILE_PATH, file_type = '7z'):
            FILE_PATH.unlink(missing_ok=True)
            raise RuntimeError(f"Downloaded file is not a valid {file_type} file: {FILE_PATH}")

    return str(FILE_PATH)

# extract a file format
def extract_file(DIR_IN, FILENAME_IN, DIR_OUT, data_format="7z"):
    
    # build the file path to extract from 
    FILE_PATH_IN = os.path.join(DIR_IN, FILENAME_IN)

    # check if source file exists
    if not os.path.exists(FILE_PATH_IN):
        raise FileNotFoundError(f"File not found: {FILE_PATH_IN}")
    
    # make output directory if it doesn't exist
    os.makedirs(DIR_OUT, exist_ok=True)

    # safety: do not overwrite existing files
    expected_subdir = os.path.splitext(FILENAME_IN)[0]      # clips the extension 
    expected_dir = os.path.join(DIR_OUT, expected_subdir)   # builds expected directory 
    if os.path.isdir(expected_dir):
        print(f"Already extracted, skipping:\n  {expected_dir}")
        return expected_dir
    
    # extract using 7z
    print(f"Extracting:\n  from : {FILE_PATH_IN}\n  to: {DIR_OUT}")

    if data_format == "7z":
        subprocess.run(
            ["7z", "x", FILE_PATH_IN, f"-o{DIR_OUT}", "-y"], 
            check=True
        )
    else:
        raise ValueError(f"Trying to extract unsupported data format: {data_format}")
    
    return expected_dir


# print the folder tree
def print_folder_tree(root_dir, max_depth=1):

    # configuration
    config_tree = {
        # specify starting path 
        "dirPath": root_dir,
        # set False to include both files and directories
        "onlyDirs": False,
        # set maximum depth for tree
        "maxDepth": max_depth,
        # specify sorting option (100 = no specific sort)
        "sortBy": 100,
    }
    # create and display tree
    DisplayTree(**config_tree)

# get agent ids
def get_agent_ids(root_dir, include_negative=True):
    
    root_dir = Path(root_dir)

    agent_ids = []
    for p in root_dir.iterdir():
        if not p.is_dir():
            continue

        name = p.name
        if not name.lstrip("-").isdigit():
            continue

        if not include_negative and name.startswith("-"):
            continue

        agent_ids.append(name)

    # sort numerically
    agent_ids.sort(key=int)
    return agent_ids

# find image
def find_imgs(root, camera=None, ext=".png", limit=5):

    # we specify the root direct
    root = Path(root)

    # if I don't specify a camera, return all
    if camera is None:
        pattern = f"*camera*{ext}"
    # else, return a specific one
    else:
        pattern = f"*{camera}*{ext}"

    if limit is None:
        # we can limit the max returns
        return sorted(root.rglob(pattern))
    else:
        return sorted(root.rglob(pattern))[:limit]

# show image
def show_image(path, title=None, figsize = (6,6)):
    try:
        img = Image.open(path).convert("RGB")
    except Exception as e:
        print(f"Failed to load image: {path}\n{e}")
        return

    plt.figure(figsize=figsize)
    plt.imshow(img)
    plt.axis("off")
    if title:
        plt.title(title)
    else:
        plt.title(f"{img.size[0]}x{img.size[1]}")
    plt.show()

# show images as a grid
def show_images_grid(imgs, rows=2, cols=3, randomize = True, seed=None):
    n = rows * cols

    if not imgs:
        print("No images to show.")
        return

    if randomize:
        if seed is not None:
            random.seed(seed)
        imgs = random.sample(imgs, min(n, len(imgs)))
    else:
        imgs = imgs[:n]

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 4))
    axes = axes.flatten()

    for ax, path in zip(axes, imgs):
        img = Image.open(path).convert("RGB")
        ax.imshow(img)
        ax.set_title(f"{img.size[0]} × {img.size[1]}", fontsize=10)
        ax.axis("off")

    # turn off unused axes
    for ax in axes[len(imgs):]:
        ax.axis("off")

    plt.tight_layout()
    plt.show()

# list the unique images sizes
def list_image_sizes(imgs, verbose=True):

    sizes = set()

    for path in imgs:
        try:
            with Image.open(path) as img:
                sizes.add(img.size)  # (width, height)
        except Exception as e:
            print(f"Failed to read image: {path}\n{e}")

    if verbose:
        print(f"Found {len(sizes)} unique image size(s) in {len(imgs)} images:")
        for w, h in sorted(sizes):
            print(f"  {w} × {h}")

    return sizes