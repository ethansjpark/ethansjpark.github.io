---
layout: page
permalink: /gallery/
title: gallery
nav: true
nav_order: 1
---

{% assign photos = site.data.gallery | sort: "date" | reverse %}

{% capture tiles_all %}{% for p in photos %}{% include gallery_tile.liquid p=p %}{% endfor %}{% endcapture %}

<div class="gallery">
  <div class="g-views" role="group" aria-label="View">
    <button type="button" data-view="grid" aria-pressed="true">Grid</button>
    <button type="button" data-view="list" aria-pressed="false">List</button>
    <button type="button" data-view="city" aria-pressed="false">City</button>
    <button type="button" data-view="series" aria-pressed="false">Series</button>
  </div>

  <div class="g-view" data-view="grid">
    <div class="g-grid">{{ tiles_all }}</div>
  </div>

  <div class="g-view" data-view="list" hidden>
    <ul class="g-list">
      {% for p in photos %}
      <li><a href="{{ p.url | relative_url }}"><span class="t">{{ p.title }}</span><span class="c">{{ p.city }}</span><span class="y">{{ p.date | date: "%Y" }}</span></a></li>
      {% endfor %}
    </ul>
  </div>

  {%- comment -%} City order: gallery_cities.yml first, then the rest alphabetically; case/accent-insensitive {%- endcomment -%}
  {% assign listed = "" %}{% assign listed_keys = "~" %}
  {% for c in site.data.gallery_cities %}{% include gallery_norm.liquid s=c %}{% assign listed = listed | append: norm | append: "~" | append: c | append: "|" %}{% assign listed_keys = listed_keys | append: norm | append: "~" %}{% endfor %}
  {% assign extras = "" %}{% assign extra_keys = "~" %}
  {% for p in photos %}{% include gallery_norm.liquid s=p.city %}{% assign probe = "~" | append: norm | append: "~" %}
    {% unless listed_keys contains probe or extra_keys contains probe %}{% assign extra_keys = extra_keys | append: norm | append: "~" %}{% assign extras = extras | append: norm | append: "~" | append: p.city | append: "|" %}{% endunless %}
  {% endfor %}
  {% assign ordered = listed | split: "|" %}
  {% assign extras = extras | split: "|" | sort %}
  {% assign ordered = ordered | concat: extras %}

  <div class="g-view" data-view="city" hidden>
    {% for entry in ordered %}{% assign parts = entry | split: "~" %}
    {% assign ckey = parts[0] %}{% include gallery_by_city.liquid photos=photos key=ckey %}
    {% if city_items.size > 0 %}
    <section class="g-group">
      <h2 class="g-head">{{ parts[1] }}<span>{{ city_items.size }}</span></h2>
      <div class="g-grid">{% for p in city_items %}{% include gallery_tile.liquid p=p %}{% endfor %}</div>
    </section>
    {% endif %}{% endfor %}
  </div>

  {%- comment -%} Series = "City Year", year from the same date the overlay shows {%- endcomment -%}
  <div class="g-view" data-view="series" hidden>
    {% for entry in ordered %}{% assign parts = entry | split: "~" %}{% assign c = parts[1] %}
    {% assign ckey = parts[0] %}{% include gallery_by_city.liquid photos=photos key=ckey %}{% assign items = city_items %}
    {% assign seen = "" %}
    {% for p in items %}{% assign y = p.date | date: "%Y" %}{% unless seen contains y %}{% assign seen = seen | append: y | append: "|" %}
    {% assign n = 0 %}{% for q in items %}{% assign qy = q.date | date: "%Y" %}{% if qy == y %}{% assign n = n | plus: 1 %}{% endif %}{% endfor %}
    <section class="g-group">
      <h2 class="g-head">{{ c }} {{ y }}<span>{{ n }}</span></h2>
      <div class="g-grid">{% for q in items %}{% assign qy = q.date | date: "%Y" %}{% if qy == y %}{% include gallery_tile.liquid p=q %}{% endif %}{% endfor %}</div>
    </section>
    {% endunless %}{% endfor %}
    {% endfor %}
  </div>
</div>

<script>
  (function () {
    var root = document.querySelector(".gallery");
    var btns = root.querySelectorAll(".g-views button");
    var views = root.querySelectorAll(".g-view");
    function show(name) {
      btns.forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.view === name); });
      views.forEach(function (v) { v.hidden = v.dataset.view !== name; });
    }
    btns.forEach(function (b) {
      b.addEventListener("click", function () {
        show(b.dataset.view);
        history.replaceState(null, "", "#" + b.dataset.view);
      });
    });
    var h = location.hash.slice(1);
    if (root.querySelector('.g-view[data-view="' + h + '"]')) show(h);
  })();
</script>
