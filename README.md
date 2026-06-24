# FIRE-VIZ

FIRE-VIZ is a Python-based 3D surface and understory fuels characterization pipeline built for the SERDP / Central Florida Tech Grove **3D Surface Fuels & Vegetation Modeling Prize Challenge**.

## Critical boundary

**FIRE-VIZ characterizes and visualizes fuels; it does NOT compute fire behavior and does not replace QUIC-Fire, FIRETEC, or FDS.** It prepares compliant fuel inputs, diagnostics, and validation hooks for those downstream fire behavior systems.

## Three-stage architecture

1. **FastFuels baseline**: scaffolded hooks for generating a first-pass landscape from FastFuels and public datasets.
2. **LiDAR understory refinement**: scaffolded modules for PDAL-backed ingestion, stratification, heterogeneity analysis, and DWD proxy estimation.
3. **Compliant voxel array + validation**: implemented voxel builder, NetCDF/GeoJSON writers, renderer hooks, and validation harness.

## Module map

- `fireviz/voxelize/` — implemented voxel compliance engine, NetCDF writer, GeoJSON AOI writer, validator
- `fireviz/viz/` — PyVista renderer and property-map generation
- `fireviz/validation/` — holdout validation and provenance summaries
- `fireviz/baseline/` — FastFuels integration scaffold
- `fireviz/lidar/` — LiDAR refinement scaffolds
- `fireviz/impute/` — understory imputation scaffold
- `fireviz/export/` — downstream export scaffolds
- `fireviz/aoi/` — AOI helpers and placeholders
- `scripts/` — synthetic example generation
- `tests/` — self-contained compliance and validation tests

## Status

| Module | Status | Notes |
| --- | --- | --- |
| `voxelize` | Implemented | Pass/fail compliance engine with sentinel handling, CRS, NetCDF export, AOI GeoJSON |
| `viz` | Implemented | PyVista voxel rendering plus matplotlib-derived property maps |
| `validation` | Partially implemented | Holdout validation and provenance summary are real; literature/LANDFIRE comparisons are placeholders |
| `baseline` | Scaffolded | Documents target FastFuels SDK API calls |
| `lidar` | Scaffolded | Documents PDAL and analysis phases |
| `impute` | Scaffolded | Documents provenance-aware imputation |
| `export` | Scaffolded | Documents QUIC-Fire and FastFuels-oriented exports |
| `aoi` | Implemented | Placeholder AOIs plus GeoJSON-oriented helpers |

## Installation

```bash
pip install -e ".[dev]"
```

Optional extras:

```bash
pip install -e ".[dev,lidar]"
pip install -e ".[dev,fastfuels]"
```

## Quick start

Generate a synthetic compliant voxel array:

```bash
python scripts/generate_synthetic_array.py
```

Validate an emitted array in Python:

```python
from fireviz.voxelize import validate_array
result = validate_array("outputs/synthetic_fireviz.nc")
print(result["all_checks_passed"])
```

Render a PNG preview:

```bash
python -m fireviz.viz outputs/synthetic_fireviz.nc --property bulk_density --output outputs/bulk_density.png
```

## Compliance behavior implemented here

- 1 m × 1 m × 1 m voxels
- Separate arrays for `bulk_density`, `live_dead_fraction`, `moisture`, `savr`, `fuel_load`, `surface_depth`, and `provenance`
- Uniform vertical extent set by the tallest occupied column
- Empty cells use `bulk_density = 0` and sentinel `1.23456` for all non-density properties
- `surface_depth` is only populated in the bottom layer
- NetCDF output includes CRS metadata via `xarray` + `rioxarray`
- AOI bounding polygon is emitted as GeoJSON with CRS metadata
