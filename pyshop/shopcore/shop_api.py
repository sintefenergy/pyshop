from typing import Any, Dict, List, Union
import numpy as np
import pandas as pd

from ..helpers.typing_annotations import ShopApi, ShopDatatypes, XyType
from ..helpers.time import get_shop_datetime, get_shop_timestring
from ..helpers.timeseries import create_constant_time_series, get_timestamp_indexed_series, resample_resolution

def get_attribute_value(shop_api:ShopApi, object_name:str, object_type:str, attribute_name:str, datatype:str, dataframe:bool=True) -> ShopDatatypes:
    value = None
    if datatype == 'int':
        value = shop_api.GetIntValue(object_type, object_name, attribute_name)
    elif datatype == 'int_array':
        value = list(shop_api.GetIntArray(object_type, object_name, attribute_name))
        if len(value) == 0:
            value = None
    elif datatype == 'double':
        value = shop_api.GetDoubleValue(object_type, object_name, attribute_name)
    elif datatype == 'double_array':
        value = list(shop_api.GetDoubleArray(object_type, object_name, attribute_name))
        if len(value) == 0:
            value = None
    elif datatype == 'string':
        value = shop_api.GetStringValue(object_type, object_name, attribute_name)
    elif datatype == 'string_array':
        value = shop_api.GetStringArray(object_type, object_name, attribute_name)
    elif datatype == 'xy':
        ref = shop_api.GetXyCurveReference(object_type, object_name, attribute_name)
        x = np.fromiter(shop_api.GetXyCurveX(object_type, object_name, attribute_name), float)
        y = np.fromiter(shop_api.GetXyCurveY(object_type, object_name, attribute_name), float)
        if x.size == 0:
            value = None
        else:
            if dataframe:
                value = pd.Series(y, index=x, name=ref)
            else:
                xy = [[x, y] for x, y in zip(x, y)]
                value = dict(ref=ref, xy=xy)
    elif datatype == 'sy':
        s = shop_api.GetSyCurveS(object_type, object_name, attribute_name)
        y = np.fromiter(shop_api.GetSyCurveY(object_type, object_name, attribute_name), float)
        if y.size == 0:
            value = None
        else:
            if dataframe:
                value = pd.Series(y, index=s)
            else:
                sy = [[s, y] for s, y in zip(s, y)]
                value = dict(sy=sy)
    elif datatype == 'xy_array':
        refs = np.fromiter(shop_api.GetXyCurveArrayReferences(object_type, object_name, attribute_name), float)
        n = np.fromiter(shop_api.GetXyCurveArrayNPoints(object_type, object_name, attribute_name), int)
        x = np.fromiter(shop_api.GetXyCurveArrayX(object_type, object_name, attribute_name), float)
        y = np.fromiter(shop_api.GetXyCurveArrayY(object_type, object_name, attribute_name), float)
        value = []
        offset = 0
        if n.size == 0:
            value = None
        else:
            if dataframe:
                for n_items, ref in zip(n, refs):
                    df = pd.Series(y[offset:offset + n_items], index=x[offset:offset + n_items], name=ref)
                    value.append(df)
                    offset += n_items
            else:
                for n_items, ref in zip(n, refs):
                    xy = [[x[i], y[i]] for i in range(offset, offset + n_items)]
                    v = dict(ref=ref, xy=xy)
                    value.append(v)
                    offset += n_items
    elif datatype == 'xyt':
        tz_name = get_shop_timzone_name(shop_api)
        start = get_shop_datetime(shop_api.GetStartTime(), tz_name)
        end = get_shop_datetime(shop_api.GetEndTime(), tz_name)
        value = get_xyt_attribute(shop_api, object_name, object_type, attribute_name, start, end, dataframe)
    elif datatype == 'txy':
        start_time = shop_api.GetTxySeriesStartTime(object_type, object_name, attribute_name)
        if start_time:
            tz_name = get_shop_timzone_name(shop_api)
            start_time = get_shop_datetime(start_time, tz_name)
            t = shop_api.GetTxySeriesT(object_type, object_name, attribute_name)
            y = shop_api.GetTxySeriesY(object_type, object_name, attribute_name)
            time_unit = shop_api.GetTimeUnit()
            value = get_timestamp_indexed_series(start_time, time_unit, t, y, column_name=attribute_name)
    else:
        value = None
    return value


def get_xyt_attribute(shop_api:ShopApi, object_name:str, object_type:str, attribute_name:str, start:pd.Timestamp, end:pd.Timestamp, dataframe:bool=True) -> List[XyType]:

    tz_name = get_shop_timzone_name(shop_api)
    
    #Get the time stamp for each xy function in the xyt attribute
    try:
        time_strings = shop_api.GetXyTCurveTimeStrings(object_type, object_name, attribute_name)
        time_list = [get_shop_datetime(t, tz_name) for t in time_strings]
    #To keep backwards compatibility before GetXyTCurveTimeStrings was implemented in the API. Get the time indices instead
    except AttributeError:
        time_indices = shop_api.GetXyTCurveTimes(object_type, object_name, attribute_name)
        shop_start_time = get_shop_datetime(shop_api.GetStartTime(), tz_name)

        time_unit = shop_api.GetTimeUnit()
        delta = pd.Timedelta(hours=1)
        if time_unit == 'minute':
            delta = pd.Timedelta(minutes=1)
        elif time_unit == 'second':
            delta = pd.Timedelta(seconds=1)

        time_list = [shop_start_time + t*delta for t in time_indices]

    x = np.fromiter(shop_api.GetXyTCurveX(object_type, object_name, attribute_name,
                                          get_shop_timestring(start), get_shop_timestring(end)), float)
    y = np.fromiter(shop_api.GetXyTCurveY(object_type, object_name, attribute_name,
                                          get_shop_timestring(start), get_shop_timestring(end)), float)
    n = np.fromiter(shop_api.GetXyTCurveN(object_type, object_name, attribute_name,
                                          get_shop_timestring(start), get_shop_timestring(end)), int)
    
    #Before SHOP 14.4.3.0, the function GetXyTCurveN returned a value for every time step in the optimization.
    #This can result in many 0 values for time steps where there is no xy table defined. 
    #Remove these zeros since the x and y arrays only return values for times where there is an xy
    n = n[n != 0]
    
    value = []
    offset = 0
    if n.size == 0:
        value = None
    else:
        if dataframe:            
            for n_items, time in zip(n, time_list):
                df = pd.Series(y[offset:offset + n_items], index=x[offset:offset + n_items], name=time)
                value.append(df)
                offset += n_items
        else:
            for n_items, time in zip(n, time_list):
                xy = [[x[i], y[i]] for i in range(offset, offset + n_items)]
                v = dict(time=time, xy=xy)
                value.append(v)
                offset += n_items
    return value


def get_attribute_info(shop_api:ShopApi, object_type:str, attribute_name:str, key:str='') -> Union[str,Dict[str,str]]:
    if key:
        return shop_api.GetAttributeInfo(object_type, attribute_name, key)
    else:
        return {
            key: shop_api.GetAttributeInfo(object_type, attribute_name, key) for key in shop_api.GetValidAttributeInfoKeys()
        }


def get_object_info(shop_api:ShopApi, object_type:str, key:str='') -> Union[str,Dict[str,str]]:
    if key:
        return shop_api.GetObjectInfo(object_type, key)
    else:
        return {key: shop_api.GetObjectInfo(object_type, key) for key in shop_api.GetValidObjectInfoKeys()}

def set_attribute(shop_api:ShopApi, object_name:str, object_type:str, attribute_name:str, datatype:str, value:ShopDatatypes) -> None:
    # Set a attribute in the SHOP core.
    # datatype = get_attribute_info(shop_api, object_type, attribute_name, 'datatype')
    if datatype == 'int':
        shop_api.SetIntValue(object_type, object_name, attribute_name, int(value))
    elif datatype == 'int_array':
        shop_api.SetIntArray(object_type, object_name, attribute_name, value)
    elif datatype == 'double':
        shop_api.SetDoubleValue(object_type, object_name, attribute_name, value)
    elif datatype == 'double_array':
        shop_api.SetDoubleArray(object_type, object_name, attribute_name, value)
    elif datatype == 'string':
        shop_api.SetStringValue(object_type, object_name, attribute_name, value)
    elif datatype == 'string_array':
        shop_api.SetStringArray(object_type, object_name, attribute_name, value)
    elif datatype == 'xy':
        if isinstance(value, pd.Series):
            ref = value.name
            if ref is None:
                ref = 0.0
            ref = float(ref)
            shop_api.SetXyCurve(object_type, object_name, attribute_name, ref, value.index.values,
                                value.values)
        else:
            x = [x[0] for x in value['xy']]
            y = [x[1] for x in value['xy']]
            shop_api.SetXyCurve(object_type, object_name, attribute_name, value['ref'], x, y)
    elif datatype == 'sy':
        if isinstance(value, pd.Series):
            shop_api.SetSyCurve(object_type, object_name, attribute_name, value.index.to_list(),
                                value.values)
        else:
            s = [s[0] for s in value['sy']]
            y = [x[1] for x in value['sy']]
            shop_api.SetSyCurve(object_type, object_name, attribute_name, list(s), y)
    elif datatype == 'xy_array':
        if len(value) == 0:
            return
        ref = np.array([])
        x = np.array([])
        y = np.array([])
        n = np.array([])
        if isinstance(value[0], pd.DataFrame):
            for df in value:
                ref = np.append(ref, float(df.columns[0]))
                n = np.append(n, df.size)
                x = np.append(x, df.index.values)
                y = np.append(y, df.iloc[:, 0].values)
        elif isinstance(value[0], pd.Series):
            for ser in value:
                ref = np.append(ref, float(ser.name))
                n = np.append(n, ser.size)
                x = np.append(x, ser.index.values)
                y = np.append(y, ser.values)
        else:
            for xy in value:
                ref = np.append(ref, xy['ref'])
                n = np.append(n, len(xy['xy']))
                x = np.append(x, [x[0] for x in xy['xy']])
                y = np.append(y, [x[1] for x in xy['xy']])
        shop_api.SetXyCurveArray(object_type, object_name, attribute_name, ref, n, x, y)
    elif datatype == 'xyt':
        if len(value) == 0:
            return

        #XYT curves are XY curves specified for different times
        #Convert times from timestamp to time strings in SHOP format
        times = []
        x = np.array([])
        y = np.array([])
        n = np.array([])
        if isinstance(value[0], pd.DataFrame):
            for df in value:
                t = pd.Timestamp(str(df.columns[0]))
                times.append(get_shop_timestring(t))
                n = np.append(n, df.size)
                x = np.append(x, df.index.values)
                y = np.append(y, df.iloc[:, 0].values)
        elif isinstance(value[0], pd.Series):
            for ser in value:
                t = pd.Timestamp(str(ser.name))
                times.append(get_shop_timestring(t))
                n = np.append(n, ser.size)
                x = np.append(x, ser.index.values)
                y = np.append(y, ser.values)
        else:
            for xy in value:
                t = pd.Timestamp(str(xy['time']))
                times.append(get_shop_timestring(t))
                n = np.append(n, len(xy['xy']))
                x = np.append(x, [x[0] for x in xy['xy']])
                y = np.append(y, [x[1] for x in xy['xy']])
        
        #Note that times is a regular python list while n, x, and y are np arrays
        shop_api.SetXyTCurve(object_type, object_name, attribute_name, times, n, x, y)        

    elif datatype == 'txy':
        time = get_time_resolution(shop_api)

        # Make sure we continue on with a Series or a DataFrame
        if isinstance(value, float) or isinstance(value, int):
            df = create_constant_time_series(value, time['starttime'])
        else:
            df = value

        if df.shape[0] == 0:
            shop_api.SetTxySeries(
                object_type, object_name, attribute_name,
                get_shop_timestring(time['starttime']), [], []
            )
            return

        # Extract data in time interval
        if df.loc[time['starttime']:time['starttime']].empty:
            df.loc[time['starttime']] = df.loc[:time['starttime']].iloc[-1]
            df.sort_index(inplace=True)
        df = df.loc[time['starttime']:time['endtime']]

        # Get scaling factor
        freq = 'H'
        delta = 1/3600
        if time['timeunit'] == 'minute':
            freq = 'T'
            delta = 1/60
        elif time['timeunit'] == 'second':
            freq = 'S'
            delta = 1
        txy_start_time = df.index[0]

        # If we have a non-constant time resolution, we need to resample input accordingly
        if time['timeresolution'].shape[0] > 1:
            if df.index[-1] != time['endtime']:
                if isinstance(df, pd.DataFrame):
                    new_row = pd.DataFrame(df[-1:].values, index=[time['endtime']], columns=df.columns)
                else:
                    new_row = pd.Series(df[-1], index=[time['endtime']])
                df = pd.concat([df, new_row])
            df = df.asfreq(freq=freq, method='ffill')
            df = df[:-1]
            time_resolution = pd.Series(data=shop_api.GetTimeResolutionY(), index=shop_api.GetTimeResolutionT())
            df = resample_resolution(time, df, delta, time_resolution)
            t = df.index
        else:
            t = (df.index - time['starttime']).total_seconds() * delta
        y = df.values
        shop_api.SetTxySeries(object_type, object_name, attribute_name, get_shop_timestring(txy_start_time),
                              t.astype(int), y)


def get_time_resolution(shop_api:ShopApi) -> Dict[str,Any]:
    tz_name = get_shop_timzone_name(shop_api)
    starttime = get_shop_datetime(shop_api.GetStartTime(), tz_name)
    endtime = get_shop_datetime(shop_api.GetEndTime(), tz_name)
    timeunit = shop_api.GetTimeUnit()
    t = shop_api.GetTimeResolutionT()
    y = shop_api.GetTimeResolutionY()
    timeresolution = get_timestamp_indexed_series(starttime, timeunit, t, y)
    return dict(starttime=starttime, endtime=endtime, timeunit=timeunit, timeresolution=timeresolution)

def get_shop_timzone_name(shop_api:ShopApi) -> str:
    try:
        tz_name = shop_api.GetTimeZone()
    except AttributeError:  # For backwards compatability to SHOP 13
        tz_name = ""
    return tz_name
