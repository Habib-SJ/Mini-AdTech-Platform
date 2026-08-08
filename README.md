# Mini AdTech Platform

A simplified **Click-Based Advertising Platform** built with **Python** and **Django** to study the architecture and business logic behind modern AdTech systems.

Instead of focusing only on CRUD operations, this project explores how the core workflow of a real advertising platform can be designed and implemented, including campaign management, ad serving, impression and click tracking, billing, reporting, and system design decisions.

Although this project is implemented as a **Minimum Viable Product (MVP)**, the architecture is intentionally designed to be extensible so that more advanced AdTech concepts can be added incrementally without major architectural changes.

---

## Project Goals

The primary goals of this project are:

* Design the core architecture of a click-based advertising platform.
* Implement the main business workflow from campaign creation to billing.
* Practice software engineering principles, including maintainable architecture, clean code, testing, and documentation.
* Explore design decisions commonly found in large-scale AdTech systems.

---

## Core Workflow

```text
Advertiser
      │
      ▼
Campaign
      │
      ▼
Ad
      │
      ▼
Ad Selection
      │
      ▼
Publisher → Website → AdSlot
      │
      ▼
Impression
      │
      ▼
Click
      │
      ▼
Billing
      │
      ▼
Reporting & Dashboard
```

---

## Current Scope (MVP)

The current implementation focuses on the essential components of a click-based advertising platform:

* Advertiser & Publisher management
* Campaign management
* Advertisement management
* Website & AdSlot modeling
* Impression tracking
* Click tracking
* CTR & CPC calculation
* Billing foundation
* Reporting infrastructure

Several advanced capabilities—such as sophisticated ad ranking, fraud detection, targeting, distributed caching, and high-scale optimizations—are intentionally excluded from the MVP and will be explored in future iterations.

---

## Project Roadmap

* [*] Phase 0 — Repository & Project Setup
* [ ] Phase 1 — Core Models & Business Logic
* [ ] Phase 2 — Impression, Click & Billing Engine
* [ ] Phase 3 — REST API & Ad Serving
* [ ] Phase 4 — Reporting & Dashboard
* [ ] Phase 5 — Testing & Documentation
* [ ] Phase 6 — Redis, Docker & Advanced Features *(Optional)*

---

## Tech Stack

* Python
* Django
* Django REST Framework (planned)
* PostgreSQL
* Redis *(planned)*
* Docker *(planned)*

---

## Documentation

This repository contains detailed documentation describing the project's architecture, design decisions, data model, and implementation roadmap.

The goal is not only to build a working application, but also to document the engineering decisions made throughout the development process.

---

## Project Status

🚧 This project is currently under active development.

Each phase is implemented incrementally, documented, and reviewed before moving to the next stage.
