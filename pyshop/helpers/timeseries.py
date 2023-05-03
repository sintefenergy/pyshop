from typing import Dict, Sequence, Union
from .typing_annotations import DataFrameOrSeries
import pandas as pd
import numpy as np

def create_constant_time_series(value:Union[int,float], start:pd.Timestamp) -> pd.Series:
    return pd.Series([value], index=[start])


def remove_consecutive_duplicates(df:DataFrameOrSeries) -> DataFrameOrSeries:
    """
    Compress timeseries by only keeping the first row of consecutive duplicates. This is done by comparing a copied
    DataFrame/Series that has been shifted by one, with the original, and only keeping the rows in which at least one
    one column value is different from the previous row. The first row will always be kept. NaN values must be replaced
    with a proper number before comparing since NaN != NaN. Undo the change before returning the compressed DataFrame/Series
    """
    df = df.replace(np.nan, 1e40)
    if isinstance(df, pd.DataFrame):
        df = df.loc[(df.shift() != df).any(axis=1)]
    else:
        df = df.loc[df.shift() != df]
    df = df.replace(1e40, np.nan)
    return df


def get_timestamp_indexed_series(starttime:pd.Timestamp, time_unit:str, t:Sequence[Union[int,float]], y:Sequence[float], column_name:str='data') -> DataFrameOrSeries:
    if not isinstance(t, np.ndarray):
        t = np.fromiter(t, int)
    if not isinstance(y, np.ndarray):
        y = np.array(y, dtype=float)
    if time_unit == 'minute':
        delta = pd.Timedelta(minutes=1)
    elif time_unit == 'second':
        delta = pd.Timedelta(seconds=1)
    else:
        delta = pd.Timedelta(hours=1)

    # Remove time zone info before calling to_datetime64 which automatically converts timestamps to utc time
    tz_name = starttime.tzname()
    if tz_name is not None:
        starttime = starttime.tz_localize(tz=None)

    t = np.repeat(starttime.to_datetime64(), t.size) + t * delta
    if y.size > t.size:  # Stochastic
        value = pd.DataFrame(data=y, index=t)
        if tz_name is not None:
            value.index = value.index.tz_localize(tz=tz_name)     #Add the original time zone info back        
    else:
        value = pd.Series(data=y.flatten(), index=t, name=column_name)
        if tz_name is not None:
            value = value.tz_localize(tz=tz_name)                 #Add the original time zone info back 

    value[value >= 1.0e40] = np.nan

    return value


def resample_resolution(time:Dict, df:DataFrameOrSeries, delta:float, time_resolution:pd.Series) -> DataFrameOrSeries:
    """
    Resample timeseries when time resolution is non-constant
    """
    # Convert timeseries index to integers based on the time unit
    df.index = ((df.index - time['starttime']).total_seconds() * delta).astype(int)

    # Compress the time resolution returned from shop, by only keeping the first of consecutive duplicate resolutions
    resolution_format = time_resolution.astype(int)
    compressed_resolution_format = remove_consecutive_duplicates(resolution_format)

    # Extract the different time resolutions and their respective time of enactment
    resolution_tuples = list(compressed_resolution_format.items())

    # Add a dummy time at the optimization end time to serve as a well defined bound
    resolution = resolution_tuples[-1][1]
    end_unit_index = int((time['endtime'] - time['starttime']).total_seconds() * delta)
    resolution_tuples.append((end_unit_index, resolution))

    # Build the resampled output
    output_parts = []
    index = 0
    for i, res_tuple in enumerate(resolution_tuples[:-1]):
        unit_index, resolution = res_tuple
        next_unit_index = resolution_tuples[i+1][0]
        selection = df.iloc[unit_index:next_unit_index]

        # Normalize index
        # line below is commented out since it gives wrong result after concating output parts
        # selection.index = selection.index - unit_index

        # Resample by taking the mean of all datapoints in "resolution" sized windows
        selection = selection.rolling(window=resolution).mean().shift(-(resolution-1))

        # Extract the correct means from the rolling means
        selection = selection.iloc[::resolution]

        # Handle any remaining intervals that are less than "resolution" sized
        if (next_unit_index - unit_index) % resolution != 0:
            reduced_res = (next_unit_index - unit_index) % resolution
            last_selection_index = next_unit_index - reduced_res
            last_row = df.iloc[last_selection_index:next_unit_index].mean()
            if isinstance(df, pd.Series):
                last_row = pd.Series(index=[last_selection_index], data=[last_row])
            else:
                last_row = last_row.to_frame().T
                last_row.index = [last_selection_index]
            # Replace the last row, as this has been set to "nan" by the rolling mean
            selection = pd.concat([selection[:-1], last_row])
        output_parts.append(selection)

        index = index + (next_unit_index-unit_index)//resolution
    output_df = pd.concat(output_parts)
    return output_df
