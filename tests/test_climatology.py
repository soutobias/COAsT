from datetime import date
import pytest

import numpy as np
import pandas as pd
import xarray as xr

from coast import seasons
from coast.CLIMATOLOGY import CLIMATOLOGY


YEARS = [2000, 2001]
PERIOD = seasons.ALL
# Date ranges for all seasons 2000 -> 2003.
DATE_RANGES = [
    (date(2000, 3, 1), date(2000, 5, 31)),
    (date(2000, 6, 1), date(2000, 9, 30)),
    (date(2000, 10, 1), date(2000, 11, 30)),
    (date(2000, 12, 1), date(2001, 2, 28)),
    (date(2001, 3, 1), date(2001, 5, 31)),
    (date(2001, 6, 1), date(2001, 9, 30)),
    (date(2001, 10, 1), date(2001, 11, 30)),
    (date(2001, 12, 1), date(2002, 2, 28)),
]

EXPECTED_MEANS = np.array([45.5, 152.5, 244.0, 319.5, 410.5, 517.5, 609.0, 684.5])


@pytest.fixture
def test_dataset():
    time = pd.date_range(start=DATE_RANGES[0][0], end=DATE_RANGES[-1][1], freq='D')
    ds = xr.Dataset({"data": ("time", np.arange(len(time))), "time": time})
    yield ds


def test_get_date_ranges():
    result = CLIMATOLOGY._get_date_ranges(YEARS, PERIOD)
    assert result == DATE_RANGES


# Simple test for calculating means on a known small dataset. Generated within test_dataset().
def test_multiyear_averages(test_dataset):
    ds_mean = CLIMATOLOGY.multiyear_averages(test_dataset, PERIOD, time_var="time", time_dim="time")['data']
    # Assert ds_mean meaned data in equal to our precalculated EXPECTED_MEANS values.
    assert np.array_equal(ds_mean, EXPECTED_MEANS)
    # Assert there are 8 year_period index values in ds_mean. (One for each DATE RANGE.)
    assert len(ds_mean['year_period']) == 8
    # Assert dataset years are all values defined within the YEARS list.
    dataset_years = set(ds_mean['year_period_level_0'].data)
    assert set(dataset_years).issubset(YEARS)
