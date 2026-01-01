# imports
import subprocess
from pathlib import Path

# extract a single archive file
def extract_file(source_path, output_dir, data_format="7z"):
    
    # ensure Path types (defensive conversion)
    if not isinstance(source_path, Path):
        source_path = Path(source_path)
    if not isinstance(output_dir, Path):
        output_dir = Path(output_dir)
    
    # check if source file exists
    if not source_path.exists():
        raise FileNotFoundError(f"File not found: {source_path}")
    
    # create output directory if needed
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # determine extracted directory name (use .stem to clip extension)
    expected_dir = output_dir / source_path.stem
    
    # skip if already extracted (safety: do not overwrite)
    if expected_dir.exists():
        print(f"[SKIP] Already extracted:\n  {expected_dir}")
        return expected_dir
    
    # extract using 7z
    print(f"[EXTRACT] Extracting:\n  from: {source_path}\n  to: {output_dir}")
    
    if data_format == "7z":
        subprocess.run(
            ["7z", "x", str(source_path), f"-o{output_dir}", "-y"],
            check=True
        )
    else:
        raise ValueError(f"Unsupported archive format: {data_format}")
    
    return expected_dir

# extract multiple files efficiently
def extract_files(source_dir, filenames, output_dir, data_format="7z"):
    
    # ensure Path types (defensive conversion)
    if not isinstance(source_dir, Path):
        source_dir = Path(source_dir)
    if not isinstance(output_dir, Path):
        output_dir = Path(output_dir)
    
    # initialize
    output_dir.mkdir(parents=True, exist_ok=True)
    extracted_dirs = []
    
    # iterate through filenames
    for filename in filenames:
        try:
            # build full source path
            source_path = source_dir / filename
            # extract
            extracted_dir = extract_file(source_path, output_dir, data_format)
            extracted_dirs.append(extracted_dir)
            print(f"[EXTRACT] {filename} successful.")
        except Exception as e:
            print(f"[ERROR] {filename}: {e}")
    
    return extracted_dirs