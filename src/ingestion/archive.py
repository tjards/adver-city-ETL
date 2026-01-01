# imports
import subprocess
from pathlib import Path
import json

# list all files in an archive
def index_archive(archive_path):

    # ensure Path type
    if not isinstance(archive_path, Path):
        archive_path = Path(archive_path)

    # list contents of 7z
    result = subprocess.run(
        ["7z", "l", "-slt", str(archive_path)],
        capture_output=True,
        text=True,
        check=True
    )

    # parse the filenames
    files = []
    in_list = False
    for line in result.stdout.splitlines():
        
        # header separator
        if "---" in line:
            in_list = not in_list # this is a toggle on/off 
            continue

        #  if in list and not empty (line will return False if all whitespace)
        if in_list and line.strip():
            # create a list of the parts splitting on any spaces/newlines
            parts = line.split()
            if parts:
                files.append(parts[-1])  # last part is the filename
    
    return files

# build a manifest 
def build_manifest(archive_path, index_dir):

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
    files = index_archive(archive_path)

    # save
    manifest_path.write_text(json.dumps(files, indent=2))
    print(f"[SAVE] Manifest saved:\n  {manifest_path.name}")

    return files
