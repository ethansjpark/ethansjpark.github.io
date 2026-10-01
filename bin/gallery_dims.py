#!/usr/bin/env python3
"""Fill missing width/height in _data/gallery.yml from the image files.

Usage: python3 bin/gallery_dims.py
Reads PNG/JPEG/GIF/WebP headers directly; no dependencies. Only touches
entries that lack width/height, and edits the file in place as text so
comments and formatting are preserved.
"""
import os, re, struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "_data", "gallery.yml")


def size(path):
    with open(path, "rb") as f:
        d = f.read(32)
        if d[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">II", d[16:24])
        if d[:6] in (b"GIF87a", b"GIF89a"):
            return struct.unpack("<HH", d[6:10])
        if d[:4] == b"RIFF" and d[8:12] == b"WEBP":
            k = d[12:16]
            if k == b"VP8X":
                return (int.from_bytes(d[24:27], "little") + 1, int.from_bytes(d[27:30], "little") + 1)
            if k == b"VP8L":
                b = int.from_bytes(d[21:25], "little")
                return ((b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1)
            if k == b"VP8 ":
                w, h = struct.unpack("<HH", d[26:30])
                return (w & 0x3FFF, h & 0x3FFF)
        if d[:2] == b"\xff\xd8":
            f.seek(2)
            orient = 1
            while True:
                b = f.read(1)
                while b and b != b"\xff":
                    b = f.read(1)
                m = f.read(1)
                while m == b"\xff":
                    m = f.read(1)
                if not m:
                    break
                m = m[0]
                if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7:
                    continue
                n = struct.unpack(">H", f.read(2))[0]
                if m == 0xE1:
                    orient = exif_orientation(f.read(n - 2)) or orient
                    continue
                if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
                    f.read(1)
                    h, w = struct.unpack(">HH", f.read(4))
                    return (h, w) if orient >= 5 else (w, h)
                f.seek(n - 2, 1)
    raise ValueError("unsupported image: " + path)


def exif_orientation(seg):
    if seg[:6] != b"Exif\0\0":
        return None
    t = seg[6:]
    e = "<" if t[:2] == b"II" else ">"
    off = struct.unpack(e + "I", t[4:8])[0]
    n = struct.unpack(e + "H", t[off:off + 2])[0]
    for i in range(n):
        ent = t[off + 2 + i * 12: off + 14 + i * 12]
        if struct.unpack(e + "H", ent[:2])[0] == 0x0112:
            return struct.unpack(e + "H", ent[8:10])[0]
    return None


def main():
    lines = open(DATA).read().split("\n")
    out, i, changed = [], 0, 0
    # split into "- " item blocks
    blocks, cur = [], []
    for ln in lines:
        if ln.startswith("- ") and cur:
            blocks.append(cur); cur = []
        cur.append(ln)
    blocks.append(cur)
    for b in blocks:
        text = "\n".join(b)
        m = re.search(r"^\s*image:\s*(\S+)", text, re.M)
        if m and not (re.search(r"^\s*width:", text, re.M) and re.search(r"^\s*height:", text, re.M)):
            w, h = size(os.path.join(ROOT, m.group(1).lstrip("/")))
            # insert after the last non-blank line of the block
            end = len(b)
            while end > 0 and not b[end - 1].strip():
                end -= 1
            b[end:end] = [f"  width: {w}", f"  height: {h}"]
            changed += 1
        out.extend(b)
    open(DATA, "w").write("\n".join(out))
    print(f"filled {changed} photo(s)")


if __name__ == "__main__":
    main()
