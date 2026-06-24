from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import rioxarray  # noqa: F401
import xarray as xr

SENTINEL = 1.23456


def _cell_edges(values: np.ndarray) -> tuple[float, float]:
    if values.size == 1:
        half = 0.5
    else:
        diffs = np.diff(values)
        half = float(np.median(diffs)) / 2.0
    return float(values.min() - half), float(values.max() + half)



def write_voxel_netcdf(ds: xr.Dataset, path: str | Path) -> None:
    """Write a voxel dataset to NetCDF with explicit encodings."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    encoding: dict[str, dict[str, object]] = {}
    for name, data_array in ds.data_vars.items():
        if np.issubdtype(data_array.dtype, np.floating):
            encoding[name] = {'zlib': True, 'complevel': 4, 'dtype': 'float32'}
        else:
            encoding[name] = {'zlib': True, 'complevel': 4, 'dtype': 'uint8'}
    if 'spatial_ref' in ds:
        encoding['spatial_ref'] = {'dtype': 'int32'}

    ds.to_netcdf(target, engine='netcdf4', encoding=encoding)



def write_aoi_geojson(ds: xr.Dataset, path: str | Path) -> None:
    """Write an AOI bounding polygon as GeoJSON with CRS metadata."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    x = ds['x'].values.astype(float)
    y = ds['y'].values.astype(float)
    xmin, xmax = _cell_edges(x)
    ymin, ymax = _cell_edges(y)
    crs_name = ds.rio.crs.to_string() if ds.rio.crs is not None else ds.attrs.get('crs', 'EPSG:4326')

    feature_collection = {
        'type': 'FeatureCollection',
        'crs': {'type': 'name', 'properties': {'name': crs_name}},
        'features': [
            {
                'type': 'Feature',
                'properties': {},
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [[
                        [xmin, ymin],
                        [xmax, ymin],
                        [xmax, ymax],
                        [xmin, ymax],
                        [xmin, ymin],
                    ]],
                },
            }
        ],
    }

    target.write_text(json.dumps(feature_collection, indent=2), encoding='utf-8')
