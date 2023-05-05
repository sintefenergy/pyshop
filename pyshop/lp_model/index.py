from typing import List, Optional, Sequence, Union, Dict
import numpy as np
from . import lp_model


class IndexType(object):

    lp_model:'lp_model.LpModelBuilder'
    id:int

    def __init__(self, lp_model:'lp_model.LpModelBuilder', id:int) -> None:
        self.lp_model = lp_model
        self.id = id

    def __getattr__(self, attr:str) -> Union[int, str, Sequence[str], Dict[int, str]]:
        if attr == 'id':
            return self.id
        elif attr == 'name':
            return self.lp_model._lp_model['index_type_names'][self.id]
        elif attr == 'description':
            id_start = self.lp_model._lp_model['index_type_desc_beg'][self.id]
            id_count = self.lp_model._lp_model['index_type_desc_cnt'][self.id]
            desc_vals = self.lp_model._lp_model['index_type_desc_val'][id_start:id_start+id_count]
            desc_indices = self.lp_model._lp_model['index_type_desc_index'][id_start:id_start+id_count]
            return {i: v for (i,v) in zip(desc_indices, desc_vals)}

    def __dir__(self) -> List[str]:
        return ['id', 'name', 'description']


class IndexTypeBuilder(object):

    lp_model:'lp_model.LpModelBuilder'
    index_type_names_no_space:Optional[Sequence[str]]

    def __init__(self, lp_model:'lp_model.LpModelBuilder') -> None:
        self.lp_model = lp_model
        self.index_type_names_no_space = None

    def __dir__(self) -> Sequence[str]:
        if self.index_type_names_no_space is None:
            self.index_type_names_no_space = np.char.replace(self.get_names(), ' ', '_')
        return np.append(self.index_type_names_no_space, super().__dir__())

    def __getattr__(self, attr:str) -> IndexType:
        return IndexType(self.lp_model, np.where(self.__dir__() == attr)[0][0])

    def __getitem__(self, item:Union[int,str]) -> IndexType:
        if isinstance(item, str):
            ret = np.where(self.get_names() == item)[0]
            if ret.size > 0:
                id = ret[0]
            else:
                id = None
        else:
            id = item
        return IndexType(self.lp_model, id)

    def get_names(self) -> Sequence[str]:
        return self.lp_model._lp_model['index_type_names']
