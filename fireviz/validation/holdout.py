from __future__ import annotations

import numpy as np
import xarray as xr
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split



def run_holdout_validation(ds: xr.Dataset, test_fraction=0.2, random_seed=42) -> dict:
    """Predict bottom-layer bulk density from x, y, and surface depth."""
    bottom_bulk_density = ds['bulk_density'].isel(z=0).values
    bottom_surface_depth = ds['surface_depth'].isel(z=0).values
    xx, yy = np.meshgrid(ds['x'].values, ds['y'].values, indexing='ij')
    occupied = bottom_bulk_density > 0

    X = np.column_stack([xx[occupied], yy[occupied], bottom_surface_depth[occupied]])
    y = bottom_bulk_density[occupied]
    if y.size < 3:
        raise ValueError('Need at least three occupied cells for holdout validation')

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_fraction, random_state=random_seed)
    model = GradientBoostingRegressor(random_state=random_seed)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    return {
        'rmse': float(np.sqrt(mean_squared_error(y_test, preds))),
        'r2': float(r2_score(y_test, preds)),
        'n_train': int(y_train.size),
        'n_test': int(y_test.size),
    }



def provenance_summary(ds: xr.Dataset) -> dict:
    """Summarize provenance classes across occupied cells."""
    provenance = ds['provenance'].values
    occupied = provenance != 255
    total = int(occupied.sum())
    model_count = int((provenance == 0).sum())
    lidar_count = int((provenance == 1).sum())
    return {
        'model_derived_count': model_count,
        'lidar_refined_count': lidar_count,
        'no_data_count': int((provenance == 255).sum()),
        'model_derived_fraction': float(model_count / total) if total else 0.0,
        'lidar_refined_fraction': float(lidar_count / total) if total else 0.0,
        'occupied_count': total,
    }
