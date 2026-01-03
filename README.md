# Adver-City ETL Pipeline for ML Workflows

## Overview

This project implements a production-ready **ETL (Extract, Transform, Load) pipeline** for the [Adver-City](https://labs.cs.queensu.ca/quarrg/datasets/adver-city/) synthetic dataset. The dataset is designed for investigating **cooperative perception in autonomous vehicles**—where multiple agents share sensor data to improve object detection and perception in adverse weather conditions (e.g., fog, rain, snow, etc.).

The pipeline selectively ingests data from the [FRDR remote server](https://www.frdr-dfdr.ca/repo/files/1/published/publication_1079/submitted_data), extracts files based on a sampling plan, creates labels, and generates clean train/val/test splits.

Overall, this pipeline enables efficient, reproducible preparation of the Adver-City dataset for machine learning workflows.

## Key Features

- **Selective Extraction**: Only extracts images you need via a configurable sampling plan  
- **Intelligent Caching**: Cross-references existing files and skips redundant extractions  
- **Metadata Generation**: Automatically extracts weather, visibility, and time-of-day labels from labelling 
- **Reproducible Splits**: Configurable random seeds guarantee consistent train/val/test splits across runs  
- **Cleanup Options**: Optionally delete raw archives and sampled data, on the fly, to free disk space  
- **Configuration-Driven**: All parameters are set in in `config.json` for easy configuration and reproducibility

## Project Structure

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
    ├── download.py              # file used for downloading from remote
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
- Weather condition (clear, fog, rain, etc.), time of day (day/night), traffic Density (sparse/dense)
- Frame ID, camera ID, agent ID
- Stored in `data/index/labels.csv`.

### 7. **Generate Train/Val/Test sets**
Neatly organize into train/val/test directories. Ratios are configurable (e.g., 70/15/15). 
- **Optional cleanup**: Delete `data/sampled/` files after splitting to preserve disk space
- **Reproduciblilty**: Configurable seed enables identical splits across runs

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
- requirements have been exported using `pip freeze > requirements.txt` and are located in the root directory
- to unzip the `.7z` files ensure to install p7zip

1. **Activate virtual environment**:
   ```bash
   source ./venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **I
nstall p7zip** (if not already installed):
   ```bash
   brew install p7zip
   ```

### Configuration

All pipeline behavior is controlled via `config/config.json`. Key sections:

- **data_paths**: Local directors for data storage
- **ingestion**: Parameters for ingesting from the remote server
- **labels**: Choose which labels to sample and how they are interpreted
- **sampling**: Define other sampling parameters
- **reproducibility**: Define random seed for reproducibility

## Use

**1. Explore the dataset** (optional):

Before building this pipeline, we needed to famailiarize ourselves with the Adver-City dataset structure and contents. We recorded this exploration in the following notebook:

   ```
   notebooks/initial_explore.ipynb
   ```

**2. Run the ETL pipeline**:

We have provided a walk-through for using the ETL pipeline in the following notebook:


   ```
   notebooks/data_ingestion_pipeline.ipynb
   ```


