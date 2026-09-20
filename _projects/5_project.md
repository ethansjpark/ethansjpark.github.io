---
layout: page
title: freq-nav-sim2real
description: Frequency-Based Visual Invariance for Sim-to-Real Embodied Navigation
img: assets/img/freqnav/freqnav_card.png
importance: 2
category: research
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

Simulated and real images differ unevenly across the spectrum: style sits in the low frequencies, geometry in the high ones. A policy leaning on the band that shifts most across domains fails on transfer, so this project locates that band by removing frequencies and watching where navigation breaks.

## Approach

Fourier Domain Adaptation swaps low frequency amplitude between domains while preserving phase, so structure survives and style transfers. A perturbation module keeps a disc of radius r around the DC term and injects noise outside it, turning surviving high frequency content into a training parameter.

## Architecture

Observations pass through both operators, then a three layer CNN encoder and a PPO actor critic. GAE, the Fourier swap, the perturbation, and the environment step loop run as C++ extensions through pybind11.

<div class="row">
    {% include figure.liquid loading="eager" path="assets/img/freqnav/freqnav_architecture.png" alt="Pipeline from simulated RGB observations through Fourier domain adaptation and frequency perturbation into a three layer CNN encoder and PPO actor critic emitting navigation actions" title="System architecture" class="img-fluid rounded z-depth-1" zoomable=true %}
</div>
<div class="caption">
    Pipeline, with the environment feedback loop
</div>

## Observations

Observations are encoded rather than photographic. The red channel carries goal proximity, and green and blue stripes carry distance and bearing.

<div class="row">
    {% include figure.liquid loading="eager" path="assets/img/freqnav/freqnav_episode_detail.png" alt="A successful 199 step episode alongside four observation frames showing the red proximity channel brightening and the bearing stripe centering as the agent reaches the goal" title="Episode walkthrough" class="img-fluid rounded z-depth-1" zoomable=true %}
</div>
<div class="caption">
    A successful episode, with its observations at four points
</div>

Those stripes are four pixels wide on a 224 pixel frame, which puts the whole goal signal high in the spectrum. Running the perturbation on a real observation shows what each cutoff costs.

<div class="row">
    {% include figure.liquid loading="eager" path="assets/img/freqnav/freqnav_method.png" alt="The same mock observation at four settings: unfiltered with crisp stripes, radius 8 where both stripes smear into the background, radius 16 where they are legible again, and radius 32 which is close to the original" title="Frequency perturbation across cutoff radii" class="img-fluid rounded z-depth-1" zoomable=true %}
</div>
<div class="caption">
    The same observation under each cutoff radius
</div>

## Stack

| Area             | Tools                                               |
| :--------------- | :-------------------------------------------------- |
| Learning         | PyTorch, PPO actor critic, Habitat-Sim, Habitat-Lab |
| Performance      | C++, pybind11                                       |
| Data and tooling | NumPy, OpenCV, TensorBoard, matplotlib, pytest      |

## Results

Six conditions in the mock environment, each trained 50k steps and evaluated over 50 episodes at a fixed seed. SR is success rate; SPL weights success by how efficient the path was.

| Condition        | Radius | Noise Std | SR   | SPL   |
| :--------------- | :----- | :-------- | :--- | :---- |
| baseline         | —      | —         | 0.96 | 0.907 |
| freq_r8          | 8      | 1.0       | 0.00 | 0.000 |
| freq_r16         | 16     | 1.0       | 1.00 | 0.929 |
| freq_r32         | 32     | 1.0       | 0.98 | 0.904 |
| freq_r16_noise05 | 16     | 0.5       | 1.00 | 1.000 |
| freq_r16_noise20 | 16     | 2.0       | 1.00 | 0.998 |

<div class="row">
    {% include figure.liquid loading="eager" path="assets/img/freqnav/freqnav_ablation_results.png" alt="Bar chart of success rate and SPL across six frequency ablation conditions, showing total failure at radius 8 and full success from radius 16 onward" title="Success rate and SPL by condition" class="img-fluid rounded z-depth-1" zoomable=true %}
</div>
<div class="caption">
    Success rate and SPL across all six conditions
</div>

At radius 8 the agent fails every episode, running to the step cap rather than degrading. At 16 and 32 it matches or beats the baseline, so noise in place of high frequency magnitude regularizes rather than damages. Intensity barely matters: at radius 16, weak and strong noise both reach full success.

## Threshold

<div class="row">
    {% include figure.liquid loading="eager" path="assets/img/freqnav/freqnav_radius_sweep.png" alt="Line plot of success rate and SPL against frequency cutoff radius, jumping from zero at radius 8 to one at radius 16, with the critical band shaded" title="SR and SPL against frequency cutoff radius" class="img-fluid rounded z-depth-1" zoomable=true %}
</div>
<div class="caption">
    The sweep is a step, not a slope
</div>

The transition is discontinuous. Between radius 8 and 16 the agent goes from total failure to perfect success, placing the critical band in that range.

## Habitat Validation

The same six conditions then ran in Habitat-Sim on reconstructed real scenes, at 200k steps with shaped rewards.

<div class="row">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/freqnav/freqnav_scene_apartment.jpg" alt="Agent-perspective render of a reconstructed apartment interior in Habitat-Sim" title="Apartment scene" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/freqnav/freqnav_scene_castle.jpg" alt="Agent-perspective render of a hall in Skokloster Castle, with paintings and period furniture" title="Skokloster Castle scene" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/freqnav/freqnav_scene_vangogh.jpg" alt="Agent-perspective render of the Van Gogh room scene" title="Van Gogh room scene" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    Agent-perspective renders from the three Habitat-Sim test scenes
</div>

Photorealistic geometry and lighting replace the encoded stripes, so the frequency content the policy reads is now ordinary scene structure rather than a synthetic signal.

<div class="row">
    {% include figure.liquid loading="eager" path="assets/img/freqnav/freqnav_habitat_comparison.png" alt="Two panel comparison: mock environment success rate above, Habitat-Sim mean return below, showing the same ordering across conditions" title="Mock to 3D transfer validation" class="img-fluid rounded z-depth-1" zoomable=true %}
</div>
<div class="caption">
    Mock success rate above, Habitat mean return below
</div>

| Condition        | Radius | Noise Std | Mean Return |
| :--------------- | :----- | :-------- | :---------- |
| baseline         | —      | —         | −4.83       |
| freq_r8          | 8      | 1.0       | −5.65       |
| freq_r16         | 16     | 1.0       | −5.00       |
| freq_r32         | 32     | 1.0       | −5.00       |
| freq_r16_noise05 | 16     | 0.5       | −5.00       |
| freq_r16_noise20 | 16     | 2.0       | −6.62       |

No condition reaches a goal here. Every episode runs to the 500 step cap, so success rate and SPL are zero throughout and shaped return is the only signal separating conditions: a small CNN at 200k steps does not solve real PointNav.

Within that signal the mock ordering reappears. Radius 8 falls below baseline, the strongest noise setting is worst of all, and r=16, r=32 and the low noise variant sit together at −5.00. The frequency sensitivity survives the change of environment even though absolute performance does not.

The repository carries a 91 test suite covering the Fourier swap, the perturbation, GAE and the PPO update, both environments, the models, metrics, and plotting.

If you're interested in the code, check out [freq-nav-sim2real](https://github.com/ethansjpark/freq-nav-sim2real) on GitHub! 🚀
