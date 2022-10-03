from typing import Any, Dict, List, Optional, Sequence, Union
import numpy as np
from . import lp_model


class Var(object):

    lp_model:'lp_model.LpModelBuilder'
    id:int

    def __init__(self, lp_model:'lp_model.LpModelBuilder', var_id: int) -> None:
        self.lp_model = lp_model
        self.id = var_id

    def __getattr__(self, attr:str) -> Any:
        type_id = self.lp_model._lp_model['var_type'][self.id]
        if attr == 'id':
            return self.id
        elif attr == 'type_id':
            return type_id
        elif attr == 'type_name':
            return self.lp_model.get_var_types()[type_id]
        elif attr == 'type_abbrev':
            return self.lp_model._lp_model['var_type_abbrev'][type_id]
        elif attr == 'index_type_ids':
            return self.lp_model.var_type[type_id].get_index_types()
        elif attr == 'index_type_names':
            return self.lp_model.index_type.get_names()[self.lp_model.var_type[type_id].get_index_types()]
        elif attr == 'index_values':
            return self.get_index_values()
        elif attr == 'index_descriptions':
            index_types = self.lp_model.var_type[type_id].get_index_types()
            index_values = self.get_index_values()
            return [self.lp_model.index_type[t].description[v] for (t, v) in zip(index_types, index_values)]
        elif attr in self.__dir__():
            try:
                return self.lp_model._lp_model[attr][self.id]
            except:
                return None
        else:
            return None

    def __dir__(self) -> Sequence[str]:
        return np.append(
            ['id', 'type_id', 'type_name', 'type_abbrev', 'index_type_ids', 'index_type_names',
                'index_values', 'index_descriptions', 'ub', 'lb', 'cc', 'bin', 'x'],
            super().__dir__()
        )

    def info(self) -> Dict[str,Any]:
        type_id = self.lp_model._lp_model['var_type'][self.id]
        index_type_ids = self.lp_model.var_type[type_id].get_index_types()
        index_values = self.get_index_values()
        return {
            'id': self.id,
            'type_id': type_id,
            'type_name': self.lp_model.var_type[type_id].name,
            'index_type_ids': index_type_ids,
            'index_type_names': self.lp_model.index_type.get_names()[index_type_ids],
            'index_values': index_values,
            'index_descriptions': [self.lp_model.index_type[t].description[v] for (t, v) in zip(index_type_ids, index_values)],
            'ub': self.lp_model._lp_model['ub'][self.id],
            'lb': self.lp_model._lp_model['lb'][self.id],
            'cc': self.lp_model._lp_model['cc'][self.id],
            'bin': self.lp_model._lp_model['bin'][self.id],
            'x': self.x
        }

    def format(self) -> str:
        return '{} <= {}{} <= {}'.format(self.lb, self.type_abbrev, self.index_values, self.ub)

    def set_parameters(self, ub: Optional[float] = None, lb: Optional[float] = None, cc: Optional[float] = None, bin: Optional[int] = None) -> int:
        info = self.info()
        self.lp_model.shop.model.lp_model.lp_model['add_var_type'].set(info['type_id'])
        self.lp_model.shop.model.lp_model.lp_model['add_var_index'].set(info['index_values'])
        self.lp_model.shop.model.lp_model.lp_model['add_var_ub'].set(info['ub'] if ub is None else ub)
        self.lp_model.shop.model.lp_model.lp_model['add_var_lb'].set(info['lb'] if lb is None else lb)
        self.lp_model.shop.model.lp_model.lp_model['add_var_cc'].set(info['cc'] if cc is None else cc)
        self.lp_model.shop.model.lp_model.lp_model['add_var_bin'].set((1 if info['bin'] else 0) if bin is None else bin)
        self.lp_model.shop.set_lp_var([], [])
        return self.lp_model.shop.model.lp_model.lp_model['add_var_last'].get()

    def get_index_values(self) -> Sequence[int]:
        lp_model = self.lp_model._lp_model
        return (
            lp_model['var_index_val'][
                lp_model['var_index_beg'][self.id]:lp_model['var_index_beg'][self.id] + lp_model['var_index_cnt'][self.id]
            ]
        )


class VarBuilder(object):

    lp_model:'lp_model.LpModelBuilder'

    def __init__(self, lp_model:'lp_model.LpModelBuilder') -> None:
        self.lp_model = lp_model

    def __getitem__(self, item:int) -> Var:
        if isinstance(item, (int, np.integer)):
            return Var(self.lp_model, item)
        else:
            return None

    def __getattr__(self, item:str) -> int:
        if item == 'n_vars':
            return self.lp_model._lp_model['var_type'].size
    
    def __dir__(self) -> Sequence[str]:
        return np.append(
            super().__dir__(), 'n_vars'
        )

    def filter(self, var_type:Optional[int]=None, index_values:Sequence[int]=[]) -> List[int]:
        lp_model = self.lp_model
        result = []
        for (var_id, var_t) in enumerate(lp_model._lp_model['var_type']):
            if var_type is None or var_type == var_t:
                # Check if index matches
                if len(index_values) == 0:
                    result.append(var_id)
                else:
                    index_val = lp_model.var[var_id].get_index_values()
                    success = True
                    for (i, r) in zip(index_val, index_values):
                        if i != r and r > -1:
                            success = False
                            break
                    if success:
                        result.append(var_id)
        return result

    def add(self, variable_type: int, variable_index: Sequence[int],
            ub: Optional[float] = None, lb: Optional[float] = None, cc: Optional[float] = None,
            bin: Optional[int] = None) -> int:
        var_id = self.filter(var_type=variable_type, index_values=variable_index)
        self.lp_model.shop.model.lp_model.lp_model['add_var_type'].set(variable_type)
        self.lp_model.shop.model.lp_model.lp_model['add_var_index'].set(variable_index)
        if len(var_id) > 0:
            info = self[var_id].info()
            self.lp_model.shop.model.lp_model.lp_model['add_var_ub'].set(info['ub'] if ub is None else ub)
            self.lp_model.shop.model.lp_model.lp_model['add_var_lb'].set(info['lb'] if lb is None else lb)
            self.lp_model.shop.model.lp_model.lp_model['add_var_cc'].set(info['cc'] if cc is None else cc)
            self.lp_model.shop.model.lp_model.lp_model['add_var_bin'].set((1 if info['bin'] else 0) if bin is None else bin)
        else:
            self.lp_model.shop.model.lp_model.lp_model['add_var_ub'].set(1e20 if ub is None else ub)
            self.lp_model.shop.model.lp_model.lp_model['add_var_lb'].set(-1e20 if lb is None else lb)
            self.lp_model.shop.model.lp_model.lp_model['add_var_cc'].set(0.0 if cc is None else cc)
            self.lp_model.shop.model.lp_model.lp_model['add_var_bin'].set(0 if bin is None else bin)
        self.lp_model.shop.set_lp_var([], [])

        return self.lp_model.shop.model.lp_model.lp_model['add_var_last'].get()


class VarType(object):

    lp_model:'lp_model.LpModelBuilder'
    id:int

    def __init__(self, lp_model:'lp_model.LpModelBuilder', id:int) -> None:
        self.lp_model = lp_model
        self.id = id

    def __getattr__(self, attr:str) -> Any:
        if attr == 'id':
            return self.id
        elif attr == 'name':
            return self.lp_model._lp_model['var_type_names'][self.id]
        elif attr == 'index_types':
            return self.get_index_types()
        elif attr == 'index_type_names':
            index_type = self.get_index_types()
            return self.lp_model.index_type.get_names()[index_type]
            # return self.lp_model.get_index_types()[index_type]

    def __dir__(self) -> List[str]:
        return ['id', 'name', 'index_types', 'index_type_names']

    def get_index_types(self) -> Sequence[int]:
        index_type_beg = self.lp_model._lp_model['var_type_index_type_beg']
        index_type_cnt = self.lp_model._lp_model['var_type_index_type_cnt']
        index_type_val = self.lp_model._lp_model['var_type_index_type_val']
        return index_type_val[index_type_beg[self.id]:index_type_beg[self.id]+index_type_cnt[self.id]]


class VarTypeBuilder(object):

    lp_model:'lp_model.LpModelBuilder'
    var_type_names_no_space:Optional[Sequence[str]]

    def __init__(self, lp_model:'lp_model.LpModelBuilder') -> None:
        self.lp_model = lp_model
        self.var_type_names_no_space = None

    def __dir__(self) -> Sequence[str]:
        if self.var_type_names_no_space is None:
            self.var_type_names_no_space = np.char.replace(self.lp_model._lp_model["var_type_names"], ' ', '_')
        return np.append(self.var_type_names_no_space, super().__dir__())

    def __getattr__(self, attr:str) -> VarType:
        return VarType(self.lp_model, np.where(self.__dir__() == attr)[0][0])

    def __getitem__(self, item:Union[int,str]) -> VarType:
        if isinstance(item, str):
            ret = np.where(self.lp_model._lp_model['var_type_names'] == item)[0]
            if ret.size > 0:
                id = ret[0]
            else:
                id = None
        else:
            id = item
        return VarType(self.lp_model, id)

    def get_names(self) -> Sequence[str]:
        return self.lp_model._lp_model['var_type_names']
