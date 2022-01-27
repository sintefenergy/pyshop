from typing import Any, Dict, Optional, Sequence
from ..helpers.typing_annotations import LpModelDatatypes
import numpy as np
from .. import shop_runner
from .row import RowBuilder, RowTypeBuilder
from .var import VarBuilder, VarTypeBuilder
from .index import IndexTypeBuilder

class LpModelBuilder(object):

    shop:'shop_runner.ShopSession'
    _lp_model:Dict[str,LpModelDatatypes]
    _lp_model_attributes:Dict[str,None]
    var:VarBuilder
    var_type:VarTypeBuilder
    row:RowTypeBuilder
    index_type:IndexTypeBuilder

    def __init__(self, shop:'shop_runner.ShopSession') -> None:
        self.shop = shop
        self._lp_model = {}
        self._lp_model_attributes = {
            "var_type_names": None, # Array{String}
            "var_type_abbrev": None, # Array{String}
            "var_type_index_type_beg": None, # Array{Int}
            "var_type_index_type_cnt": None, # Array{Int}
            "var_type_index_type_val": None, # Array{Int}
            "row_type_names": None, # Array{String}
            "row_type_index_type_beg": None, # Array{Int}
            "row_type_index_type_cnt": None, # Array{Int}
            "row_type_index_type_val": None, # Array{Int}
            "index_type_names": None, # Array{String}
            "index_type_desc_beg": None, # Array{Int}
            "index_type_desc_cnt": None, # Array{Int}
            "index_type_desc_val": None, # Array{String}
            "AA": None, # Array{Float64}
            "Irow": None, # Array{Int}
            "Jcol": None, # Array{Int}
            "rhs": None, # Array{Float64}
            "sense": None, # Array{Int}
            "ub": None, # Array{Float64}
            "lb": None, # Array{Float64}
            "cc": None, # Array{Float64}
            "bin": None, # Array{Bool}
            "x": None, # Array{Float64}
            "dual": None, # Array{Float64}
            "var_type": None, # Array{Int}
            "var_index_beg": None, # Array{Int}
            "var_index_cnt": None, # Array{Int}
            "var_index_val": None, # Array{Int}
            "row_type": None, # Array{Int}
            "row_index_beg": None, # Array{Int}
            "row_index_cnt": None, # Array{Int}
            "row_index_val": None, # Array{Int}
        }
        self.var = VarBuilder(self)
        self.var_type = VarTypeBuilder(self)
        self.row = RowBuilder(self)
        self.row_type = RowTypeBuilder(self)
        self.index_type = IndexTypeBuilder(self)

    def build(self) -> None:
        self.shop.model.lp_model.lp_model['sim_mode'].set(1)
        self.shop.start_sim([], ['1'])

    def load_model(self) -> None:
        self.shop.reset_lp_model([],[])
        for attr_name in self._lp_model_attributes.keys():
            self._lp_model[attr_name] = np.array(self.shop.model.lp_model.lp_model[attr_name].get())
    
    def load_results(self) -> None:
        for attr_name in ["x", "dual"]:
            self._lp_model[attr_name] = np.array(self.shop.model.lp_model.lp_model[attr_name].get())

    def solve(self) -> None:
        self.shop.model.lp_model.lp_model['sim_mode'].set(2)
        self.shop.start_sim([], ['1'])
        self.shop.model.lp_model.lp_model['sim_mode'].set(0)

    def build_pyomo_model(self, optimizer:Optional[Any]=None) -> None:
        pass # Not implemented yet

    def print(self, row_types:Sequence[int]=[], var_types:Sequence[int]=[]) -> None:
        print(self.row.format(row_types))
        for var_id in range(self.var.n_vars):
            if len(var_types) == 0 or self.var[var_id].type_id in var_types:
                print(self.var[var_id].format())
    
    def save(self, filename:str, row_types:Sequence[int]=[], var_types:Sequence[int]=[]) -> None:
        with open(filename, "w") as file:
            file.write(self.row.format(row_types) + '\n')
            for var_id in range(self.var.n_vars):
                if len(var_types) == 0 or self.var[var_id].type_id in var_types:
                    file.write(self.var[var_id].format() + '\n')