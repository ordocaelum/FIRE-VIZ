from __future__ import annotations

"""AOI helpers and placeholders for FIRE-VIZ."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AOIPlaceholder:
    name: str
    crs: str
    bbox: tuple[float, float, float, float]
    description: str


AOI_PLACEHOLDERS = {
    'eglin_afb_open_canopy': AOIPlaceholder(
        name='Eglin AFB open-canopy longleaf placeholder',
        crs='EPSG:32616',
        bbox=(540000.0, 3370000.0, 541000.0, 3371000.0),
        description='Representative open-canopy longleaf pine AOI placeholder for challenge planning.',
    ),
    'closed_canopy_secondary': AOIPlaceholder(
        name='Closed-canopy secondary site placeholder',
        crs='EPSG:32617',
        bbox=(500000.0, 3300000.0, 501000.0, 3301000.0),
        description='Placeholder AOI representing a denser secondary comparison site.',
    ),
}


def build_aoi_feature_collection(name: str) -> dict:
    if name not in AOI_PLACEHOLDERS:
        raise KeyError(f'Unknown AOI placeholder: {name}')
    aoi = AOI_PLACEHOLDERS[name]
    xmin, ymin, xmax, ymax = aoi.bbox
    return {
        'type': 'FeatureCollection',
        'crs': {'type': 'name', 'properties': {'name': aoi.crs}},
        'features': [
            {
                'type': 'Feature',
                'properties': {'name': aoi.name, 'description': aoi.description},
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
