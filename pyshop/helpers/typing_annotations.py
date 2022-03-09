from typing import Any, Dict, List, Sequence, TypeVar, Union 
import pandas as pd
from ..shopcore import shop_rest

ShopCore = TypeVar("ShopCore")  #To represent shop_pybind.ShopCore
ShopApi = Union[ShopCore,'shop_rest.ShopRestNative']
IntStrFloat = Union[int,str,float]
DataFrameOrSeries = Union[pd.DataFrame,pd.Series]
CommandValues = Union[IntStrFloat,List[IntStrFloat]]
CommandOptions = Union[str,List[str]]
Message = Union[Dict[str,str], List[Dict[str,str]]]
XyType = Union[pd.Series,List[Dict[str,Any]]]       #XY curves can be specified by pd.Series or a list of dicts
ShopDatatypes = Union[IntStrFloat,Sequence[IntStrFloat],DataFrameOrSeries,Sequence[DataFrameOrSeries],XyType,List[XyType]]
LpModelDatatypes = Sequence[Union[IntStrFloat,bool]]