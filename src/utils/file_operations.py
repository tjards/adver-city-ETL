from pathlib import Path
from PIL import Image


# get agent ids
def get_agent_ids(root_dir, include_negative=True):
    
    root_dir = Path(root_dir)

    agent_ids = []
    for p in root_dir.iterdir():
        if not p.is_dir():
            continue

        name = p.name
        if not name.lstrip("-").isdigit():
            continue

        if not include_negative and name.startswith("-"):
            continue

        agent_ids.append(name)

    # sort numerically
    agent_ids.sort(key=int)
    return agent_ids

# find image
def find_imgs(root, camera=None, ext=".png", limit=5):

    # we specify the root direct
    root = Path(root)

    # if I don't specify a camera, return all
    if camera is None:
        pattern = f"*camera*{ext}"
    # else, return a specific one
    else:
        pattern = f"*{camera}*{ext}"

    if limit is None:
        # we can limit the max returns
        return sorted(root.rglob(pattern))
    else:
        return sorted(root.rglob(pattern))[:limit]
    
# list the unique images sizes
def list_image_sizes(imgs, verbose=True):

    sizes = set()

    for path in imgs:
        try:
            with Image.open(path) as img:
                sizes.add(img.size)  # (width, height)
        except Exception as e:
            print(f"Failed to read image: {path}\n{e}")

    if verbose:
        print(f"Found {len(sizes)} unique image size(s) in {len(imgs)} images:")
        for w, h in sorted(sizes):
            print(f"  {w} × {h}")

    return sizes