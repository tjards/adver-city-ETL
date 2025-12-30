# imports
import requests
from tqdm import tqdm

# build a filename from desired prefix, weather, and traffic density 
def build_filename(prefix, weather, density, 
                   VALID_PREFIX, VALID_WEATHER, VALID_DENSITY, 
                   ARCHIVE_EXT):
 
    prefix = prefix.lower()
    weather = weather.lower()
    density = density.lower()

    if prefix not in VALID_PREFIX:
        raise ValueError(f"Invalid prefix '{prefix}'. Valid: {sorted(VALID_PREFIX)}")

    if weather not in VALID_WEATHER:
        raise ValueError(f"Invalid weather code '{weather}'. Valid: {sorted(VALID_WEATHER)}")

    if density not in VALID_DENSITY:
        raise ValueError(f"Invalid scene type '{density}'. Valid: {sorted(VALID_DENSITY)}")

    return f"{prefix}_{weather}_{density}{ARCHIVE_EXT}"

# build multiple filenames
def build_filenames(CHOOSE_PREFIX, CHOOSE_WEATHER, CHOOSE_DENSITY, 
                    VALID_PREFIX, VALID_WEATHER, VALID_DENSITY,
                    ARCHIVE_EXT):

    filenames = []
    for p in CHOOSE_PREFIX:
        for w in CHOOSE_WEATHER:
            for d in CHOOSE_DENSITY:
                filenames.append(build_filename(p, w, d, 
                                                VALID_PREFIX, VALID_WEATHER, VALID_DENSITY, 
                                                ARCHIVE_EXT)
                                                )
    
    return filenames               

# check the content length of a file
'''
recall HTTP lingo:
    200     = Content (OK)
    204     = No Content (OK)
    206     = Partial Content (OK)
    403     = forbidden 
    404     = broken 
    > 500   = server errors 
'''
def content_length(url, timeout):

    # request the header
    r = requests.head(url, timeout = timeout, allow_redirects=True)
    if not (200 <= r.status_code < 300):
        return None
    
    # get the content length
    content_length = r.headers.get("content-length", None)
    
    # return
    if content_length is None:
        return None
    else:
        return int(content_length)
    


# download a file
def download_file(url, destination, filename, timeout):
    
    # note: I shouldn't pass in both the destination and the filename (redundant), fix later

    # temp file for partial downloads
    temp = destination.with_suffix(destination.suffix + ".part")
    
    # return, if it's been completed 
    if destination.exists():
        return destination

    if temp.exists():
        temp.unlink()

    with requests.get(url, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))

        with open(temp, "wb") as f, tqdm(total=total, unit="B", unit_scale=True, desc=filename) as bar:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))

    temp.rename(destination)

    return destination 

# download multiple files (same dir, has a GB budget [per file])
def download_files(base_url, 
                   destinations_dir, 
                   filenames, 
                   timeout = 60, 
                   max_size_GB = 5, 
                   overwrite = False):

    # convert GB to B
    max_B = int(max_size_GB * 1024 ** 3)

    # initialize
    downloaded = []
    destinations_dir.mkdir(parents = True, exist_ok = True)

    for filename in filenames:

        # build url and filename for this item in the list 
        url = f"{base_url}/{filename}"
        destination = destinations_dir / filename

        # avoid overwrite, if desired and if it exists
        if not overwrite and destination.exists():
            # record it as already downloaded
            downloaded.append(destination)
            # try next in list
            continue

        # avoid files that are too big
        if max_B is not None:
            # get size
            size = content_length(url, timeout)
            # if no return
            if size is None:
                size = 0 # this would be suspicious, but keep going
            # if it's too big
            if size > max_B:
                # try next in the list
                print(f"[SKIP] {filename} would exceed {max_size_GB} GB.")
                continue 

        # if you made it this far, try download
        try:
            downloaded_file = download_file(url, destination, filename, timeout)
            downloaded.append(downloaded_file)
            print(f"[DOWNLOAD] {filename} successful.")
        except Exception as e:
            print(f"[ERROR] {filename}: {e}")

    return downloaded
            
             







