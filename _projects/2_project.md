---
layout: page
title: MEDi
description: AI-driven medication detection platform
img: assets/img/medi/medi_logo.jpg
importance: 4
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

MEDi is an AI-driven platform that helps visually impaired shoppers identify pharmaceutical products in stores, so that medication is not taken by mistake.

My team and I launched it in February 2025.

## Approach

Rather than broad assistance, MEDi gives a step-by-step shopping guide built on hand-tracking and object detection, so the guidance follows where the user is actually reaching. Audible recognition carries the same information without requiring the screen.

## Stack

| Area       | Tools                               |
| :--------- | :---------------------------------- |
| App        | Kotlin, Android                     |
| On-device  | TensorFlow Lite, MediaPipe          |
| Optimizing | Model quantization for edge devices |

Running inference on the device rather than in the cloud is what keeps the guidance responsive enough to follow a hand in real time, and quantization is what makes the models small enough to do it.

## Interface

<div class="row">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/medi/medi_ix1.jpg" alt="MEDi app interface screen" title="MEDi interface" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/medi/medi_ix2.jpg" alt="MEDi app interface screen" title="MEDi interface" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/medi/medi_ix3.jpg" alt="MEDi app interface screen" title="MEDi interface" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    UI walkthrough
</div>

<div class="row">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/medi/med_try1.jpg" alt="MEDi camera view detecting a pharmaceutical product on a shelf" title="Camera interface" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/medi/med_try2.jpg" alt="MEDi camera view detecting a pharmaceutical product on a shelf" title="Camera interface" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/medi/med_try3.jpg" alt="MEDi camera view detecting a pharmaceutical product on a shelf" title="Camera interface" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    Camera integrated interface
</div>

## Status

MEDi is in beta testing. You can join us by clicking the logo below.

<div class="row">
    <div class="col-sm-3 mt-3 mt-md-0">
        <a href="https://play.google.com/apps/testing/com.MedI" target="_blank" rel="noopener noreferrer">
            {% include figure.liquid loading="eager" path="assets/img/medi/medi_logo.jpg" alt="MEDi logo, linking to the Play Store beta" title="Join the MEDi beta" class="img-fluid rounded z-depth-1" %}
        </a>
        <div class="caption mt-2">
            Click our logo!
        </div>
    </div>
</div>

If you're interested in our code, check out [MEDi's GitHub](https://github.com/2nd-Company/MEDi) repository! 🚀
