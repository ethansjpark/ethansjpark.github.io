#!/usr/bin/env python3
"""Generate grid thumbnails for the photos listed in _data/gallery.yml.

Usage: python3 bin/gallery_thumbs.py [--force]

For each `image:` it writes <image dir>/thumbs/<name>.jpg (longest side 800px,
JPEG q82, EXIF rotation applied, metadata stripped). Existing thumbnails that
are newer than their source are skipped unless --force is given.

The site picks thumbnails up by that naming convention (see
_plugins/gallery-pages.rb) and falls back to the original when one is missing.
Run this after adding a photo, together with bin/gallery_dims.py, and commit the
generated files. Needs Pillow (`pip install Pillow`); the site build does not.
"""
import os
import re
import sys

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("This script needs Pillow: pip install Pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "_data", "gallery.yml")
MAX_SIDE = 800
QUALITY = 82


def thumb_path(image):
    d, f = os.path.split(image.lstrip("/"))
    return os.path.join(ROOT, d, "thumbs", os.path.splitext(f)[0] + ".jpg")


def main():
    force = "--force" in sys.argv[1:]
    images = re.findall(r"^\s*(?:- )?image:\s*(\S+)", open(DATA).read(), re.M)
    made = skipped = 0
    before = after = 0
    for image in images:
        src = os.path.join(ROOT, image.lstrip("/"))
        dst = thumb_path(image)
        if not os.path.exists(src):
            print(f"missing source: {image}")
            continue
        if not force and os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
            skipped += 1
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
            im.save(dst, "JPEG", quality=QUALITY, optimize=True, progressive=True)
        made += 1
        before += os.path.getsize(src)
        after += os.path.getsize(dst)
        print(f"{os.path.basename(dst):40s} {os.path.getsize(src)/1048576:5.2f} MB -> {os.path.getsize(dst)/1024:5.0f} KB")
    print(f"made {made}, skipped {skipped}" + (f"; {before/1048576:.1f} MB -> {after/1048576:.1f} MB" if made else ""))


if __name__ == "__main__":
    main()
