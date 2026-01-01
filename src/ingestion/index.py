# imports
import pandas as pd
from pathlib import Path
from src.utils.file_operations import get_agent_ids, find_imgs

# configs
sort_order = ["data_name", "agent_id", "frame_id", "camera", "image_path"]

# build an index from one source
def build_index(data_dir, camera=None, ext='.png', limit=8):
    
    # turn dir into a proper path
    data_path = Path(data_dir)
    
    # pull folder name
    data_name = data_path.name
    
    # expecting PREFIX_WEATHER_DENSITY
    data_name_parts = data_name.split("_")

    try:
        prefix, weather, density = data_name_parts[0], data_name_parts[1], data_name_parts[2]
    except Exception as e:
        print(f"Failed to parse directory name: {data_name}\n{e}\nExpecting format PREFIX_WEATHER_DENSITY")
        return
    
    # get the agent ids
    agent_ids = get_agent_ids(data_dir, include_negative=True)

    # initialize rows
    rows = []

    # iterate through the agent ids 
    for agent_id in agent_ids:

        # find the images for that agent id
        agent_dir = data_path / agent_id
        imgs = find_imgs(agent_dir, camera=camera, ext=ext, limit=limit)

        # parse image metadata (assuming format FRAMEID_CAMERAID.png)
        for img in imgs:

            # pull filename sans extension
            img_name_parts = img.stem.split("_")

            # pull frame id                           
            frame_id = int(img_name_parts[0]) if img_name_parts and img_name_parts[0].isdigit() else None

            # pull camera id (guard against unexpected names like "camera_01")
            camera_parts = [p for p in img_name_parts[1:] if p.lower().startswith("camera")]
            camera_id = "_".join(camera_parts) if camera_parts else None

            rows.append({
                "data_name": data_name,
                "prefix": prefix,
                "weather": weather,
                "density": density,
                "agent_id": int(agent_id),
                "frame_id": frame_id,
                "camera": camera_id,
                "image_path": str(img),
            })

    df = pd.DataFrame(rows)

    # sort the rows (if they are not empty)
    if not df.empty:
        df = df.sort_values(sort_order).reset_index(drop=True)

    return df

# build an index from multiple sources
def build_index_multi(data_dirs, camera=None, ext='.png', limit=8):
    
    # initialize index dataframe(s)
    index = []

    # iterate through directories 
    for data_dir in data_dirs:
        
        # build a dataframe (subindex)
        subindex = build_index(data_dir, camera=camera, ext=ext, limit=limit)

        # append (if there is something to append)
        if subindex is not None and not subindex.empty:
            index.append(subindex)

    # if everything is empty 
    if not index:
        # return an empty dataframe
        return pd.DataFrame() 
    
    else:
        # combine the indices into one big dataframe
        index_concat = pd.concat(index, ignore_index=True)

        # sort
        index_concat = index_concat.sort_values(sort_order).reset_index(drop=True)

        # return the concatenated dataframe
        return index_concat

# save index to file
def save_index(df, dir_out, filename, ext='.csv'):
    
    # ensure directory exists
    dir_path = Path(dir_out)
    dir_path.mkdir(parents=True, exist_ok=True)
    
    # build full path
    index_path = dir_path / f"{filename}{ext}"

    # save based on extension
    if ext == '.csv':
        df.to_csv(index_path, index=False)
        return index_path
    else:
        raise ValueError(f"Unsupported file extension: {ext} (only .csv supported for now)")
