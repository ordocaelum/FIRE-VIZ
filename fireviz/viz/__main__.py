"""CLI: python -m fireviz.viz <array.nc> [--property bulk_density] [--output out.png]"""

from __future__ import annotations

import argparse

from .renderer import VoxelRenderer



def main() -> None:
    parser = argparse.ArgumentParser(description='Render FIRE-VIZ voxel NetCDF files.')
    parser.add_argument('array_path', help='Path to voxel NetCDF file')
    parser.add_argument('--property', dest='property_name', default='bulk_density', help='Property to render')
    parser.add_argument('--output', dest='output_path', default=None, help='Optional PNG output path')
    parser.add_argument('--threshold', type=float, default=0.0, help='Threshold used for display')
    args = parser.parse_args()

    renderer = VoxelRenderer(args.array_path, off_screen=True)
    renderer.render_voxels(property_name=args.property_name, threshold=args.threshold, output_path=args.output_path)


if __name__ == '__main__':
    main()
