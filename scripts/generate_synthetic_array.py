from __future__ import annotations

from pathlib import Path

from fireviz.voxelize import FuelColumn, VoxelBuilder, validate_array, write_aoi_geojson, write_voxel_netcdf



def main() -> None:
    root = Path(__file__).resolve().parents[1]
    output_dir = root / 'outputs'
    output_dir.mkdir(exist_ok=True)

    builder = VoxelBuilder(nx=10, ny=10, x_origin=500000.0, y_origin=3300000.0, crs='EPSG:32617')
    for idx in range(10):
        builder.add_column(
            FuelColumn(
                x_idx=idx,
                y_idx=idx,
                height_m=0.5 + (idx % 4),
                bulk_density=0.8 + 0.1 * idx,
                live_dead_fraction=0.3 + 0.03 * idx,
                moisture=0.08 + 0.01 * idx,
                savr=5000.0 + 100.0 * idx,
                fuel_load=0.4 + 0.05 * idx,
                surface_depth=0.1 + 0.02 * idx,
                provenance=idx % 2,
            )
        )

    ds = builder.build()
    nc_path = output_dir / 'synthetic_fireviz.nc'
    geojson_path = output_dir / 'synthetic_fireviz_aoi.geojson'
    write_voxel_netcdf(ds, nc_path)
    write_aoi_geojson(ds, geojson_path)
    result = validate_array(nc_path)

    print('FIRE-VIZ synthetic array generated')
    print(f'NetCDF: {nc_path}')
    print(f'GeoJSON: {geojson_path}')
    print(f'Validation passed: {result["all_checks_passed"]}')
    print(f'Grid shape: x={ds.sizes["x"]}, y={ds.sizes["y"]}, z={ds.sizes["z"]}')


if __name__ == '__main__':
    main()
