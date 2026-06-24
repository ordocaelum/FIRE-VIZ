"""Understory occupancy imputation scaffold.

Planned methods include gradient-boosted trees and compact CNN models that infer missing understory
occupancy from neighboring fuel context, canopy structure, and LiDAR-derived metrics. Any voxel filled
through imputation must be flagged in the provenance array so downstream validation can separate inferred
fuel from directly observed or baseline-derived fuel.
"""


def impute_understory_occupancy(*args, **kwargs):
    raise NotImplementedError('Occupancy imputation is scaffolded only')
