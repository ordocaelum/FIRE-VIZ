"""Tests for FIRE-VIZ validation helpers."""

from fireviz.validation import provenance_summary, run_holdout_validation
from tests.test_voxelize import make_synthetic_5x5



def test_holdout_validation_returns_metrics():
    ds = make_synthetic_5x5()
    result = run_holdout_validation(ds, test_fraction=0.5, random_seed=7)
    assert set(result) == {'rmse', 'r2', 'n_train', 'n_test'}
    assert result['n_train'] > 0
    assert result['n_test'] > 0
    assert result['rmse'] >= 0.0



def test_provenance_summary_counts_occupied_cells():
    ds = make_synthetic_5x5()
    summary = provenance_summary(ds)
    assert summary['occupied_count'] == 7
    assert summary['model_derived_count'] == 2
    assert summary['lidar_refined_count'] == 5
    assert abs(summary['model_derived_fraction'] + summary['lidar_refined_fraction'] - 1.0) < 1e-9
