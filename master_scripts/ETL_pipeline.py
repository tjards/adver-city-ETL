# standard imports
import json
import sys
import os
import random
from pathlib import Path


# define root directory
cwd = Path.cwd()
if cwd.name == "master_scripts":
    os.chdir(cwd.parent)
    print("Changed to root directory")
else:
    print("Already in project root")

print(f"Current working directory: {Path.cwd()}") 

# Add project root to Python path
sys.path.insert(0, str(Path.cwd()))

# custom imports
from src.ingestion import download, archive, sample, extract, label, split

# check if I can skip download and sampling
def check_skip(INDEX_DIR, PLAN_FILENAME, SAMPLED_DIR, IMG_EXT):
    
    plan_path = INDEX_DIR / PLAN_FILENAME
    skip = False

    if plan_path.exists() and SAMPLED_DIR.exists():
        print("Checking if sampling plan is satisfied...\n")
        
        # Load sampling plan
        with open(plan_path, 'r') as f:
            sampling_plan = json.load(f)
        
        # Count expected images from plan
        expected_count = sum(len(files) for files in sampling_plan.values())
        
        # Count actual images in SAMPLED_DIR
        actual_files = list(SAMPLED_DIR.glob(f"**/*{IMG_EXT}"))
        actual_count = len(actual_files)
        
        if actual_count >= expected_count:
            print(f"Sample plan satisfied: counted{actual_count}/{expected_count} images")
            print("Skipping download, manifest, sampling, and extraction\n")
            skip = True
        else:
            print(f"Sample plan NOT satisfied: {actual_count}/{expected_count} images")
            print("Proceeding with full pipeline...\n")

    return skip


# main ETL pipeline
def main():

    # *******************************
    # Load configuration parameters
    # *******************************

    PROJECT_ROOT = Path.cwd()
    CONFIG_PATH = PROJECT_ROOT / "config" / "config.json"
    
    with open(CONFIG_PATH, "r") as f:
        cfg = json.load(f)
    
    # Project Descriptions
    PROJECT_NAME = cfg["project"]["name"]
    PROJECT_DESC = cfg["project"]["description"]

    # Data paths
    DATA_ROOT = PROJECT_ROOT / cfg["data_paths"]["root"]      # root directory for all data
    RAW_DIR = PROJECT_ROOT / cfg["data_paths"]["raw"]         # where the raw data is stored
    INDEX_DIR = PROJECT_ROOT / cfg["data_paths"]["index"]     # where the data index is stored
    SAMPLED_DIR = PROJECT_ROOT / cfg["data_paths"]["sampled"] # where the sampled data (i.e., subset) is stored
    READY_DIR = PROJECT_ROOT / cfg["data_paths"]["ready"]     # where the training/val/test sets are stored
    
    # Make the directories
    for p in [RAW_DIR, INDEX_DIR, SAMPLED_DIR, READY_DIR]:
        p.mkdir(parents=True, exist_ok=True)
    
    # Archive info
    BASE_URL = cfg["ingestion"]["url"]                        # remote location of data archive
    ARCHIVE_EXT = cfg["ingestion"]["archive_extension"]       # archive file extension
    MANIFEST_MODE = cfg["ingestion"]["manifest_mode"]         # mode for manifest generation (simple/verbose)
    
    # Sampling
    MAX_GB = float(cfg["ingestion"]["max_size_GB"])           # maximum file size
    MAX_IMGS = int(cfg["ingestion"]["images_per_archive"])    # maximum number of images to pull
    STRIDE = int(cfg["ingestion"]["frame_stride"])            # gaps between frames when sampling
    SEED = int(cfg["reproducibility"]["seed"])
    random.seed(SEED)
    CLEANUP_RAW = cfg["sampling"].get("cleanup_raw_after_extract", False)
    
    # Sampling plan config
    PLAN_FILENAME = cfg["sampling"]["plan_filename"]          # filename for sample plan
    PLAN_OVERWRITE = cfg["sampling"]["overwrite"]             # whether to overwrite existing plan
    LABELS_FILENAME = cfg["sampling"]["labels_filename"]      # filename for labels CSV
    
    # Image info
    CAMERA = cfg["ingestion"].get("camera", None)             # safer
    #IMG_TYPE = cfg["ingestion"]["image_type"]                 # rgb
    IMG_EXT = cfg["ingestion"]["image_extension"]             # file extension of images
    
    # Labelling info
    labels_cfg = cfg["labels"]
    
    # Training/splits info
    SPLITS_TRAIN = cfg["splits"]["train"]
    SPLITS_VAL = cfg["splits"]["val"]
    SPLITS_TEST = cfg["splits"]["test"]
    SPLITS_OVERWRITE = cfg["splits"]["overwrite"]
    CLEANUP_SAMPLED = cfg["splits"].get("cleanup_sampled_after_split", False)
    
    # The valid file types
    VALID_PREFIX = set(labels_cfg["valid_prefix"])
    VALID_WEATHER = set(labels_cfg["valid_weather"])
    VALID_DENSITY = set(labels_cfg["valid_density"])
    
    # The files I want to download
    CHOOSE_PREFIX = labels_cfg.get("choose_prefix", labels_cfg["valid_prefix"])
    CHOOSE_WEATHER = labels_cfg.get("choose_weather", labels_cfg["valid_weather"])
    CHOOSE_DENSITY = labels_cfg.get("choose_density", labels_cfg["valid_density"])
    
    # Decoders (two separate label spaces)
    DECODE_TIME = labels_cfg["weather_decode_time"]           # maps files to day/night
    DECODE_VIS = labels_cfg["weather_decode_visibility"]      # maps files to visibility conditions
    
    # Check if we can skip download and sampling
    CHECK_SKIP_OPTION = cfg["ingestion"].get("check_skip_option", False) 

    print('selected prefixes: ', CHOOSE_PREFIX)
    print('selected weather: ', CHOOSE_WEATHER)
    print('selected density: ', CHOOSE_DENSITY)

    separator = str('*'*30+'\n')

    print("\nStarting ETL pipeline...\n")
    print(f"Project: {PROJECT_NAME}\n")
    print(f"Description: {PROJECT_DESC}\n")

    # *******************************
    # 1. Download from remote server
    # *******************************

    if CHECK_SKIP_OPTION:
        skip = check_skip(INDEX_DIR, PLAN_FILENAME, SAMPLED_DIR, IMG_EXT)
    else:
        skip = False

    if not skip:

        print(separator)
        print("[1/7]: Downloading data from remote server... \n")

        filenames = download.build_filenames(
            CHOOSE_PREFIX, CHOOSE_WEATHER, CHOOSE_DENSITY,
            VALID_PREFIX, VALID_WEATHER, VALID_DENSITY,
            ARCHIVE_EXT
        )

        print(' Built the following filenames: \n', filenames)

        download_raw = download.download_files(
            base_url=BASE_URL,
            destinations_dir=RAW_DIR,
            filenames=filenames,
            timeout=60,
            max_size_GB=MAX_GB,
            overwrite=PLAN_OVERWRITE
        )
        print(' Downloaded ', len(download_raw), 'files.')
        for file in download_raw:
            print('-->', file.name)

        # *******************************
        # 2. Develop manifest 
        # *******************************

        print(separator)
        print("[2/7]: Developing manifest... \n")

        archives = sorted(RAW_DIR.glob(f"*{ARCHIVE_EXT}"))
        print(f"    Found {len(archives)} downloaded archives\n")
        
        manifests = {}
        for archive_file in archives:
            manifest = archive.build_manifest(archive_file, INDEX_DIR, mode=MANIFEST_MODE)
            manifests[archive_file.name] = manifest
            print(f"  {archive_file.name}: {len(manifest)} lines")

        print(f"\n Total manifests: {len(manifests)}")

        # *******************************
        # 3. Build sampling plan
        # *******************************

        print(separator)
        print("[3/7]: Building sampling plan... \n")

        sampling_plan = sample.build_sample_plan(
            manifests,
            CAMERA=CAMERA,
            IMG_EXT=IMG_EXT,
            STRIDE=STRIDE,
            MAX_IMGS=MAX_IMGS,
            SEED=SEED
        )

        print(f"\n Total images to extract: {sum(len(v) for v in sampling_plan.values())}")
        
        sample.save_sample_plan(
            sampling_plan,
            INDEX_DIR / PLAN_FILENAME,
            overwrite=PLAN_OVERWRITE
        )

        # *******************************
        # 4. Extract based on sampling plan
        # *******************************

        print(separator)
        print("[4/7]: Extracting based on sampling plan... \n")

        sample_plan_file = INDEX_DIR / PLAN_FILENAME
        
        _ = extract.extract_from_sample_plan(
            sample_plan_file=sample_plan_file,
            raw_dir=RAW_DIR,
            sampled_dir=SAMPLED_DIR,
            overwrite=PLAN_OVERWRITE,
            cleanup_raw=CLEANUP_RAW
        )
        
        print(f"\n Extraction complete. Location:")
        print(f"  {SAMPLED_DIR.name}/")
    
    else:
        print(" [SKIP] Skipping step #1/7: Download data from remote server\n")
        print(" [SKIP] Skipping step #2/7: Develop manifest\n")
        print(" [SKIP] Skipping step #3/7: Build sampling plan\n")
        print(" [SKIP] Skipping step #4: Extract based on sampling plan\n")

    # *******************************
    # 5. Labelling and Metadata
    # *******************************

    print(separator)
    print("[5/7]: Labelling and Metadata... \n")

    labels_data = label.build_labels_df(
        sampled_dir=SAMPLED_DIR,
        decode_time=DECODE_TIME,
        decode_vis=DECODE_VIS,
        archive_ext=ARCHIVE_EXT,
        img_ext=IMG_EXT
    )
    
    print(f"\nLabeled {len(labels_data)} images")
    
    _ = label.save_labels(
        df=labels_data,
        output_path=INDEX_DIR / LABELS_FILENAME,
    )

    # *******************************
    # 6. Generate Train/Val/Test sets
    # *******************************

    print(separator)
    print("[6/7]: Generating Train/Val/Test sets... \n")

    splits = split.split_labels(
        labels_path=INDEX_DIR / LABELS_FILENAME,
        train_ratio=SPLITS_TRAIN,
        val_ratio=SPLITS_VAL,
        test_ratio=SPLITS_TEST,
        seed=SEED
    )
    
    print(f"Train: {len(splits['train'])} images")
    print(f"Val: {len(splits['val'])} images")
    print(f"Test: {len(splits['test'])} images")
    
    split.build_splits(
        splits=splits,
        sampled_dir=SAMPLED_DIR,
        ready_dir=READY_DIR,
        cleanup_sampled=CLEANUP_SAMPLED
    )

    # *******************************
    # 7. Finish
    # *******************************

    print(separator)
    print("[7/7]: Finished... \n")

    print(f" Dataset ready for next steps at: ")
    print(f"  Train: {(READY_DIR / 'train')}/")
    print(f"  Val: {(READY_DIR / 'val')}/")
    print(f"  Test: {(READY_DIR / 'test')}/")

if __name__ == "__main__":
    main()