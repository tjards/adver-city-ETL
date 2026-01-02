import random
import json
from pathlib import Path

# filter images from manifest
def filter_manifest(files, camera=None, img_ext='.png', stride=1):

    # filter by extension
    candidates = [f for f in files if f.endswith(img_ext)] 

    # additional filter by camera, if specified
    if camera is not None:
        # specific camera name
        candidates = [f for f in candidates if camera in f]
    else:
        # else, anything called 'camera'
        candidates = [f for f in candidates if 'camera' in f] 

    # apply the stride
    return candidates[::stride]

# randomly k sample(s) from manifest
def sample_manifest(files, k, seed):

    rnd = random.Random(seed)
    
    # if fewer than k files, return all
    if len(files) <= k:
        return files
    
    # otherwise sample k files
    return rnd.sample(files, k)

# build the sampling plan
def build_sample_plan(manifests, 
                      CAMERA=None, 
                      IMG_EXT='.png', 
                      STRIDE=1, 
                      MAX_IMGS=5, 
                      SEED=42):

    # sampling plan will be stored here
    sampling_plan = {}

    for archive_name, files in manifests.items():
        
        # filter candidates from manifest
        candidates = filter_manifest(
            files, 
            camera=CAMERA, 
            img_ext=IMG_EXT, 
            stride=STRIDE
        )
        
        # sample images per archive
        sampled = sample_manifest(candidates, MAX_IMGS, seed=SEED)
        
        sampling_plan[archive_name] = sampled
        
        print(f"{archive_name}:")
        print(f"  Candidates: {len(candidates)}")
        print(f"  Sampled: {len(sampled)}\n")
    
    return sampling_plan

# save the sampling plan to JSON
def save_sample_plan(sampling_plan, output_file, overwrite=False):
  
    output_file = Path(output_file)
    
    if output_file.exists() and not overwrite:
        print(f"[SKIP] Sample plan already exists at {output_file}. Using existing plan.")
        return output_file
    
    if output_file.exists() and overwrite:
        print(f"[OVERWRITE] Overwriting existing sample plan at {output_file}")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(sampling_plan, f, indent=2)
    
    print(f"[SAVE] Sample plan saved to {output_file}")
    
    return output_file
