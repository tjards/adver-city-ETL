# imports 
import pandas as pd
from pathlib import Path
from data_ingestion.explore import get_agent_ids, find_imgs

def build_index(data_dir, camera = None, ext = '.png', limit = 8):

    # turn dir into a proper path
    data_path = Path(data_dir)
    
    # pull folder name
    data_name = data_path.name
    
    # expecting PREFIX_WEATHER_DENSITY
    data_name_parts = data_name.split("_")

    try:
        prefix, weather, density = data_name_parts[0], data_name_parts[1], data_name_parts[2]
    except Exception as e:
        print(f"Failed to load image: {data_name}\n{e} \n Expecting format PREFIX_WEATHER_DENSITY")
        return
    
    # get the agent ids
    agent_ids = get_agent_ids(data_dir, include_negative=False)

    rows = []

    # iterate through the agent ids 
    for agent_id in agent_ids:

        # find the images for that agent id
        agent_dir = data_path / agent_id    # short hand when using Path()
        imgs = find_imgs(agent_dir, camera=camera, ext=ext, limit=limit)

        # pull out the metadata, assuming format FRAMEID_CAMERAID.png (e.g. 000060_camera0.png)
        for img in imgs:

            # pull filename sans extension
            img_name_parts = img.stem.split("_")

            # pull frame id                           
            frame_id = int(img_name_parts[0]) if img_name_parts and img_name_parts[0].isdigit() else None

            # pull camera id
            camera_id = str(img_name_parts[1]) if img_name_parts[1] else None

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
        df = df.sort_values(["agent_id", "frame_id", "camera"]).reset_index(drop=True)

    return df










    




