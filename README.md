# AgriFore — Agricultural Forecasting and Market Intelligence Platform

AgriFore is a data-driven agricultural forecasting and analytics platform built around crop production, weather, and market data for Telangana, with Kamareddy used as a district-level modeling case. The project combines data engineering, predictive modeling, analytics, and deployment into a single end-to-end system rather than treating forecasting as a notebook-only workflow.

## Live Demo

Frontend: [kamareddyprojectionfrontend.vercel.app](https://kamareddyprojectionfrontend.vercel.app)

## Repository Overview

This repository contains the full AgriFore system stack, including:

- `AgriMarket/` — market-related data and processing workflows
- `AgricultureProd/` — production-related data and validation layers
- `aaaFinalModels/` — model artifacts / final modeling layer
- `api/` — backend serving and API integration
- `frontend/` — user-facing application layer
- research and verification artifacts, including:
  - `AgriFore_IEEE_Paper.md`
  - `AgriFore_IEEE_Paper_repo_verified.md`
  - forecast output files
  - prediction-vs-reality analysis
  - runtime and verification summaries

These components indicate that the project is organized as a full system spanning data, models, API, frontend, and research-style documentation. :contentReference[oaicite:1]{index=1}

## What the Project Does

AgriFore is designed as an agricultural decision-support system that connects:

- crop production data
- weather signals
- market/transaction data
- forecasting outputs
- dashboard-style exploration
- deployment-ready interfaces

The goal is to make forecasting usable in a practical workflow, where data preparation, model outputs, and user-facing analytics all connect inside one system.

