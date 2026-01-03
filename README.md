# Adver-City ETL Pipeline for ML Workflows

## Overview

This project implements an **ETL (Extract, Transform, Load) pipeline** for the [Adver-City](https://labs.cs.queensu.ca/quarrg/datasets/adver-city/) synthetic dataset. The dataset is designed for investigating **cooperative perception** in autonomous vehicles.

The pipeline selectively ingests data from the [FRDR remote server](https://www.frdr-dfdr.ca/repo/dataset/3bda7692-779f-4cbd-b806-b8aa69d5dff9), extracts files based on a sampling plan, creates labels, and generates clean train/val/test splits.

Overall, this pipeline enables efficient, reproducible preparation of the Adver-City dataset for machine learning workflows.

## Key Features

- **Selective Extraction**: Only extracts images you need via a configurable sampling plan  
- **Intelligent Caching**: Cross-references existing files and skips redundant extractions  
- **Metadata Generation**: Automatically extracts weather, visibility, and time-of-day labels from labelling 
- **Reproducible Splits**: Configurable random seeds guarantee consistent train/val/test splits across runs  
- **Cleanup Options**: Optionally delete raw archives and sampled data, on the fly, to free disk space  
- **Configuration-Driven**: All parameters are set in `config.json` for easy configuration and reproducibility

## Project Structure

You will see a broader file structure to support follow-on ML workflows. Here is a high-level summary of the key directories for ETL. 

```
pytorch_project_advercity/
├── config/
│   └── config.json              # All pipeline parameters
├── data/
│   ├── raw/                     # Downloaded archives 
│   ├── index/                   # Manifests, sample plans, and labels
│   ├── sampled/                 # Selectively extracted images
│   └── ready/                   # Final train/val/test datasets
├── notebooks/
│   ├── data_ingestion_pipeline.ipynb   # Main ETL workflow
│   └── initial_explore.ipynb           # Dataset exploration
└── src/ingestion/
    ├── download.py              # File used for downloading from remote
    ├── archive.py               # Archive indexing 
    ├── sample.py                # Sampling plan generation 
    ├── extract.py               # Selective extraction 
    ├── label.py                 # Metadata and labeling 
    └── split.py                 # Train/val/test generation 
```

## Pipeline Stages

### 1. **Configure**
Define directories and load configuration from `config/config.json`.

### 2. **Download from Remote Server**
Downloaded from the Adver-City remote repository and store in `data/raw/`. 

### 3. **Develop Manifest**
Build a manifest of available images to support building a sampling plan. Stored in `data/index/{name}_manifest.json`.

### 4. **Build a Sampling Plan**
Generate a sampling based on configurable parameters:
- Specific cameras 
- Stride (e.g., every 5th frame)
- Maximum images 
- Reproducible seeds
Stored in `data/index/sampling_plan.csv`.

### 5. **Extract based on Sampling Plan**
Extract only images in the sampling plan. 
- **Optional cleanup**: Delete `data/raw/` archives after extraction to preserve disk space.

### 6. **Labelling and Metadata**
Generate a comprehensive index of labels and metadata for each extracted image:
- Weather condition (clear, fog, rain, etc.), time of day (day/night), traffic density (sparse/dense)
- Frame ID, camera ID, agent ID
- Stored in `data/index/labels.csv`.

### 7. **Generate Train/Val/Test sets**
Neatly organize into train/val/test directories. Ratios are configurable (e.g., 70/15/15). 
- **Optional cleanup**: Delete `data/sampled/` files after splitting to preserve disk space
- **Reproducibility**: Configurable seed enables identical splits across runs

### 8. **Conclusion**
The `data/ready/` directory contains the final organized dataset:
```
ready/
├── train/              # Training images 
├── val/                # Validation images 
├── test/               # Test images 
├── train_labels.csv    # Training labels
├── val_labels.csv      # Validation labels
└── test_labels.csv     # Test labels
```

## Getting Started

### Setup

- Ensure to source virtual environment located at `./venv/bin/python` before running
- Requirements have been exported using `pip freeze > requirements.txt` and are located in the root directory
- To unzip the `.7z` files ensure to install p7zip

1. **Activate virtual environment**:
   ```bash
   source ./venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Install p7zip** (if not already installed):
   ```bash
   brew install p7zip
   ```

### Configuration

All pipeline behavior is controlled via `config/config.json`. Key sections:

- **data_paths**: Local directories for data storage
- **ingestion**: Parameters for ingesting from the remote server
- **labels**: Choose which labels to sample and how they are interpreted
- **sampling**: Define other sampling parameters
- **reproducibility**: Define random seed for reproducibility

## Use

### **Run the full ETL pipeline**: 

For a complete end-to-end execution, we have created a single call as follows:

   ```bash
   python ./master_scripts/ETL_pipeline.py
   ```

When the `check_skip_option` is set to `True` in the config file, the pipeline will follow this logic:

```
Load configs
    ↓
Check: Does a sample plan exist?
    ├─ YES: Count actual sampled images vs expected in sampling plan
    │   ├─ actual ≥ expected → SKIP stages 1-4 
    │   └─ actual < expected → RUN stages 1-4
    └─ NO: RUN stages 1-4
    ↓
Run Stage 5: Generate Labels (always)
    ↓
Run Stage 6: Create Splits (always)
    ↓
Run Stage 7: Conclude (always)
```
This option is useful if you have previously run the pipeline and want to avoid re-downloading and re-sampling the data (so long as the sampling plan hasn't changed). Wrapping these conditions around Stages 1-4 also allows you to define new labels and/or change splits without repeating the earlier steps.

**Other config options**:
- `check_skip_option`: toggle the above skip logic
- `sampling.overwrite`: for a re-download and re-sample even if files exist
- `sampling.cleanup_raw_after_extract`: delete raw data after extracting samples
- `splits.cleanup_sampled_after_split`: delete sampled data after splitting

### **Explore the dataset** (optional):

Before building this pipeline, we needed to familiarize ourselves with the Adver-City dataset structure and contents. We recorded this exploration in the following notebook:

   ```
   notebooks/initial_explore.ipynb
   ```

### **Walk-through of the ETL pipeline stages** (optional):

We have provided a walk-through for using the ETL pipeline in the following notebook:


   ```
   notebooks/data_ingestion_pipeline.ipynb
   ```


