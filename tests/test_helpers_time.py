import pandas as pd
from pyshop.helpers.timeseries import remove_consecutive_duplicates, resample_resolution

def test_remove_consecutive_duplicates_series():
    series = pd.Series([1, 1, 2, 2, 2, 3], index=range(6))
    ret_series = remove_consecutive_duplicates(series)
    assert (ret_series.index == [0, 2, 5]).all()
    assert (ret_series.values == [1, 2 ,3]).all()

def test_remove_consecutive_duplicates_dataframe():
    df = pd.DataFrame([1, 1, 2, 2, 2, 3], index=range(6))
    ret_df = remove_consecutive_duplicates(df)
    assert (ret_df.index == [0, 2, 5]).all()
    assert (ret_df.values[:, 0] == [1, 2 ,3]).all()
