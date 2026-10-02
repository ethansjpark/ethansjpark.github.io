# Builds one page per entry in _data/gallery.yml (no per-photo files needed).
#   /gallery/<slug>/   slug = image filename without extension, "_" -> "-"
# Also sets `url` and `thumb` on every photo, exposes site.data.gallery_sorted (newest
# first, the order used by the listing and by Previous/Next), and writes redirect stubs
# for old URLs listed in _data/gallery_redirects.yml.
module GalleryPages
  class PhotoPage < Jekyll::PageWithoutAFile
    def initialize(site, dir, data, content = "")
      super(site, site.source, dir, "index.html")
      self.data = data
      self.content = content
    end
  end

  class Generator < Jekyll::Generator
    safe true
    priority :high

    def generate(site)
      photos = Array(site.data["gallery"])
      photos.each do |p|
        p["slug"] = File.basename(p["image"].to_s, ".*").tr("_", "-")
        p["url"] = "/gallery/#{p["slug"]}/"
        # grid thumbnail by convention: <image dir>/thumbs/<name>.jpg (bin/gallery_thumbs.py);
        # only set when the file exists, so the grid falls back to the original image
        dir, file = File.split(p["image"].to_s)
        thumb = File.join(dir, "thumbs", File.basename(file, ".*") + ".jpg")
        p["thumb"] = thumb if File.exist?(File.join(site.source, thumb.sub(%r{\A/}, "")))
      end
      # newest first; ties keep file order
      sorted = photos.each_with_index.sort_by { |p, i| [p["date"].to_s, -i] }.reverse.map(&:first)
      site.data["gallery_sorted"] = sorted

      sorted.each_with_index do |p, i|
        site.pages << PhotoPage.new(site, "gallery/#{p["slug"]}", {
          "layout" => "photo",
          "title" => p["title"],
          "photo" => p,
          "prev" => i > 0 ? sorted[i - 1] : nil,
          "next" => sorted[i + 1],
        })
      end

      by_slug = photos.to_h { |p| [p["slug"], p] }
      (site.data["gallery_redirects"] || {}).each do |old, slug|
        next unless by_slug[slug]
        to = site.baseurl.to_s + by_slug[slug]["url"]
        html = %(<!doctype html><meta charset="utf-8"><title>Redirecting…</title>) +
               %(<link rel="canonical" href="#{to}"><meta http-equiv="refresh" content="0; url=#{to}">) +
               %(<a href="#{to}">#{to}</a>\n)
        site.pages << PhotoPage.new(site, old.to_s.sub(%r{\A/}, "").chomp("/"),
                                    { "layout" => nil, "sitemap" => false }, html)
      end
    end
  end
end
