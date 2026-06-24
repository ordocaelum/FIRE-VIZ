"""Tests for voxel compliance engine - must pass without any LiDAR or external API."""
import json
import numpy as np
import pytest
import tempfile
from pathlib import Path
from fireviz.voxelize import VoxelBuilder, FuelColumn, write_voxel_netcdf, write_aoi_geojson, validate_array, VoxelComplianceError

SENTINEL = 1.23456


def make_synthetic_5x5():
    """5x5 grid with varying heights: some empty, some <1m, some >1m."""
    builder = VoxelBuilder(nx=5, ny=5, x_origin=0.0, y_origin=0.0, crs="EPSG:32617")
    builder.add_column(FuelColumn(x_idx=1, y_idx=1, height_m=0.5,
        bulk_density=1.2, live_dead_fraction=0.6, moisture=0.12,
        savr=6000.0, fuel_load=0.8, surface_depth=0.3, provenance=0))
    builder.add_column(FuelColumn(x_idx=2, y_idx=2, height_m=1.5,
        bulk_density=2.1, live_dead_fraction=0.4, moisture=0.15,
        savr=5500.0, fuel_load=1.2, surface_depth=0.5, provenance=1))
    builder.add_column(FuelColumn(x_idx=3, y_idx=3, height_m=2.5,
        bulk_density=0.9, live_dead_fraction=0.7, moisture=0.10,
        savr=7000.0, fuel_load=0.6, surface_depth=0.2, provenance=1))
    builder.add_column(FuelColumn(x_idx=4, y_idx=4, height_m=0.8,
        bulk_density=1.5, live_dead_fraction=0.5, moisture=0.13,
        savr=6200.0, fuel_load=0.9, surface_depth=0.4, provenance=0))
    return builder.build()


def test_vertical_extent():
    """Uniform vertical extent driven by tallest column (2.5m -> 3 layers)."""
    ds = make_synthetic_5x5()
    assert ds.sizes['z'] == 3


def test_empty_column_sentinel():
    """Empty columns: bulk_density=0, all other fuel props=sentinel."""
    ds = make_synthetic_5x5()
    assert float(ds['bulk_density'].values[0, 0, 0]) == 0.0
    assert abs(float(ds['live_dead_fraction'].values[0, 0, 0]) - SENTINEL) < 1e-3
    assert abs(float(ds['moisture'].values[0, 0, 0]) - SENTINEL) < 1e-3
    assert abs(float(ds['savr'].values[0, 0, 0]) - SENTINEL) < 1e-3
    assert abs(float(ds['fuel_load'].values[0, 0, 0]) - SENTINEL) < 1e-3


def test_surface_depth_only_in_bottom_layer():
    """surface_depth must be sentinel in all layers above z=0."""
    ds = make_synthetic_5x5()
    if ds.sizes['z'] > 1:
        upper = ds['surface_depth'].values[:, :, 1:]
        assert np.allclose(upper, SENTINEL, atol=1e-3)


def test_provenance_array():
    """Provenance: 255 for empty, 0 for model_derived, 1 for lidar_refined."""
    ds = make_synthetic_5x5()
    assert 'provenance' in ds.data_vars
    prov = ds['provenance'].values
    assert prov[0, 0, 0] == 255
    assert prov[2, 2, 0] == 1
    assert prov[1, 1, 0] == 0


def test_write_and_validate_netcdf():
    """Write NetCDF and run compliance checker."""
    ds = make_synthetic_5x5()
    with tempfile.TemporaryDirectory() as tmpdir:
        nc_path = Path(tmpdir) / "test.nc"
        write_voxel_netcdf(ds, nc_path)
        result = validate_array(nc_path)
        assert result['all_checks_passed'] is True


def test_write_geojson():
    """Write AOI GeoJSON with CRS."""
    ds = make_synthetic_5x5()
    with tempfile.TemporaryDirectory() as tmpdir:
        nc_path = Path(tmpdir) / "test.nc"
        geojson_path = Path(tmpdir) / "aoi.geojson"
        write_voxel_netcdf(ds, nc_path)
        write_aoi_geojson(ds, geojson_path)
        with open(geojson_path) as f:
            gj = json.load(f)
        assert gj['type'] == 'FeatureCollection'
        assert 'crs' in gj or any('crs' in str(f) for f in gj.get('features', []))


def test_compliance_checker_catches_violation():
    """Compliance checker raises VoxelComplianceError for bad data."""
    ds = make_synthetic_5x5()
    with tempfile.TemporaryDirectory() as tmpdir:
        nc_path = Path(tmpdir) / "bad.nc"
        ds['moisture'].values[0, 0, 0] = 0.99
        write_voxel_netcdf(ds, nc_path)
        with pytest.raises(VoxelComplianceError):
            validate_array(nc_path)
