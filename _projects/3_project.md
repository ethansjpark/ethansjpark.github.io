---
layout: page
title: Reverie
description: AI-powered Dream Analysis Platform for Personalized Insights
img: assets/img/reverie/reverie_logo.png
importance: 3
category: work
related_publications: false
toc:
  sidebar: left
_styles: >
  article h2 {
    margin-top: 2.25rem;
  }
  article h2:first-of-type {
    margin-top: 1rem;
  }
  article table {
    margin-bottom: 1.5rem;
  }
---

Reverie is an AI powered dream journaling platform for reflecting on emotions and uncovering patterns over time.

My team and I built it as a calm, intentional space for self reflection. Rather than offering instant interpretations or clinical conclusions, it encourages users to slow down, record their dreams, and engage thoughtfully with AI assisted insights.

## Approach

Users write and revisit entries while exploring recurring emotional themes through structured analysis. The system focuses on pattern discovery and reflective summaries rather than prescriptive meaning, and the interface is deliberately minimal, encouraging consistent reflection rather than constant engagement.

## Architecture

A full stack web application built around privacy and reliability. Dream entries are encrypted before storage, and the system stays stable even when AI services are unavailable.

<div class="row">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/reverie/reverie_structure.png" alt="Reverie's technology structure, from the Next.js frontend through the Python backend and AI layer to the PostgreSQL database" title="Reverie's technology structure" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    Technology structure
</div>

## Stack

| Area     | Tools                                     |
| :------- | :---------------------------------------- |
| Frontend | Next.js, TypeScript, Vercel               |
| Backend  | Python, Flask, FastAPI, Cloud Run         |
| AI layer | TinyLLaMA, LoRA fine tuning, Hugging Face |
| Database | PostgreSQL, Google Cloud SQL              |

## Interface

<div class="row">
    {% include figure.liquid loading="eager" path="assets/img/reverie/reverie_landing.png" alt="The Reverie landing page" title="Landing page" class="img-fluid rounded z-depth-1" zoomable=true %}
</div>
<div class="caption">
    Landing page
</div>

<div class="row">
    {% include figure.liquid loading="eager" path="assets/img/reverie/reverie_dashboard.png" alt="The Reverie dashboard, showing recorded dream entries and emotional themes" title="Dashboard" class="img-fluid rounded z-depth-1" zoomable=true %}
</div>
<div class="caption">
    Dashboard
</div>

<div class="row">
    {% include figure.liquid loading="eager" path="assets/img/reverie/reverie_library.png" alt="The Reverie dream library, listing past entries for review" title="Dream library" class="img-fluid rounded z-depth-1" zoomable=true %}
</div>
<div class="caption">
    Dream library
</div>

## Live

Reverie is live. You can join us by clicking the logo below.

<div class="row">
    <div class="col-sm-3 mt-3 mt-md-0">
        <a href="https://reverie-ai.vercel.app/" target="_blank" rel="noopener noreferrer">
            {% include figure.liquid loading="eager" path="assets/img/reverie/reverie_logo.png" alt="Reverie logo, linking to the live site" title="Open Reverie" class="img-fluid rounded z-depth-1" %}
        </a>
        <div class="caption mt-2">
            Click our logo!
        </div>
    </div>
</div>

If you're interested in our code, check out [Reverie](https://github.com/Reverie-Dream-Analyzer) repository! 🚀
