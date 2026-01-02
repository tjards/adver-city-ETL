# imports
import subprocess
import json
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

# selectively extract specified files from a single archive
def extract_selected(archive_path, file_list, output_dir, overwrite=False):
    
    # ensure Path types
    if not isinstance(archive_path, Path):
        archive_path = Path(archive_path)
    if not isinstance(output_dir, Path):
        output_dir = Path(output_dir)
    
    # validate inputs
    if not archive_path.exists():
        raise FileNotFoundError(f"Archive not found: {archive_path}")
    
    if not file_list:
        return {"archive": archive_path.name, "extracted": 0, "errors": 0, "skipped": 0}
    
    # create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # build 7z subprocess command
    # -aoa: overwrite all existing files
    # -aos: skip all existing files
    overwrite_flag = "-aoa" if overwrite else "-aos"
    cmd = ["7z", "x", str(archive_path), f"-o{output_dir}", overwrite_flag]
    
    # add each file to extract
    for file_path in file_list:
        cmd.append(str(file_path))
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # count how many files were actually extracted vs skipped
        # 7z output includes lines like "Extracting  filename" or "Skipping  filename"
        extracted_count = result.stdout.count("Extracting  ")
        skipped_count = result.stdout.count("Skipping  ")
        
        return {
            "archive": archive_path.name,
            "extracted": extracted_count if extracted_count > 0 else len(file_list),
            "skipped": skipped_count,
            "errors": 0
        }
    except subprocess.CalledProcessError as e:
        return {
            "archive": archive_path.name,
            "extracted": 0,
            "skipped": 0,
            "errors": 1,
            "error_msg": str(e)
        }

# check if files in sample plan already exist. per archive file
def all_files_exist_for_archive(file_list, sampled_dir):
    # for each file in the list
    for file_path in file_list:
        # build its path
        full_path = sampled_dir / file_path
        # if it's not there, the sampling plan is not satisfied
        if not full_path.exists():
            print(f"some files in {full_path} missing from {sampled_dir}")
            return False
    # if all there, we don't need to re-do
    print(f"all files in {full_path} required in {sampled_dir}")
    return True

# extract all files specified in sampling plan
def extract_from_sample_plan(sample_plan_file, raw_dir, sampled_dir, overwrite=False, cleanup_raw = False):
    
    # ensure Path types
    if not isinstance(sample_plan_file, Path):
        sample_plan_file = Path(sample_plan_file)
    if not isinstance(raw_dir, Path):
        raw_dir = Path(raw_dir)
    if not isinstance(sampled_dir, Path):
        sampled_dir = Path(sampled_dir)
    
    # load sample plan
    if not sample_plan_file.exists():
        raise FileNotFoundError(f"Sample plan not found: {sample_plan_file}")
    
    with open(sample_plan_file, 'r') as f:
        sample_plan = json.load(f)
    
    # process each archive
    results = []
    total_extracted = 0
    total_skipped = 0
    total_errors = 0
    
    # for each file in the sample plan
    for archive_name, file_list in sample_plan.items():
        archive_path = raw_dir / archive_name
        
        print(f"\n{archive_name}:")
        print(f"  Files to extract: {len(file_list)}")

        # check if all files already exist in the archive
        if not overwrite and all_files_exist_for_archive(file_list=file_list, sampled_dir=sampled_dir):
            print(f" [SKIP] All files already extracted for {archive_name}")
            results.append({
                "archive": archive_name,
                "extracted": 0,
                "skipped": len(file_list),
                "errors": 0
            })
            total_skipped += len(file_list)
            continue        
        try:
            result = extract_selected(archive_path, file_list, sampled_dir, overwrite=overwrite)
            results.append(result)
            total_extracted += result["extracted"]
            total_skipped += result.get("skipped", 0)
            total_errors += result["errors"]
            
            if result["errors"] == 0:
                msg = f"[SUCCESS] Extracted {result['extracted']} files"
                if result.get("skipped", 0) > 0:
                    msg += f", skipped {result['skipped']} (already exist)"
                print(f"  {msg}")
            
                if cleanup_raw:            
                    try:
                        archive_path.unlink()
                        print(f"  [CLEANUP] Deleted raw archive: {archive_path}")
                    except Exception as e:
                        print(f"  [CLEANUP ERROR] Could not delete {archive_path}: {e}")
                else:
                    print(f"  [CLEANUP] Leaving raw archive for later.")
            
            else:
                print(f"  [ERROR] {result.get('error_msg', 'Unknown error')}")
        except FileNotFoundError as e:
            print(f"  [SKIP] {e}")
            results.append({
                "archive": archive_name,
                "extracted": 0,
                "skipped": 0,
                "error_msg": str(e)
            })
            total_errors += 1
    
    # summary
    print(f"\n{'='*50}")
    print(f"Extraction Summary:")
    print(f"  Total archives processed: {len(results)}")
    print(f"  Total files extracted: {total_extracted}")
    print(f"  Total files skipped: {total_skipped}")
    print(f"  Total errors: {total_errors}")
    print(f"{'='*50}")
    
    return {
        "total_archives": len(results),
        "total_extracted": total_extracted,
        "total_skipped": total_skipped,
        "total_errors": total_errors,
        "results": results
    }