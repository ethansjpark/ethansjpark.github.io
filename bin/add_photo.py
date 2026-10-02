#!/usr/bin/env python3
"""Add a photo to the gallery in one step.

Copies the image into assets/img/photo/<slug>.<ext> (the original is left
untouched), appends its entry (title, city, date, image, width, height) to the
end of _data/gallery.yml, and makes its grid thumbnail. Width/height come from
bin/gallery_dims.py and the thumbnail from bin/gallery_thumbs.py.

  title  defaults to the file name, tidied ("IMG_0042.jpg" -> "img 0042")
  date   defaults to the EXIF DateTimeOriginal, then the file's modified time
  city   --city, else (with --geocode) the place at the photo's GPS position,
         else asked interactively. It is matched against _data/gallery_cities.yml
         ignoring case and accents, so the listed spelling is used.

Privacy: if the image carries GPS data the script says so, because publishing it
exposes where the photo was taken, and asks before continuing (or pass --yes).
--strip-gps removes only the GPS tags from the published copy: losslessly for
JPEG (the image data is copied byte for byte), by a high-quality re-encode for
other formats. It also reports which photos already in assets/img/photo/ still
contain GPS data, without changing them.

Network: none, except with --geocode, which sends one request to
nominatim.openstreetmap.org (OpenStreetMap Nominatim reverse geocoding) with only
the photo's coordinates, rounded to 3 decimals (about 100 m). No retries.

Pillow (pip install Pillow) is used for the thumbnail and for non-JPEG files; JPEG
EXIF is read without it. Without Pillow the photo is still added and the script
tells you to run bin/gallery_thumbs.py later.
"""
import argparse
import datetime
import glob
import json
import os
import re
import struct
import sys
import tempfile
import urllib.parse

sys.dont_write_bytecode = True  # importing the helpers below must not leave bin/__pycache__
import sitelib
from sitelib import ROOT, die, warn, rel, fold, slugify, yaml_scalar

import gallery_dims

DATA = os.path.join(ROOT, "_data", "gallery.yml")
CITIES = os.path.join(ROOT, "_data", "gallery_cities.yml")
PHOTO_DIR = os.path.join(ROOT, "assets", "img", "photo")
EXTS = {".jpg": ".jpg", ".jpeg": ".jpg", ".png": ".png", ".webp": ".webp", ".gif": ".gif"}
NOMINATIM = "https://nominatim.openstreetmap.org/reverse"

try:
    from PIL import Image
except ImportError:
    Image = None


# ---------------------------------------------------------------- EXIF (JPEG, stdlib)

TYPE_SIZE = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 7: 1, 9: 4, 10: 8}
XMP_ID = b"http://ns.adobe.com/xap/1.0/\0"


def jpeg_segments(data):
    """Yield (marker, start, end, payload_start) for each segment before the scan."""
    if data[:2] != b"\xff\xd8":
        raise ValueError("not a JPEG")
    i = 2
    while i + 4 <= len(data):
        if data[i] != 0xFF:
            raise ValueError("corrupt JPEG marker stream")
        m = data[i + 1]
        if m == 0xFF:
            i += 1
            continue
        if m in (0x01,) or 0xD0 <= m <= 0xD7:
            i += 2
            continue
        n = struct.unpack(">H", data[i + 2:i + 4])[0]
        yield m, i, i + 2 + n, i + 4
        if m == 0xDA:  # start of scan: image data follows
            return
        i += 2 + n


class Tiff:
    def __init__(self, buf):
        self.b = buf
        self.e = "<" if buf[:2] == b"II" else ">"
        if buf[:2] not in (b"II", b"MM"):
            raise ValueError("bad TIFF header")

    def u16(self, o):
        return struct.unpack(self.e + "H", self.b[o:o + 2])[0]

    def u32(self, o):
        return struct.unpack(self.e + "I", self.b[o:o + 4])[0]

    def ifd(self, off):
        """{tag: (type, count, value_offset, entry_offset)}"""
        out = {}
        if not off or off + 2 > len(self.b):
            return out
        for k in range(self.u16(off)):
            p = off + 2 + 12 * k
            if p + 12 > len(self.b):
                break
            tag, typ, cnt = self.u16(p), self.u16(p + 2), self.u32(p + 4)
            size = TYPE_SIZE.get(typ, 1) * cnt
            out[tag] = (typ, cnt, p + 8 if size <= 4 else self.u32(p + 8), p)
        return out

    def ascii(self, ent):
        typ, cnt, vo, _ = ent
        return self.b[vo:vo + cnt].split(b"\0")[0].decode("ascii", "replace")

    def rationals(self, ent):
        typ, cnt, vo, _ = ent
        vals = []
        for k in range(cnt):
            num, den = self.u32(vo + 8 * k), self.u32(vo + 8 * k + 4)
            vals.append(num / den if den else 0.0)
        return vals


def jpeg_meta(data):
    """{'date', 'gps_tags', 'latlon', 'xmp_gps'} from a JPEG's EXIF/XMP."""
    meta = {"date": None, "gps_tags": 0, "latlon": None, "xmp_gps": False}
    for m, s, e, p in jpeg_segments(data):
        if m != 0xE1:
            continue
        if data[p:p + 6] == b"Exif\0\0":
            t = Tiff(data[p + 6:e])
            ifd0 = t.ifd(t.u32(4))
            if 0x8769 in ifd0:
                ex = t.ifd(t.u32(ifd0[0x8769][2]))
                if 0x9003 in ex:
                    meta["date"] = t.ascii(ex[0x9003])
            if 0x8825 in ifd0:
                gps = t.ifd(t.u32(ifd0[0x8825][2]))
                meta["gps_tags"] = len(gps)
                if 2 in gps and 4 in gps:
                    lat, lon = (sum(v / 60 ** i for i, v in enumerate(t.rationals(gps[k]))) for k in (2, 4))
                    if 1 in gps and t.ascii(gps[1]).upper().startswith("S"):
                        lat = -lat
                    if 3 in gps and t.ascii(gps[3]).upper().startswith("W"):
                        lon = -lon
                    if lat or lon:
                        meta["latlon"] = (lat, lon)
        elif data[p:p + len(XMP_ID)] == XMP_ID and re.search(rb"GPS(Latitude|Longitude)", data[p:e]):
            meta["xmp_gps"] = True
    return meta


def jpeg_strip_gps(data):
    """Return the JPEG with the GPS IFD emptied (zeroed in place, same length, so no other
    offset moves) and any XMP packet holding GPS removed. Image data is untouched."""
    out = bytearray(data)
    drop = []
    for m, s, e, p in jpeg_segments(data):
        if m != 0xE1:
            continue
        if data[p:p + 6] == b"Exif\0\0":
            base = p + 6
            t = Tiff(data[base:e])
            ifd0 = t.ifd(t.u32(4))
            if 0x8825 not in ifd0:
                continue
            goff = t.u32(ifd0[0x8825][2])
            gps = t.ifd(goff)
            for typ, cnt, vo, ep in gps.values():
                size = TYPE_SIZE.get(typ, 1) * cnt
                if size > 4:
                    out[base + vo:base + vo + size] = bytes(size)
                out[base + ep:base + ep + 12] = bytes(12)
            n = t.u16(goff)
            out[base + goff:base + goff + 2] = bytes(2)  # entry count 0
            nxt = base + goff + 2 + 12 * n
            out[nxt:nxt + 4] = bytes(4)  # old next-IFD pointer
        elif data[p:p + len(XMP_ID)] == XMP_ID and re.search(rb"GPS(Latitude|Longitude)", data[p:e]):
            drop.append((s, e))
    for s, e in reversed(drop):
        del out[s:e]
    return bytes(out)


def pil_meta(path):
    meta = {"date": None, "gps_tags": 0, "latlon": None, "xmp_gps": False}
    with Image.open(path) as im:
        exif = im.getexif()
        meta["date"] = exif.get_ifd(0x8769).get(0x9003)
        gps = exif.get_ifd(0x8825)
        meta["gps_tags"] = len(gps)
        try:
            lat = sum(float(v) / 60 ** i for i, v in enumerate(gps[2]))
            lon = sum(float(v) / 60 ** i for i, v in enumerate(gps[4]))
            lat = -lat if str(gps.get(1, "N")).upper().startswith("S") else lat
            lon = -lon if str(gps.get(3, "E")).upper().startswith("W") else lon
            meta["latlon"] = (lat, lon) if (lat or lon) else None
        except (KeyError, TypeError, ValueError):
            pass
        xmp = im.info.get("xmp") or b""
        meta["xmp_gps"] = bool(re.search(rb"GPS(Latitude|Longitude)", xmp if isinstance(xmp, bytes) else xmp.encode()))
    return meta


def read_meta(path):
    """Metadata, or None when it can't be read (non-JPEG without Pillow)."""
    with open(path, "rb") as f:
        head = f.read(2)
    if head == b"\xff\xd8":
        with open(path, "rb") as f:
            return jpeg_meta(f.read())
    if Image is None:
        return None
    return pil_meta(path)


def has_gps(meta):
    return bool(meta and (meta["gps_tags"] or meta["xmp_gps"]))


def stripped_copy(src, ext):
    """(bytes, how) for the published copy without GPS."""
    data = open(src, "rb").read()
    if data[:2] == b"\xff\xd8":
        return jpeg_strip_gps(data), "lossless: GPS tags removed, image data copied unchanged"
    if Image is None:
        die("removing GPS from a non-JPEG file needs Pillow: pip install Pillow")
    import io
    with Image.open(src) as im:
        exif = im.getexif()
        exif.pop(0x8825, None)
        buf = io.BytesIO()
        fmt = {".png": "PNG", ".webp": "WEBP", ".gif": "GIF"}[ext]
        opts = {"exif": exif.tobytes()} if fmt != "GIF" else {}
        if fmt == "WEBP":
            opts.update(quality=95, method=6)
        im.save(buf, fmt, **opts)
    how = "re-encoded as WebP at quality 95 (could not be done losslessly)" if fmt == "WEBP" else f"re-saved as {fmt} without GPS (lossless)"
    return buf.getvalue(), how


def gps_report():
    files = sorted(f for f in glob.glob(os.path.join(PHOTO_DIR, "*")) if os.path.isfile(f))
    found, unknown = [], []
    for f in files:
        try:
            meta = read_meta(f)
        except Exception:
            meta = None
        if meta is None:
            unknown.append(os.path.basename(f))
        elif has_gps(meta):
            found.append(os.path.basename(f) + ("" if meta["latlon"] else " (GPS tags, no position)"))
    msg = f"GPS report: {len(found)} of {len(files)} photos in {rel(PHOTO_DIR)}/ contain GPS data"
    print(msg + (": " + ", ".join(found) if found else "."))
    if unknown:
        print(f"  could not check {len(unknown)} (install Pillow): {', '.join(unknown)}")
    print("  (report only; nothing changed. Thumbnails carry no metadata.)")


# ---------------------------------------------------------------- city

def listed_cities():
    return [ln[2:].strip() for ln in open(CITIES, encoding="utf-8") if ln.startswith("- ")]


def used_cities(text):
    counts = {}
    for c in re.findall(r"^\s*city:\s*(.+?)\s*$", text, re.M):
        c = c.strip("\"'")
        counts[c] = counts.get(c, 0) + 1
    return counts


def normalize_city(city, used):
    city = " ".join(city.split())
    for c in listed_cities():
        if fold(c) == fold(city):
            return c
    for c in used:
        if fold(c) == fold(city):
            warn(f"city '{c}' is used in gallery.yml but is not in {rel(CITIES)}; it will sort after the listed cities")
            return c
    warn(f"'{city}' is a new city, not in {rel(CITIES)}; add it there to control its position in the City view")
    return city


def geocode(latlon):
    lat, lon = (round(v, 3) for v in latlon)
    q = urllib.parse.urlencode({"format": "jsonv2", "lat": lat, "lon": lon, "zoom": 10, "accept-language": "en"})
    print(f"geocoding ({lat}, {lon}) with nominatim.openstreetmap.org ...")
    status, body = sitelib.http_get(f"{NOMINATIM}?{q}", accept="application/json")
    if status != 200:
        raise ConnectionError(f"nominatim.openstreetmap.org returned HTTP {status}")
    addr = json.loads(body).get("address", {})
    for k in ("city", "town", "village", "municipality", "county", "state"):
        if addr.get(k):
            return addr[k]
    raise ConnectionError("nominatim.openstreetmap.org returned no place name")



# ---------------------------------------------------------------- main

def tidy_title(path):
    stem = os.path.splitext(os.path.basename(path))[0]
    return " ".join(re.sub(r"[_\-.]+", " ", stem).split()).lower()


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Network: only with --geocode, one request to nominatim.openstreetmap.org (coordinates only).",
    )
    ap.add_argument("image", help="path to the photo (JPEG, PNG, WebP or GIF)")
    ap.add_argument("--title", help="title (default: the file name, tidied); its slug is the file name")
    ap.add_argument("--city", help="city (matched against _data/gallery_cities.yml)")
    ap.add_argument("--date", help="YYYY-MM-DD (default: EXIF DateTimeOriginal, then file modified time)")
    ap.add_argument("--yes", action="store_true", help="don't ask: publish even if the image has GPS data")
    ap.add_argument("--strip-gps", action="store_true", help="remove GPS tags from the published copy (original untouched)")
    ap.add_argument("--geocode", action="store_true",
                    help="if no --city, look the city up from the EXIF GPS via nominatim.openstreetmap.org (sends only the coordinates)")
    ap.add_argument("--dry-run", action="store_true", help="print what would change and write nothing")
    a = ap.parse_args()

    src = a.image
    if not os.path.isfile(src):
        die(f"no such file: {src}")
    ext = EXTS.get(os.path.splitext(src)[1].lower())
    if not ext:
        die(f"unsupported image type {os.path.splitext(src)[1] or '(none)'}; use JPEG, PNG, WebP or GIF")
    text = open(DATA, encoding="utf-8").read()

    # title and file name
    title = " ".join((a.title if a.title is not None else tidy_title(src)).split())
    slug = slugify(title)
    if not slug:
        die("the title is empty or has no letters or digits to make a file name from")
    dest = os.path.join(PHOTO_DIR, slug + ext)
    image = "/" + rel(dest).replace(os.sep, "/")
    page_slug = slug.replace("_", "-")
    taken = [f for f in os.listdir(PHOTO_DIR) if os.path.splitext(f)[0].lower() == slug]
    if taken:
        die(f"{rel(PHOTO_DIR)}/{taken[0]} already exists; choose another --title")
    for img in re.findall(r"^\s*(?:- )?image:\s*(\S+)", text, re.M):
        if os.path.splitext(os.path.basename(img))[0].replace("_", "-").lower() == page_slug:
            die(f"gallery.yml already has a photo with slug '{page_slug}' ({img}); choose another --title")
    thumb = os.path.join(PHOTO_DIR, "thumbs", slug + ".jpg")
    if os.path.exists(thumb):
        die(f"{rel(thumb)} already exists; not overwriting")

    # metadata
    try:
        meta = read_meta(src)
    except Exception as e:
        die(f"could not read {src}: {e}")
    if meta is None:
        warn("Pillow is not installed, so EXIF date and GPS of this non-JPEG file can't be read")

    # date
    if a.date:
        try:
            date = datetime.date.fromisoformat(a.date).isoformat()
        except ValueError:
            die(f"--date must be YYYY-MM-DD, got '{a.date}'")
    elif meta and meta["date"] and re.match(r"\d{4}:\d\d:\d\d", meta["date"]):
        date = meta["date"][:10].replace(":", "-")
        print(f"date: {date} (EXIF DateTimeOriginal)")
    else:
        date = datetime.date.fromtimestamp(os.path.getmtime(src)).isoformat()
        print(f"date: {date} (no EXIF date; used the file's modified time; pass --date to change it)")

    # privacy
    gps = has_gps(meta)
    if gps:
        where = "at %.5f, %.5f" % meta["latlon"] if meta["latlon"] else "(GPS tags, no position)"
        print(f"PRIVACY: {src} contains GPS data {where}.")
        if a.strip_gps:
            print("  --strip-gps: the published copy will have the GPS tags removed.")
        else:
            print("  Publishing it exposes exactly where the photo was taken. Use --strip-gps to remove it.")
    elif meta is None:
        print("PRIVACY: GPS data could not be checked (install Pillow).")
    else:
        print("privacy: no GPS data in this image.")
    gps_report()

    # city
    used = used_cities(text)
    city = a.city
    if not city and a.geocode:
        if meta and meta["latlon"]:
            try:
                city = geocode(meta["latlon"])
                print(f"city from GPS: {city}")
            except (ConnectionError, ValueError) as e:
                warn(f"geocoding failed ({e}); asking instead")
        else:
            warn("--geocode: the image has no GPS position; asking instead")
    if not city:
        if not sitelib.is_tty():
            die("no city: pass --city (or --geocode for a photo with GPS)")
        order = sorted(used, key=lambda c: -used[c])
        print("cities in gallery.yml: " + ", ".join(f"{c} ({used[c]})" for c in order))
        city = sitelib.ask("city: ").strip()
        if not city:
            die("no city given")
    city = normalize_city(city, used)

    # confirm publishing a location
    risky = (gps or meta is None) and not a.strip_gps
    if risky and not a.yes and not a.dry_run:
        if not sitelib.is_tty():
            die("the image may contain its GPS location; pass --strip-gps to remove it or --yes to publish as is")
        if sitelib.ask("publish with the location data? [y/N] ").strip().lower() not in ("y", "yes"):
            die("stopped; nothing written (try --strip-gps)")

    # published bytes and size
    if a.strip_gps and gps:
        data, how = stripped_copy(src, ext)
    else:
        data, how = None, "copied unchanged"
    with tempfile.TemporaryDirectory() as tmp:
        probe = src
        if data is not None:
            probe = os.path.join(tmp, "probe" + ext)
            open(probe, "wb").write(data)
            if has_gps(read_meta(probe)):
                die("GPS data is still present after stripping; nothing written")
        try:
            w, h = gallery_dims.size(probe)
        except Exception as e:
            die(f"could not read the image size: {e}")

    entry = (f"- title: {yaml_scalar(title)}\n  city: {yaml_scalar(city)}\n  date: {date}\n"
             f"  image: {image}\n  width: {w}\n  height: {h}\n")

    tag = "would " if a.dry_run else ""
    print()
    print(f"{tag}create {rel(dest)} ({how})")
    print(f"{tag}append to {rel(DATA)}:")
    print("".join("    " + ln + "\n" for ln in entry.rstrip("\n").split("\n")), end="")
    print(f"{tag}create {rel(thumb)}" + ("" if Image else " -- skipped: needs Pillow"))
    if a.dry_run:
        print("dry run: nothing written")
        return

    # write: image, entry, thumbnail
    if data is None:
        data = open(src, "rb").read()
    sitelib.write_new(dest, data, False)
    st = os.stat(src)
    os.utime(dest, (st.st_atime, st.st_mtime))
    sitelib.append_text(DATA, entry, False)
    made_thumb = make_thumb(image)

    print()
    print(f"added '{title}' ({city}, {date}): {rel(dest)}, entry in {rel(DATA)}" + (f", {rel(thumb)}" if made_thumb else ""))
    print(f"page: /gallery/{page_slug}/")
    print(f"next: review, then git add {rel(dest)} {rel(DATA)}" + (f" {rel(thumb)}" if made_thumb else "") + " && git commit, and push")
    if not made_thumb:
        print("      and after installing Pillow run: python3 bin/gallery_thumbs.py")


def make_thumb(image):
    """Make this one photo's thumbnail with bin/gallery_thumbs.py's own code."""
    try:
        import gallery_thumbs
    except SystemExit:
        warn("Pillow is not installed; thumbnail not made")
        return False
    with tempfile.TemporaryDirectory() as tmp:
        one = os.path.join(tmp, "gallery.yml")
        open(one, "w").write(f"- image: {image}\n")
        saved, gallery_thumbs.DATA = gallery_thumbs.DATA, one
        argv, sys.argv = sys.argv, sys.argv[:1]
        try:
            gallery_thumbs.main()
        finally:
            gallery_thumbs.DATA, sys.argv = saved, argv
    return os.path.exists(gallery_thumbs.thumb_path(image))


if __name__ == "__main__":
    main()
