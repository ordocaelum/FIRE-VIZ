"""FastFuels baseline workflow stub.

The intended Phase II integration wraps FastFuels SDK builders to seed a first-pass fuel scene:

- SurfaceGridBuilder()
    - .with_fuel_load_from_landfire(...)
    - .with_fuel_depth_from_landfire(...)
    - .with_uniform_fuel_load_by_size_class(...)
- TreeGridBuilder()
    - .with_bulk_density_from_tree_inventory(...)
    - .with_canopy_base_height_from_inventory(...)
    - .with_species_groups(...)
- TopographyGridBuilder()
    - .with_elevation_from_3dep(...)
- Grids.create_export("QUIC-Fire")
- Grids.create_export("zarr")

FDS and FIRETEC are not native FastFuels SDK exporters, so FIRE-VIZ should treat those as
custom downstream conversions rather than first-class SDK output targets.
"""


def build_fastfuels_baseline(*args, **kwargs):
    raise NotImplementedError('FastFuels SDK integration is scaffolded but not implemented')
