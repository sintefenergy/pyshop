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

def test_resample_resolution():
    time_dict = dict(
        starttime=pd.Timestamp('2022-01-01T00:00'),
        endtime=pd.Timestamp('2022-01-02T00:00')
    )
    series = pd.Series([1, 2], index=[time_dict['starttime'], time_dict['starttime'] + pd.Timedelta(hours=7)])
    delta = 1/60
    timeres = pd.Series([15, 60], index=[time_dict['starttime'], time_dict['starttime'] + pd.Timedelta(hours=1)])
    series_res = resample_resolution(time_dict, series, delta, timeres)
    assert True
