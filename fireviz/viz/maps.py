from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

SENTINEL = 1.23456



def _collapse_map(name: str, values: np.ndarray, bulk_density: np.ndarray) -> np.ndarray:
    occupied = ~np.isclose(bulk_density, 0.0)
    if name in {'bulk_density', 'fuel_load'}:
        data = values.copy()
        data[~occupied] = 0.0
        return data.sum(axis=2)
    data = values.astype(float)
    data[~occupied] = np.nan
    data[np.isclose(data, SENTINEL, atol=1e-4)] = np.nan
    return np.nanmean(data, axis=2)



def plot_property_maps(nc_path, output_dir):
    """Create per-property plan-view maps from a voxel NetCDF."""
    ds = xr.open_dataset(nc_path, engine='netcdf4')
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    bulk_density = ds['bulk_density'].values

    for name in ds.data_vars:
        collapsed = _collapse_map(name, ds[name].values, bulk_density)
        fig, ax = plt.subplots(figsize=(6, 5))
        im = ax.imshow(collapsed.T, origin='lower')
        ax.set_title(f'{name} horizontal map')
        ax.set_xlabel('x index')
        ax.set_ylabel('y index')
        fig.colorbar(im, ax=ax, label=name)
        fig.savefig(out_dir / f'{name}.png', dpi=200, bbox_inches='tight')
        plt.close(fig)
