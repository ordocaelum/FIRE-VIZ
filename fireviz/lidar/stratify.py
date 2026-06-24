"""LiDAR stratification scaffold.

Vertical strata targets:
- litter: < 0.3 m
- herb: 0.3-1.0 m
- shrub: 1.0-2.0 m

These bins are intended to support surface/understory attribution before voxel-level fusion.
"""


def stratify_returns(*args, **kwargs):
    raise NotImplementedError('Vertical stratification logic is scaffolded only')
