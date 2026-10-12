# Micro-Grid Time-Series Dataset Format Specification

This document details the required CSV/Excel schema, timestamp conventions, energy signal definitions, physical units, sampling frequency rules, and validation criteria for the **Micro-Grid Load Forecaster**.

---

## 1. Required & Supported Columns

The application requires a time-series dataset containing at least one **timestamp column** and one **numeric target power signal column**.

### Core Schema Overview

| Column Name | Data Type | Required / Optional | Physical Unit | Description |
| :--- | :--- | :--- | :--- | :--- |
| `timestamp` | ISO String / Datetime | **Required** | N/A | Chronological date and time of reading |
| `load_kW` | Float | **Recommended Target** | Kilowatts (kW) | Total active electrical load / power consumption |
| `solar_generation_kW` | Float | Optional Signal | Kilowatts (kW) | Solar PV generation power output |
| `wind_generation_kW` | Float | Optional Signal | Kilowatts (kW) | Wind turbine generation power output |
| `battery_soc` | Float | Optional Signal | Percentage (%) | Battery storage State of Charge (20% - 100%) |
| `grid_import_kW` | Float | Optional Signal | Kilowatts (kW) | Net active power imported from external grid |

---

## 2. Timestamp Specifications & Parsing Rules

- **Supported Formats**:
  - `YYYY-MM-DD HH:MM:SS` (e.g. `2026-01-01 08:00:00`)
  - `YYYY-MM-DDTHH:MM:SSZ` (ISO 8601 UTC)
  - `MM/DD/YYYY HH:MM`
- **Sorting Requirement**: Datasets are automatically sorted chronologically by timestamp upon ingestion.
- **Duplicate Rule**: If duplicate timestamps are found, the first occurrence is retained and a warning is recorded in the data quality audit summary.

---

## 3. Sampling Frequency & Resampling

- **Supported Frequencies**:
  - `1 Hour (1H)` (Standard microgrid interval)
  - `15 Minutes (15T)`
  - `1 Day (1D)`
- **Missing Value Handling**:
  - Missing values in continuous power signals are filled using **linear interpolation** bounded by leading and trailing valid observations.
  - Silent dropping of missing rows is avoided to maintain uniform time steps for lag feature engineering.

---

## 4. Sample CSV Data Format

Below is an excerpt of a valid micro-grid time-series CSV dataset:

```csv
timestamp,load_kW,solar_generation_kW,wind_generation_kW,battery_soc,grid_import_kW
2026-01-01 00:00:00,132.45,0.00,78.20,60.0,54.25
2026-01-01 01:00:00,128.10,0.00,82.40,58.5,45.70
2026-01-01 06:00:00,185.60,12.30,65.10,55.0,108.20
2026-01-01 12:00:00,345.80,234.50,45.20,85.0,66.10
2026-01-01 19:00:00,420.15,0.00,92.30,70.0,327.85
```

---

## 5. Distinction Between Power (kW) and Energy (kWh)

- **Power (kW)**: Represents instantaneous rate of energy consumption or generation.
- **Energy (kWh)**: Represents total energy accumulated over time.
- **Note**: This application operates primarily on **Power signals (kW)** sampled at regular intervals.
