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

  <div class="g-view" data-view="city" hidden>
    {% assign groups = photos | group_by: "city" | sort: "name" %}
    {% for g in groups %}
    <section class="g-group">
      <h2 class="g-head">{{ g.name }}<span>{{ g.size }}</span></h2>
      <div class="g-grid">{% for p in g.items %}{% include gallery_tile.liquid p=p %}{% endfor %}</div>
    </section>
    {% endfor %}
  </div>

  <div class="g-view" data-view="series" hidden>
    {% assign groups = photos | group_by: "series" | sort: "name" %}
    {% for g in groups %}{% if g.name != "" and g.name != nil %}
    <section class="g-group">
      <h2 class="g-head">{{ g.name }}<span>{{ g.size }}</span></h2>
      <div class="g-grid">{% for p in g.items %}{% include gallery_tile.liquid p=p %}{% endfor %}</div>
    </section>
    {% endif %}{% endfor %}
    {% for g in groups %}{% if g.name == "" or g.name == nil %}
    <section class="g-group">
      <div class="g-grid">{% for p in g.items %}{% include gallery_tile.liquid p=p %}{% endfor %}</div>
    </section>
    {% endif %}{% endfor %}
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
