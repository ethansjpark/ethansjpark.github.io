---
layout: page
title: Tries
description: Financial Modeling and DCF Valuation Platform for Investors and Analysts
img: assets/img/tries/tries_logo.png
importance: 1
category: work
related_publications: false
---

Tries is a financial modeling platform built as a programmable alternative to terminals like Bloomberg and Capital IQ for generating DCF valuations.

Most of an analyst's time goes into pulling numbers from filings and vendor APIs, normalizing them, and wiring them into spreadsheets by hand. The modeling itself, the part that actually needs judgment, is a small slice of the work. Tries moves everything upstream of that judgment into infrastructure.

A user picks a company, chooses a template such as a standard DCF under an enterprise or equity framework, and sets assumptions like risk free rate and terminal growth. The system fetches canonical financial data, resolves every formula through a dependency graph, and returns computed values with full derivation lineage, so any number on the screen can be traced back to the provider field it came from. Finished analyses export to Excel, PDF, or CSV.

What makes it more than a data pipeline is that the calculation layer is polymorphic. The same logical metric, WACC for example, resolves through different equations depending on the company's industry and the chosen DCF framework, and the dependency graph reshapes itself at runtime to match.

Tries is in active development at [Polymic](https://www.linkedin.com/company/polymic-tries/about/), where I work on the ingestion, template, and export infrastructure.

<div class="row">
    {% include figure.liquid loading="eager" path="assets/img/tries/tries_landing.png" alt="The Tries landing page" title="The Tries landing page" class="img-fluid rounded z-depth-1" zoomable=true %}
</div>
<div class="caption">
    Landing Page
</div>

## Technologies and Structure

### Frontend

Next.js  
TypeScript

### Backend

FastAPI  
Python  
SQLAlchemy  
Pydantic

### Data and Infrastructure

PostgreSQL  
RDS Proxy  
ECS Fargate  
AWS Lambda  
EventBridge Scheduler  
SQS  
S3

### Hosting

AWS

## Architecture

The backend is a FastAPI application in front of PostgreSQL, split into five infrastructure subsystems. The seam between them is the canonical fact store: the refresh pipeline writes to it on a schedule, and the calculation engine reads from it on request, so ingestion can be slow and batched while resolution stays fast.

<div class="row">
    {% include figure.liquid loading="eager" path="assets/img/tries/tries_system_diagram.png" alt="Tries system architecture, showing the frontend, five backend infrastructure subsystems, and storage" title="Tries system architecture" class="img-fluid rounded z-depth-1" zoomable=true %}
</div>
<div class="caption">
    Full system architecture
</div>

### Refresh Infra

A scheduled pipeline that keeps financial data current without the request path ever waiting on a provider API. EventBridge triggers a Lambda dispatcher, which fans out one queue message per company and provider, and Fargate workers call the provider APIs and upsert the results through RDS Proxy. The workers run on Fargate rather than Lambda because a call spanning several years of statements can exceed Lambda's timeout.

<div class="row">
    {% include figure.liquid loading="eager" path="assets/img/tries/tries_refresh_infra.png" alt="Refresh pipeline from EventBridge Scheduler through a Lambda dispatcher and SQS queue to Fargate workers and RDS Proxy" title="Refresh infrastructure" class="img-fluid rounded z-depth-1" zoomable=true %}
</div>
<div class="caption">
    Refresh infrastructure
</div>

### Calculation Infra

The engine that turns a template into numbers. It discovers the dependency subgraph for the requested metrics, picks a formula variant at each polymorphic node, and evaluates in topological order so each metric is computed exactly once. Lineage trees are built afterward, which is what makes every value inspectable down to its source.

<div class="row">
    {% include figure.liquid loading="eager" path="assets/img/tries/tries_calculation_infra.png" alt="Calculation infrastructure with a graph assembler, variant resolver, calculation engine, lineage handler, and output caller" title="Calculation infrastructure" class="img-fluid rounded z-depth-1" zoomable=true %}
</div>
<div class="caption">
    Calculation infrastructure
</div>

### Data Infra

Reads go through a narrow pair of components rather than query logic scattered across services. The query builder decides what to fetch and from where, and the executioner runs it against RDS.

<div class="row">
    {% include figure.liquid loading="eager" path="assets/img/tries/tries_data_infra.png" alt="Data infrastructure with a query builder feeding a SQL executioner against RDS" title="Data infrastructure" class="img-fluid rounded z-depth-1" zoomable=true %}
</div>
<div class="caption">
    Data infrastructure
</div>

### Template Infra

Templates define what an analysis needs and how it is laid out, stored as a JSON config holding the DCF framework, the required metrics, and the section layout. The assembler validates incoming templates and extracts the metric list the engine asks for.

<div class="row">
    {% include figure.liquid loading="eager" path="assets/img/tries/tries_template_infra.png" alt="Template infrastructure taking JSON input into a template assembler" title="Template infrastructure" class="img-fluid rounded z-depth-1" zoomable=true %}
</div>
<div class="caption">
    Template infrastructure
</div>

### Output and Export Infra

Turns a resolved analysis into a file. A structure provider maps the template to a sheet layout, a file builder fills in values, and an uploader writes the artifact to S3 and records its key. Downloads are served through presigned URLs, so the bucket stays private and no file is served through the application.

<div class="row">
    {% include figure.liquid loading="eager" path="assets/img/tries/tries_output_export_infra.png" alt="Output and export infrastructure with a file builder and structure provider feeding an S3 uploader" title="Output and export infrastructure" class="img-fluid rounded z-depth-1" zoomable=true %}
</div>
<div class="caption">
    Output and export infrastructure
</div>

Tries is currently under active development

If you're interested in our code, check out [Tries](https://github.com/polymic) repository! 🚀
