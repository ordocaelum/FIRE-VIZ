"""Literature cross-comparison stub.
Reference loadings:
  - RxCADRE longleaf pine: bulk_density ~0.5-2.0 kg/m3 (Ottmar et al. 2016)
  - FCCS longleaf pine: fuel_load ~0.5-1.5 kg/m2 (Riccardi et al. 2007)
"""
REFERENCE_TABLE = {
    "longleaf_pine_rxcadre": {"bulk_density_kg_m3": (0.5, 2.0), "citation": "Ottmar et al. 2016"},
    "longleaf_pine_fccs": {"fuel_load_kg_m2": (0.5, 1.5), "citation": "Riccardi et al. 2007"},
}
def compare_to_literature(ds, vegetation_type="longleaf_pine_fccs"):
    raise NotImplementedError("Wire to real data in Phase II")
