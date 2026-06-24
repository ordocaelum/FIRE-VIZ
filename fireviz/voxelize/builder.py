from __future__ import annotations

from dataclasses import dataclass
from math import ceil

import numpy as np
import rioxarray  # noqa: F401
import xarray as xr

SENTINEL = np.float32(1.23456)
MODEL_DERIVED = 0
LIDAR_REFINED = 1
NO_DATA = 255


@dataclass(frozen=True, slots=True)
class FuelColumn:
    """Description of a single 1 m x 1 m fuel column."""

    x_idx: int
    y_idx: int
    height_m: float
    bulk_density: float
    live_dead_fraction: float
    moisture: float
    savr: float
    fuel_load: float
    surface_depth: float
    provenance: int


class VoxelBuilder:
    """Build a spec-compliant 3D voxel fuel dataset."""

    def __init__(self, nx: int, ny: int, x_origin: float = 0.0, y_origin: float = 0.0, crs: str = "EPSG:4326"):
        if nx <= 0 or ny <= 0:
            raise ValueError("nx and ny must be positive integers")
        self.nx = int(nx)
        self.ny = int(ny)
        self.x_origin = float(x_origin)
        self.y_origin = float(y_origin)
        self.crs = crs
        self._columns: dict[tuple[int, int], FuelColumn] = {}

    def add_column(self, col: FuelColumn) -> None:
        """Add a fuel column definition for a grid cell."""
        if not 0 <= col.x_idx < self.nx:
            raise IndexError(f"x_idx {col.x_idx} out of bounds for nx={self.nx}")
        if not 0 <= col.y_idx < self.ny:
            raise IndexError(f"y_idx {col.y_idx} out of bounds for ny={self.ny}")
        if col.height_m <= 0:
            raise ValueError("height_m must be greater than zero")
        if col.provenance not in (MODEL_DERIVED, LIDAR_REFINED):
            raise ValueError("provenance must be 0 (model_derived) or 1 (lidar_refined)")
        self._columns[(col.x_idx, col.y_idx)] = col

    def build(self) -> xr.Dataset:
        """Build a spec-compliant voxel dataset with uniform vertical extent."""
        tallest = max((col.height_m for col in self._columns.values()), default=0.0)
        n_z = max(1, ceil(tallest))

        x = self.x_origin + np.arange(self.nx, dtype=np.float32)
        y = self.y_origin + np.arange(self.ny, dtype=np.float32)
        z = np.arange(1, n_z + 1, dtype=np.float32)
        shape = (self.nx, self.ny, n_z)

        bulk_density = np.zeros(shape, dtype=np.float32)
        live_dead_fraction = np.full(shape, SENTINEL, dtype=np.float32)
        moisture = np.full(shape, SENTINEL, dtype=np.float32)
        savr = np.full(shape, SENTINEL, dtype=np.float32)
        fuel_load = np.full(shape, SENTINEL, dtype=np.float32)
        surface_depth = np.full(shape, SENTINEL, dtype=np.float32)
        provenance = np.full(shape, NO_DATA, dtype=np.uint8)

        for col in self._columns.values():
            filled_layers = max(1, ceil(col.height_m))
            slc = slice(0, filled_layers)
            bulk_density[col.x_idx, col.y_idx, slc] = np.float32(col.bulk_density)
            live_dead_fraction[col.x_idx, col.y_idx, slc] = np.float32(col.live_dead_fraction)
            moisture[col.x_idx, col.y_idx, slc] = np.float32(col.moisture)
            savr[col.x_idx, col.y_idx, slc] = np.float32(col.savr)
            fuel_load[col.x_idx, col.y_idx, slc] = np.float32(col.fuel_load)
            provenance[col.x_idx, col.y_idx, slc] = np.uint8(col.provenance)
            surface_depth[col.x_idx, col.y_idx, 0] = np.float32(col.surface_depth)

        ds = xr.Dataset(
            data_vars={
                'bulk_density': (("x", "y", "z"), bulk_density),
                'live_dead_fraction': (("x", "y", "z"), live_dead_fraction),
                'moisture': (("x", "y", "z"), moisture),
                'savr': (("x", "y", "z"), savr),
                'fuel_load': (("x", "y", "z"), fuel_load),
                'surface_depth': (("x", "y", "z"), surface_depth),
                'provenance': (("x", "y", "z"), provenance),
            },
            coords={
                'x': ('x', x, {'long_name': 'x coordinate of voxel center', 'units': 'm'}),
                'y': ('y', y, {'long_name': 'y coordinate of voxel center', 'units': 'm'}),
                'z': ('z', z, {'long_name': 'height above ground', 'units': 'm', 'positive': 'up'}),
            },
            attrs={
                'title': 'FIRE-VIZ compliant voxel fuel array',
                'Conventions': 'CF-1.10',
                'voxel_resolution': '1 m x 1 m x 1 m',
                'sentinel_value': float(SENTINEL),
                'crs': self.crs,
            },
        )

        attrs = {
            'bulk_density': {'long_name': 'fuel bulk density', 'units': 'kg m-3'},
            'live_dead_fraction': {'long_name': 'live to dead fuel fraction', 'units': '1'},
            'moisture': {'long_name': 'fuel moisture content', 'units': 'kg kg-1'},
            'savr': {'long_name': 'surface area to volume ratio', 'units': 'm-1'},
            'fuel_load': {'long_name': 'fuel load', 'units': 'kg m-2'},
            'surface_depth': {'long_name': 'surface fuel depth in ground-adjacent layer', 'units': 'm'},
            'provenance': {
                'long_name': 'fuel data provenance',
                'flag_values': np.array([0, 1, 255], dtype=np.uint8),
                'flag_meanings': 'model_derived lidar_refined no_data',
            },
        }
        for var, var_attrs in attrs.items():
            ds[var].attrs.update(var_attrs)
            ds[var].attrs['grid_mapping'] = 'spatial_ref'

        ds = ds.rio.set_spatial_dims(x_dim='x', y_dim='y', inplace=False)
        ds = ds.rio.write_crs(self.crs, inplace=False)
        return ds
