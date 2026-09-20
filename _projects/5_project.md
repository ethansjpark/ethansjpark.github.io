---
layout: page
title: freq-nav-sim2real
description: Frequency-Based Visual Invariance for Sim-to-Real Embodied Navigation
img: assets/img/freqnav/freqnav_card.png
importance: 2
category: work
related_publications: false
---

freq-nav-sim2real studies which parts of an image a navigation agent actually depends on, by controlling what survives in the frequency domain.

A policy trained in simulation sees clean synthetic texture, and the real world differs from it unevenly. Lighting, color cast, and material style live mostly in the low frequencies, while edges, geometry, and fine spatial detail live in the high ones. If a policy leans on the band that changes most between domains, it breaks on transfer. The question is which band it leans on, and that is answerable by removing frequencies deliberately and watching what happens.

The project uses Fourier Domain Adaptation to swap the low frequency amplitude spectrum between synthetic and real images while leaving phase intact, so an image keeps its structure but takes on the other domain's style. A separate perturbation module preserves a disc of radius r around the DC term and injects noise everywhere outside it, which makes the amount of surviving high frequency content a training parameter rather than a fixed property of the data.

The agent is a visual encoder feeding a PPO actor critic, evaluated on success rate and SPL across six conditions: a baseline with adaptation off, three cutoff radii, and two noise levels. Performance critical pieces run as C++ extensions through pybind11, covering generalized advantage estimation, the Fourier swap, the frequency perturbation, and the environment step loop, with Python fallbacks when the extensions are not built.

The results point at a sharp threshold rather than a gradual tradeoff, which is the part I found most interesting.

## Technologies and Structure

### Learning

PyTorch  
PPO actor critic  
Habitat-Sim

### Performance

C++  
pybind11

### Data and Tooling

NumPy  
OpenCV  
TensorBoard  
matplotlib  
pytest

## Results

| Condition        | Radius | Noise Std | SR   | SPL   |
| :--------------- | :----- | :-------- | :--- | :---- |
| baseline         | —      | —         | 0.96 | 0.907 |
| freq_r8          | 8      | 1.0       | 0.00 | 0.000 |
| freq_r16         | 16     | 1.0       | 1.00 | 0.929 |
| freq_r32         | 32     | 1.0       | 0.98 | 0.904 |
| freq_r16_noise05 | 16     | 0.5       | 1.00 | 1.000 |
| freq_r16_noise20 | 16     | 2.0       | 1.00 | 0.998 |

<div class="row">
    {% include figure.liquid loading="eager" path="assets/img/freqnav/freqnav_ablation_bar.png" alt="Bar chart of success rate and SPL across six frequency ablation conditions, showing total failure at radius 8" title="Success rate and SPL by condition" class="img-fluid rounded z-depth-1" zoomable=true %}
</div>
<div class="caption">
    Success rate and SPL across all six conditions
</div>

Cutting too much high frequency content is fatal. At radius 8 the agent fails every episode, timing out at the 500 step cap rather than degrading gracefully, so the detail it navigates by is genuinely gone rather than merely noisier.

Moderate perturbation does not hurt and slightly helps. Radius 16 and 32 both match or beat the baseline, which suggests that replacing some high frequency magnitude with noise during training acts as a regularizer rather than as damage.

Noise intensity matters far less than the cutoff. At radius 16, both a weak and a strong noise level reach full success and near perfect SPL, so what the policy needs is enough preserved structure, not quiet inputs.

<div class="row">
    {% include figure.liquid loading="eager" path="assets/img/freqnav/freqnav_radius_sweep.png" alt="Line plot of success rate and SPL against frequency cutoff radius, jumping from zero at radius 8 to one at radius 16" title="SR and SPL against frequency cutoff radius" class="img-fluid rounded z-depth-1" zoomable=true %}
</div>
<div class="caption">
    The sweep is a step, not a slope
</div>

The sweep is what makes the finding worth reporting. Between radius 8 and 16 the agent goes from complete failure to perfect success, so there is a critical band in that range carrying the information the policy depends on, and losing it is not a matter of degree.

These numbers come from 50k step PPO training on the mock PointNav environment, 50 evaluation episodes per condition at a fixed seed. That environment is a 2D simulator written for fast iteration, not a Habitat 3D scene, so the findings describe the frequency dependence of a policy trained there rather than a measured transfer onto real robot imagery. Extending the same ablation to Habitat scenes with real datasets is the next step.

The repository includes a 58 test pytest suite covering the Fourier swap, perturbation, GAE and PPO update, the environment, models, metrics, and plotting.

If you're interested in the code, check out [freq-nav-sim2real](https://github.com/ethansjpark/freq-nav-sim2real) on GitHub! 🚀
