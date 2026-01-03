# designed specifically for dataset exploration and analysis
# includes all files (images, metadata, YAML configs, etc.)

import subprocess
from pathlib import Path


def extract_archive_full(source_path, output_dir, data_format="7z"):
    
    # ensure Path types
    if not isinstance(source_path, Path):
        source_path = Path(source_path)
    if not isinstance(output_dir, Path):
        output_dir = Path(output_dir)
    
    # check if source file exists
    if not source_path.exists():
        raise FileNotFoundError(f"File not found: {source_path}")
    
    # create output directory if needed
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # determine extracted directory name
    expected_dir = output_dir / source_path.stem
    
    # skip if already extracted
    if expected_dir.exists():
        print(f"[SKIP] Already extracted:\n  {expected_dir}")
        return expected_dir
    
    # extract using 7z (full extraction)
    print(f"[EXTRACT] Extracting full archive:\n  from: {source_path}\n  to: {output_dir}")
    
    if data_format == "7z":
        subprocess.run(
            ["7z", "x", str(source_path), f"-o{output_dir}", "-y"],
            check=True
        )
    else:
        raise ValueError(f"Unsupported archive format: {data_format}")
    
    return expected_dir


def extract_archives_full(source_dir, filenames, output_dir, data_format="7z"):
    
    # ensure Path types
    if not isinstance(source_dir, Path):
        source_dir = Path(source_dir)
    if not isinstance(output_dir, Path):
        output_dir = Path(output_dir)
    
    extracted_dirs = []
    
    for filename in filenames:
        source_path = source_dir / filename
        extracted_dir = extract_archive_full(
            source_path=source_path,
            output_dir=output_dir,
            data_format=data_format
        )
        extracted_dirs.append(extracted_dir)
    
    return extracted_dirs
