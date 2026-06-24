from __future__ import annotations

from pathlib import Path

import numpy as np
import xarray as xr

SENTINEL = 1.23456


class VoxelRenderer:
    """Render compliant FIRE-VIZ voxel arrays with PyVista."""

    def __init__(self, nc_path: str | Path, off_screen: bool = True):
        self.nc_path = Path(nc_path)
        self.off_screen = off_screen
        self.ds = xr.open_dataset(self.nc_path, engine='netcdf4')

    def close(self) -> None:
        """Close the underlying dataset and release file handles."""
        if self.ds is not None:
            self.ds.close()
            self.ds = None

    def __enter__(self) -> "VoxelRenderer":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _make_grid(self):
        import pyvista as pv

        nx, ny, nz = (self.ds.sizes['x'], self.ds.sizes['y'], self.ds.sizes['z'])
        x0 = float(self.ds['x'].values.min()) - 0.5
        y0 = float(self.ds['y'].values.min()) - 0.5
        grid = pv.ImageData(dimensions=(nx + 1, ny + 1, nz + 1), spacing=(1.0, 1.0, 1.0), origin=(x0, y0, 0.0))
        return grid

    def render_voxels(self, property_name: str = 'bulk_density', threshold: float = 0.0, output_path: str | Path | None = None) -> None:
        import pyvista as pv

        if property_name not in self.ds.data_vars:
            raise KeyError(f'Unknown property: {property_name}')

        grid = self._make_grid()
        values = np.asarray(self.ds[property_name].values, dtype=np.float32).copy()
        empty_mask = np.isclose(self.ds['bulk_density'].values, 0.0)
        if property_name != 'bulk_density':
            values[empty_mask] = 0.0
            values[np.isclose(values, SENTINEL, atol=1e-4)] = 0.0
        grid.cell_data[property_name] = values.ravel(order='F')

        plotter = pv.Plotter(off_screen=self.off_screen)
        mesh = grid.threshold(value=threshold, scalars=property_name)
        plotter.add_mesh(mesh, scalars=property_name, show_edges=False)
        plotter.add_axes()
        if output_path is not None:
            plotter.show(screenshot=str(output_path))
        else:
            plotter.show()
        plotter.close()

    def render_vertical_slice(self, property_name: str, x_idx: int, output_path: str | Path | None = None) -> None:
        import matplotlib.pyplot as plt

        if property_name not in self.ds.data_vars:
            raise KeyError(f'Unknown property: {property_name}')
        if not 0 <= x_idx < self.ds.sizes['x']:
            raise IndexError('x_idx out of range')

        slice_data = np.asarray(self.ds[property_name].isel(x=x_idx).transpose('z', 'y').values, dtype=float)
        if property_name != 'bulk_density':
            slice_data[np.isclose(slice_data, SENTINEL, atol=1e-4)] = np.nan

        fig, ax = plt.subplots(figsize=(8, 4))
        im = ax.imshow(slice_data, origin='lower', aspect='auto')
        ax.set_title(f'{property_name} vertical slice at x={x_idx}')
        ax.set_xlabel('y index')
        ax.set_ylabel('z layer')
        fig.colorbar(im, ax=ax, label=property_name)
        if output_path is not None:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(output_path, dpi=200, bbox_inches='tight')
        else:
            plt.show()
        plt.close(fig)
