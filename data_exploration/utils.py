# imports
import os
import requests
from tqdm import tqdm

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

    # reach out to server 
    response = requests.get(DOWNLOAD_URL, stream=True)

    # retrieve the total file size from headers
    total_size = int(response.headers.get("content-length", 0))

    # download (UNCHANGED)
    with open(FILE_PATH, "wb") as file:
        for data in tqdm(
            response.iter_content(chunk_size=1024),
            total=total_size // 1024,
        ):
            file.write(data)
    
    return FILE_PATH


