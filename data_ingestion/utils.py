# imports
import os
import requests
from tqdm import tqdm
import subprocess

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

# download a file from a given URL
def download_file(DATA_DIR, DOWNLOAD_URL, FILENAME):

    # make the data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    FILE_PATH = os.path.join(DATA_DIR, FILENAME)

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
    
    return FILE_PATH

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
        return
    
    # extract using 7z
    print(f"Extracting:\n  from : {FILE_PATH_IN}\n  to: {DIR_OUT}")

    if data_format == "7z":
        subprocess.run(
            ["7z", "x", FILE_PATH_IN, f"-o{DIR_OUT}", "-y"], 
            check=True
        )
    else:
        raise ValueError(f"Trying to extract unsupported data format: {data_format}")

