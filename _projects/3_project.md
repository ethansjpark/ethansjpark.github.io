---
layout: page
title: Reverie
description: AI-powered Dream Analysis Platform for Personalized Insights
img: assets/img/5.jpg
importance: 2
category: work
related_publications: false
---

Reverie is an AI powered dream journaling platform designed to help people reflect on their emotions and uncover meaningful patterns over time.

My team and I built Reverie as a calm and intentional space for self reflection. Rather than offering instant interpretations or clinical conclusions, the platform encourages users to slow down, record their dreams, and engage thoughtfully with AI assisted insights.

Users can securely write and revisit dream entries while exploring recurring emotional themes through structured AI analysis. The system focuses on pattern discovery and reflective summaries rather than prescriptive meaning.

Reverie is built as a full stack web application with a strong emphasis on privacy, reliability, and scalability. Dream entries are encrypted before storage, and the system remains stable even when AI services are unavailable.

The interface is intentionally minimal and calming, encouraging consistent reflection rather than constant engagement. Reverie continues to evolve with a focus on human centered design, sustainability, and responsible use of AI.

## Technologies and Structure

<div class="row">
    <div class="col-sm mt-3 mt-md-0">        
        {% include figure.liquid loading="eager" path="assets/img/reverie_structure.png" title="example image" class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">
    Reverie's technology structure
</div>

### Frontend

Next.js  
TypeScript  
Vercel

### Backend

Python  
Flask  
FastAPI  
Google Cloud Run

### AI Layer

TinyLLaMA  
LoRA fine tuning  
Hugging Face

### Database

PostgreSQL  
Google Cloud SQL

<div class="row">
    {% include figure.liquid loading="eager" path="assets/img/reverie_landing.png" title="example image" class="img-fluid rounded z-depth-1" %}
</div>
<div class="caption">
    Landing Page
</div>

<div class="row">
    {% include figure.liquid loading="eager" path="assets/img/reverie_dashboard.png" title="example image" class="img-fluid rounded z-depth-1" %}
</div>
<div class="caption">
    Dashboard Page
</div>
<div class="row">
    {% include figure.liquid loading="eager" path="assets/img/reverie_library.png" title="example image" class="img-fluid rounded z-depth-1" %}
</div>
<div class="caption">
    Dream Library Page
</div>

Reverie is now live. You can join us by clicking the logo below.

<div class="row">
    <div class="col-sm-3 mt-3 mt-md-0">
        <a href="https://reverie-ai.vercel.app/" target="_blank" rel="noopener noreferrer">
            {% include figure.liquid loading="eager" path="assets/img/reverie_logo.png" title="logo image" class="img-fluid rounded z-depth-1" %}
        </a>
        <div class="caption mt-2">
            Click our logo! 
        </div>
    </div>
</div>

If you're interested in our code, check out [Reverie](https://github.com/Reverie-Dream-Analyzer) repository! 🚀
