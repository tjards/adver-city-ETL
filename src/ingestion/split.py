# imports
import numpy as np
import pandas as pd
from pathlib import Path

# split the labels
def split_labels(labels_path, 
                 train_ratio=0.70, 
                 val_ratio=0.15, 
                 test_ratio=0.15, 
                 seed=42):

    '''|---- train ----|---- val ----|------ test ------|
        0            train_size   train_size+val_size   end
    '''

    # enforce labels path
    if not isinstance(labels_path, Path):
        labels_path = Path(labels_path)

    # load labels from CSV
    labels_df = pd.read_csv(labels_path)
    print(f"[LOAD] Loaded {len(labels_df)} labels from: {labels_path.name}")

    # shuffle the labels with reproducible seed
    rng = np.random.RandomState(seed)
    shuffled_indices = rng.permutation(len(labels_df))

    # compute split sizes
    train_size = int(len(labels_df) * train_ratio)
    val_size = int(len(labels_df) * val_ratio)

    # split the indices (noting they are already shuffled)
    train_indices = shuffled_indices[:train_size]
    val_indices = shuffled_indices[train_size:train_size + val_size]
    test_indices = shuffled_indices[train_size + val_size:]

    # create split dataframes
    splits = {
        'train': labels_df.iloc[train_indices].reset_index(drop=True),
        'val': labels_df.iloc[val_indices].reset_index(drop=True),
        'test': labels_df.iloc[test_indices].reset_index(drop=True)
        }
    
    return splits

# build the splits
def build_splits(splits, sampled_dir, ready_dir, cleanup_sampled=False, overwrite=False):
    '''
        Creates structure:
        READY_DIR/
        ├── train/
        │   ├── rcnj_cn_s/
        │   │   ├── 1011/
        │   │   │   ├── 000060_camera0.png
        │   │   │   ├── 000060_camera1.png
        │   │   │   └── ...
        │   │   └── ...
        │   └── ...
        ├── val/
        ├── test/
        ├── train_labels.csv
        ├── val_labels.csv
        └── test_labels.csv
        
        If cleanup_sampled=True, deletes files from sampled_dir after each split is complete.
        If overwrite=False and split already exists, skips that split.
    '''

    # enforce paths
    if not isinstance(sampled_dir, Path):
        sampled_dir = Path(sampled_dir)
    if not isinstance(ready_dir, Path):
        ready_dir = Path(ready_dir)

    # create split directories
    for split_name, split_data in splits.items():

        # create split dir
        split_dir = ready_dir / split_name
        
        # check if split already exists
        if split_dir.exists() and not overwrite:
            print(f"\n[SKIP] Split '{split_name}' already exists. Use overwrite=True to rebuild.")
            continue
        
        split_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n[BUILD] Building split: {split_name} with {len(split_data)} samples")

        # map each image to split folders
        copied_count = 0
        skipped_count = 0

        # for each row in the split data
        for _, row in split_data.iterrows():

            # define source and destination paths
            src_path = sampled_dir / row['image_path']
            dest_path = split_dir / row['image_path']

            # create destination parent directories
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # copy file if source exists
            if src_path.exists():
                dest_path.write_bytes(src_path.read_bytes())
                copied_count += 1
            else:
                print(f"[WARN] Source file not found: {src_path.name}")
                skipped_count += 1

        # save split-specific labels CSV
        split_labels_path = ready_dir / f"{split_name}_labels.csv"
        split_data.to_csv(split_labels_path, index=False)
        
        print(f"[SAVE] Copied {copied_count} images (skipped {skipped_count})")
        print(f"[SAVE] Labels CSV saved to {split_labels_path.name}")

        # optionally cleanup sampled files for this split
        if cleanup_sampled:
            deleted_count = 0
            for _, row in split_data.iterrows():
                src_path = sampled_dir / row['image_path']
                if src_path.exists():
                    src_path.unlink()
                    deleted_count += 1
            print(f"[CLEANUP] Deleted {deleted_count} files from sampled_dir")
        else:
            print(f"[CLEANUP] leaving sampled data for later")