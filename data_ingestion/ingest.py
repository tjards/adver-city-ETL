import os
import requests
from tqdm import tqdm
import subprocess
from directory_tree import DisplayTree
from PIL import Image
import matplotlib.pyplot as plt
from pathlib import Path
import random

from data_ingestion.explore import build_filename, download_file, extract_file

def download_multi(DATA_DIR, BASE_URL, PREFIXES, WEATHERS, DENSITIES, VALID_PREFIX, VALID_WEATHER, VALID_DENSITY):

    # master directory for data 
    data_dir = Path(DATA_DIR)
    data_dir.mkdir(parents=True, exist_ok=True)

    # iterate through all the lists
    for prefix in PREFIXES:
        for weather in WEATHERS:
            for density in DENSITIES:
    
                # build filename from list
                filename = build_filename(
                    prefix=prefix,
                    weather=weather,
                    density=density,
                    VALID_PREFIX=VALID_PREFIX,
                    VALID_WEATHER=VALID_WEATHER,
                    VALID_DENSITY=VALID_DENSITY,
                )

                # url for this file download
                download_url = f"{BASE_URL}/{filename}"

                # pull down the raw data (probably zipped)
                downloaded_dir = download_file(
                    DATA_DIR = DATA_DIR,
                    DOWNLOAD_URL = download_url,
                    FILENAME = filename
                )

                print(f"downloaded {filename} at: \n {downloaded_dir}")

def extract_multi(DATA_DIR, PREFIXES, WEATHERS, DENSITIES, VALID_PREFIX, VALID_WEATHER, VALID_DENSITY):

    # master directory for data 
    data_dir = Path(DATA_DIR)
    data_dir.mkdir(parents=True, exist_ok=True)

    # this is where the extracted files will dump
    extracted_root = data_dir / "extracted"
    extracted_root.mkdir(parents=True, exist_ok=True)

    # initialize dirs
    extracted_dirs = []

    # iterate through all the lists
    for prefix in PREFIXES:
        for weather in WEATHERS:
            for density in DENSITIES:
                
                # build filename from list
                filename = build_filename(
                    prefix=prefix,
                    weather=weather,
                    density=density,
                    VALID_PREFIX=VALID_PREFIX,
                    VALID_WEATHER=VALID_WEATHER,
                    VALID_DENSITY=VALID_DENSITY,
                )

                # extract them
                extracted_dir = extract_file(
                    DIR_IN = DATA_DIR,
                    FILENAME_IN = filename,
                    DIR_OUT = str(extracted_root),
                    data_format="7z"
                )
                print(f"extracted {filename} at: \n {extracted_dir}")
                      
                extracted_dirs.append(Path(extracted_dir))

    return extracted_dirs

