# imports
import subprocess
from pathlib import Path
import json

# list all files in an archive
def index_archive(archive_path, mode="simple"):
    
    # ensure Path type
    archive_path = Path(archive_path)

    # list contents of 7z
    result = subprocess.run(
        ["7z", "l", "-slt", str(archive_path)],
        capture_output=True,
        text=True,
        check=True
    )

    # initialize manifest list
    files = []

    # we will temporarily hold current file record here
    current = {}

    # parse the records
    for line in result.stdout.splitlines():
        
        # clean line
        line = line.strip()

        # blank line means I am at the end of one file record, so let's assess
        if not line:

            # find the Path entry
            if "Path" in current:

                # if simple mode, just save the path string
                if mode == "simple":
                    files.append(current["Path"])

                # if not, save the whole record (verbose)
                else:  
                    files.append(current)
            
            # reset for next record
            current = {}

            # next one
            continue

        # if we're not at end of record, parse key-value pairs
        if " = " in line:
            
            # allow = to delineate key and value
            key, value = line.split(" = ", 1)
            
            # store as a dictionary entry
            current[key] = value

    # ensure to catch the last record 
    if "Path" in current:
        if mode == "simple":
            files.append(current["Path"])
        else:  
            files.append(current)

    return files



# build a manifest 
def build_manifest(archive_path, index_dir, mode="simple"):

    # ensure Path types
    if not isinstance(archive_path, Path):
        archive_path = Path(archive_path)
    if not isinstance(index_dir, Path):
        index_dir = Path(index_dir)

    # ensure index directory exists
    index_dir.mkdir(parents=True, exist_ok=True)

    # define manifest filename
    manifest_path = index_dir / f"{archive_path.stem}_manifest.json"

    # return cached manifest if it exists
    if manifest_path.exists():
        print(f"[SKIP] Manifest already exists:\n  {manifest_path.name}")
        return json.loads(manifest_path.read_text())
    
    # otherwise, index the archive
    files = index_archive(archive_path, mode)

    # save
    manifest_path.write_text(json.dumps(files, indent=2))
    print(f"[SAVE] Manifest saved:\n  {manifest_path.name}")

    return files
