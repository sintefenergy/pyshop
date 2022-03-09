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
    var:VarBuilder
    var_type:VarTypeBuilder
    row:RowBuilder
    row_type:RowTypeBuilder
    index_type:IndexTypeBuilder

    def __init__(self, shop:'shop_runner.ShopSession') -> None:
        self.shop = shop
        self._lp_model = {}
        self.var = VarBuilder(self)
        self.var_type = VarTypeBuilder(self)
        self.row = RowBuilder(self)
        self.row_type = RowTypeBuilder(self)
        self.index_type = IndexTypeBuilder(self)

    def build(self) -> None:
        self.shop.model.lp_model.lp_model['sim_mode'].set(1)
        self.shop.start_sim([], ['1'])

    def load_model(self) -> None:
        self.shop.reset_lp_model([], [])
        for attr_name in self.get_lp_model_attributes():
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

    def get_lp_model_attributes(self) -> Sequence[str]:
        return [n for n in self.shop.model.lp_model.get_attribute_names() if n != "sim_mode" and not n.startswith("add")]
