from __future__ import annotations

from pathlib import Path

import numpy as np
import xarray as xr

SENTINEL = 1.23456
REQUIRED_VARIABLES = {
    'bulk_density',
    'live_dead_fraction',
    'moisture',
    'savr',
    'fuel_load',
    'surface_depth',
    'provenance',
}


class VoxelComplianceError(RuntimeError):
    """Raised when a voxel dataset violates FIRE-VIZ compliance rules."""



def _crs_present(ds: xr.Dataset) -> bool:
    if 'spatial_ref' in ds.variables:
        return True
    if ds.attrs.get('crs_wkt'):
        return True
    for name in ds.data_vars:
        attrs = ds[name].attrs
        if attrs.get('grid_mapping') or attrs.get('crs_wkt'):
            return True
    return False



def validate_array(path: str | Path) -> dict:
    """Validate a voxel NetCDF file against the required compliance rules."""
    source = Path(path)
    with xr.open_dataset(source, engine='netcdf4') as ds:
        checks: dict[str, bool] = {}
        checks['has_required_variables'] = REQUIRED_VARIABLES.issubset(set(ds.data_vars))
        checks['has_3d_coordinates'] = all(dim in ds.dims for dim in ('x', 'y', 'z')) and all(coord in ds.coords for coord in ('x', 'y', 'z'))
        checks['uniform_vertical_extent'] = len(ds['z'].shape) == 1 and int(ds.sizes.get('z', 0)) >= 1

        bulk_density = ds['bulk_density'].values
        empty_mask = np.isclose(bulk_density, 0.0, atol=1e-6)
        sentinel_checks = []
        for name in ('live_dead_fraction', 'moisture', 'savr', 'fuel_load', 'surface_depth'):
            values = ds[name].values
            if name == 'surface_depth':
                sentinel_checks.append(np.allclose(values[:, :, 1:], SENTINEL, atol=1e-3) if values.shape[2] > 1 else True)
                sentinel_checks.append(np.allclose(values[empty_mask], SENTINEL, atol=1e-3))
            else:
                sentinel_checks.append(np.allclose(values[empty_mask], SENTINEL, atol=1e-3))
        checks['sentinel_for_empty_cells'] = all(sentinel_checks)
        checks['surface_depth_bottom_layer_only'] = np.allclose(ds['surface_depth'].values[:, :, 1:], SENTINEL, atol=1e-3) if ds.sizes['z'] > 1 else True
        checks['crs_present'] = _crs_present(ds)
        checks['correct_sentinel_value'] = np.isfinite(SENTINEL) and not np.isnan(SENTINEL)
        checks['provenance_no_data_for_empty'] = np.all(ds['provenance'].values[empty_mask] == 255)
        checks['all_checks_passed'] = all(checks.values())

    if not checks['all_checks_passed']:
        failed = ', '.join(name for name, passed in checks.items() if name != 'all_checks_passed' and not passed)
        raise VoxelComplianceError(f'Voxel compliance validation failed: {failed}')
    return checks
