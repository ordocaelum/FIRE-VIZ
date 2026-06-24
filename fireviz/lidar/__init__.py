"""LiDAR refinement scaffolding for FIRE-VIZ."""

from .ingest import ingest_lidar
from .stratify import stratify_returns
from .heterogeneity import cluster_understory
from .dwd import estimate_dwd_proxy
