# imports
import requests

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
    r = requests.head(url, timeout = timeout)
    if not (200 <= r.status_code < 300):
        return None
    
    # get the content length
    content_length = r.header.get("content-length", None)
    
    # return
    if content_length is None:
        return None
    else:
        return int(content_length)


