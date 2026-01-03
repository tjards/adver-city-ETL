# imports
import numpy as np
import pandas as pd
from pathlib import Path

# split the labels
def split_labels(labels_path, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15):

    '''|---- train ----|---- val ----|------ test ------|
        0            train_size   train_size+val_size   end
    '''

    # enforce labels path
    if not isinstance(labels_path, Path):
        labels_path = Path(labels_path)

    # load labels from CSV
    labels_df = pd.read_csv(labels_path)
    print(f"[LOAD] Loaded {len(labels_df)} labels from: {labels_path}")

    # shuffle the labels
    shuffled_indices = np.random.permutation(len(labels_df))

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
def build_splits():
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
    '''
    pass 