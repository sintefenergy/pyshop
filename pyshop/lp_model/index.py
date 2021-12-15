import numpy as np

class IndexType(object):
    def __init__(self, lp_model, id):
        self.lp_model = lp_model
        self.id = id

    def __getattr__(self, attr):
        if attr == 'id':
            return self.id
        elif attr == 'name':
            return self.lp_model._lp_model['index_type_names'][self.id]
        elif attr == 'description':
            id_start = self.lp_model._lp_model['index_type_desc_beg'][self.id]
            id_count = self.lp_model._lp_model['index_type_desc_cnt'][self.id]
            return self.lp_model._lp_model['index_type_desc_val'][id_start:id_start+id_count]
    
    def __dir__(self):
        return ['id', 'name', 'description']

class IndexTypeBuilder(object):
    def __init__(self, lp_model):
        self.lp_model = lp_model
        self.index_type_names_no_space = None

    def __dir__(self):
        if self.index_type_names_no_space is None:
            self.index_type_names_no_space = np.char.replace(self.get_names(), ' ', '_')
        return np.append(self.index_type_names_no_space, super().__dir__())

    def __getattr__(self, attr):
        return IndexType(self.lp_model, np.where(self.__dir__() == attr)[0][0])

    def __getitem__(self, item):
        if isinstance(item, str):
            ret = np.where(self.get_names() == item)[0]
            if ret.size > 0:
                id = ret[0]
            else:
                id = None
        else:
            id = item
        return IndexType(self.lp_model, id)

    def get_names(self):
        return self.lp_model._lp_model['index_type_names']