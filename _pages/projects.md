---
layout: page
title: projects
permalink: /projects/
description:
nav: true
nav_order: 2
---

{% assign projects = site.projects | where_exp: 'p', 'p.published != false' | sort: 'importance' | reverse %}

<div class="pg">
  {% for project in projects %}
    {% assign logo = project.logo | default: project.img %}
    <a class="pg-cell" href="{{ project.url | relative_url }}">
      {% if logo %}
        <img class="pg-logo" src="{{ logo | relative_url }}" alt="" width="32" height="32" loading="lazy">
      {% else %}
        <span class="pg-logo pg-letter" aria-hidden="true">{{ project.title | slice: 0 | upcase }}</span>
      {% endif %}
      <span class="pg-text">
        <span class="pg-title">{{ project.title }}</span>
        <span class="pg-desc">{{ project.description }}</span>
      </span>
    </a>
  {% endfor %}
</div>
