"""LiDAR ingestion scaffold.

Planned PDAL flow:
    readers.las -> filters.hag_delaunay -> filters.range -> voxel binning

The output of this stage should normalize heights above ground, clip to the AOI, and accumulate
return statistics into 1 m vertical bins compatible with the FIRE-VIZ voxel builder.
"""


def ingest_lidar(*args, **kwargs):
    raise NotImplementedError('PDAL-backed LiDAR ingestion will be implemented in a later phase')
