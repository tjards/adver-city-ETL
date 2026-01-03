import json
from pathlib import Path
import pandas as pd

# extract weather/vis/time labels from archive details
def extract_archive_labels(archive_name, decode_time, decode_vis, archive_ext):

    # remove extension
    archive_name = archive_name.replace(archive_ext, "")

    # decompose the archive name into parts: [prefix, weather, density]
    parts = archive_name.split("_")
    if len(parts) != 3:
        return None

    details = {}
        
    prefix, weather, density = parts

    details["prefix"]   = prefix
    details["weather"]  = weather 
    details["density"]  = density 

    # decode the weather term into the appropriate category
    details["time"]         = decode_time.get(weather, "unknown")
    details["visibility"]   = decode_vis.get(weather, "unknown")
   
    return details 

# pull out other metadata
def extract_img_metadata(img_path):

    '''
    Assumes format : "1011/000060_camera0.png"
                    {agent_id}/{timestamp}_{camera_id}.{extension}
    '''

    # enforce path
    if not isinstance(img_path, Path):
        img_path = Path(img_path)

    details = {}

    details["agent_id"] = img_path.parent.name
    img_name = img_path.stem

    img_name_parts = img_name.split("_")
    # if it has at least two parts, assume first two parts = frame_id and camera_id
    if len(img_name_parts) > 1:
        details["frame_id"] = img_name_parts[0]
        details["camera_id"] = img_name_parts[1]
    else:
        # if it has at least 1 part, assume frame_id 
        if len(img_name_parts) > 0:
            details["frame_id"] = img_name_parts[0]
            details["camera_id"] = None
        else:
            details["frame_id"] = None
            details["camera_id"] = None

    return details

# creates a dataframe with labels and metadata 
def build_labels_df(sampled_dir, decode_time, decode_vis, archive_ext, img_ext):

    # enforce Path type
    if not isinstance(sampled_dir, Path):
        sampled_dir = Path(sampled_dir)
    
    # group by archive
    rows = []
    for archive_dir in sorted(sampled_dir.iterdir()):

        # only do directories
        if not archive_dir.is_dir():
            print(f"[SKIP] {archive_dir} is not a directory")
            continue

        # pull the archive name
        archive_name = archive_dir.name

        # extract archive-level labels
        archive_labels = extract_archive_labels(
            archive_name=archive_name,
            decode_time=decode_time,
            decode_vis=decode_vis,
            archive_ext=archive_ext
        )

        # if we don't get valid labels, skip
        if not archive_labels:
            print(f"[SKIP] cannot extract labels from {archive_name}")
            continue

        # find all images in this archive (recursively)
        for img_file in archive_dir.rglob(f"*{img_ext}"):

            # initial row with archive labels
            row = {}

            # store archive and image name
            row["archive_name"] = archive_name
            row["image_path"] = str(img_file)

            # extract image-level metadata
            img_metadata = extract_img_metadata(img_file)

            # add labels and metadata 
            row.update(archive_labels)
            row.update(img_metadata)

            # append to rows
            rows.append(row)

    # build and return dataframe
    return pd.DataFrame(rows) 

def save_labels(df, output_path):

    # enforce Path type
    if not isinstance(output_path, Path):
        output_path = Path(output_path)

    df.to_csv(output_path, index=False)
    print(f"[SAVE] Labels saved to {output_path}")
    print(f" Total images: {len(df)}")
    print(f" Columns: {list(df.columns)}")
    print(f" head:\n{df.head()}")

    return output_path







       
        