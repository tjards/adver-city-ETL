from directory_tree import DisplayTree
from PIL import Image
import random
import matplotlib.pyplot as plt

# print the folder tree
def print_folder_tree(root_dir, max_depth=1):

    # configuration
    config_tree = {
        # specify starting path 
        "dirPath": root_dir,
        # set False to include both files and directories
        "onlyDirs": False,
        # set maximum depth for tree
        "maxDepth": max_depth,
        # specify sorting option (100 = no specific sort)
        "sortBy": 100,
    }
    # create and display tree
    DisplayTree(**config_tree)

# show image
def show_image(path, title=None, figsize = (6,6)):
    try:
        img = Image.open(path).convert("RGB")
    except Exception as e:
        print(f"Failed to load image: {path}\n{e}")
        return

    plt.figure(figsize=figsize)
    plt.imshow(img)
    plt.axis("off")
    if title:
        plt.title(title)
    else:
        plt.title(f"{img.size[0]}x{img.size[1]}")
    plt.show()

# show images as a grid
def show_images_grid(imgs, rows=2, cols=3, randomize = True, seed=None):
    n = rows * cols

    if not imgs:
        print("No images to show.")
        return

    if randomize:
        if seed is not None:
            random.seed(seed)
        imgs = random.sample(imgs, min(n, len(imgs)))
    else:
        imgs = imgs[:n]

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 4))
    axes = axes.flatten()

    for ax, path in zip(axes, imgs):
        img = Image.open(path).convert("RGB")
        ax.imshow(img)
        ax.set_title(f"{img.size[0]} × {img.size[1]}", fontsize=10)
        ax.axis("off")

    # turn off unused axes
    for ax in axes[len(imgs):]:
        ax.axis("off")

    plt.tight_layout()
    plt.show()