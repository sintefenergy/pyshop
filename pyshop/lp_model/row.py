import numpy as np

class Row(object):
    def __init__(self, lp_model, row_id: int):
        self.lp_model = lp_model
        self.id = row_id

    def __getattr__(self, attr):
        type_id = self.lp_model._lp_model['row_type'][self.id]
        if attr == 'id':
            return self.id
        elif attr == 'type_id':
            return type_id
        elif attr == 'type_name':
            return self.lp_model._lp_model['row_type_names'][type_id]
        elif attr == 'index_type_ids':
            return self.lp_model.row_type[type_id].get_index_types()
        elif attr == 'index_type_names':
            return self.lp_model.get_index_types()[self.lp_model.row_type[type_id].get_index_types()]
        elif attr == 'index_values':
            return self.get_index_values()
        elif attr == 'index_descriptions':
            index_types = self.lp_model.row_type[type_id].get_index_types()
            index_values = self.get_index_values()
            return [self.lp_model.index_type[t].descrition[v] for (t,v) in zip(index_types, index_values)]
        elif attr == 'vars':
            lp_model = self.lp_model._lp_model
            ij = lp_model['Irow'] == self.id
            var_ids = lp_model['Jcol'][ij]
            var_coeffs = lp_model['AA'][ij]
            return [(i,c) for (i,c) in zip(var_ids, var_coeffs)]
        elif attr in self.__dir__():
            return self.lp_model._lp_model[attr][self.id]
        else:
            return None

    def __dir__(self):
        return np.append(
            ['id', 'type_id', 'type_name', 'index_type_ids', 'index_type_names',
            'index_values', 'index_descriptions', 'vars', 'rhs', 'sense'],
            super(Row, self).__dir__()
        )
    
    def info(self):
        type_id = self.lp_model._lp_model['row_type'][self.id]
        index_type_ids = self.lp_model.row_type[type_id].get_index_types()
        index_values = self.get_index_values()
        ij = self.lp_model._lp_model['Irow'] == self.id
        var_ids = self.lp_model._lp_model['Jcol'][ij]
        var_coeffs = self.lp_model._lp_model['AA'][ij]
        rhs = self.lp_model._lp_model['rhs'][self.id]
        sense = self.lp_model._lp_model['sense'][self.id]
        return {
            'id': self.id,
            'type_id': type_id,
            'type_name': self.lp_model._lp_model['row_type_names'][type_id],
            'index_type_ids': index_type_ids,
            'index_type_names': self.lp_model.index_type.get_names()[index_type_ids],
            'index_values': index_values,
            'index_descriptions': [self.lp_model.index_type[t].description[v] for (t,v) in zip(index_type_ids, index_values)],
            'vars': [(i,c) for (i,c) in zip(var_ids, var_coeffs)],
            'rhs': rhs,
            'sense': sense
        }

    def format(self):
        ret_str = ''
        ret_str += 'C{}: '.format(self.id)
        for (var_index, var_coeff) in self.vars:
            var_type_abbrev = self.lp_model.var[var_index].type_abbrev
            var_index_values = self.lp_model.var[var_index].index_values
            if var_coeff >= 0:
                ret_str += ' + '
                ret_str += '{} {}{}'.format(var_coeff, var_type_abbrev, var_index_values)
            else:
                ret_str += ' - '
                ret_str += '{} {}{}'.format(-var_coeff, var_type_abbrev, var_index_values)
        if self.sense == -1:
            ret_str += ' <= '
        elif self.sense == 1:
            ret_str += ' >= '
        else:
            ret_str += ' = '
        ret_str += str(self.rhs)
        return ret_str

    def set_parameters(self, variables: list=[], coefficients: list=[], rhs: float=None, sense: int=None):
        info = self.info()
        self.lp_model.shop.model.lp_model.lp_model['add_row_type'].set(info['type_id'])
        self.lp_model.shop.model.lp_model.lp_model['add_row_index'].set(info['index_values'])
        self.lp_model.shop.model.lp_model.lp_model['add_row_variables'].set(variables)
        self.lp_model.shop.model.lp_model.lp_model['add_row_coeff'].set(coefficients)
        self.lp_model.shop.model.lp_model.lp_model['add_row_rhs'].set(info['rhs'] if rhs == None else rhs)
        self.lp_model.shop.model.lp_model.lp_model['add_row_sense'].set(info['sense'] if sense == None else sense)
        self.lp_model.shop.set_lp_row([],[])
        return self.lp_model.shop.model.lp_model.lp_model['add_row_last'].get()

    def get_index_values(self):
        lp_model = self.lp_model._lp_model
        return lp_model['row_index_val'][lp_model['row_index_beg'][self.id]:lp_model['row_index_beg'][self.id] + lp_model['row_index_cnt'][self.id]]

class RowBuilder(object):
    def __init__(self, lp_model):
        self.lp_model = lp_model

    def __getitem__(self, item):
        if isinstance(item, (int, np.integer)):
            return Row(self.lp_model, item)
        else:
            return None

    def __getattr__(self, item):
        if item == 'n_rows':
            return self.lp_model._lp_model["row_type"].size

    def __dir__(self):
        return np.append(
            super(RowBuilder, self).__dir__(), 'n_rows'
        )

    def filter(self, row_type=None, index_values=[]):
        result = []
        for (row_id, row_t) in enumerate(self.lp_model._lp_model['row_type']):
            if row_type is None or row_type == row_t:
                # Check if index matches
                if len(index_values) == 0:
                    result.append(row_id)
                else:
                    index_val = self.lp_model.row[row_id].get_index_values()
                    success = True
                    for (i,r) in zip(index_val, index_values):
                        if i != r and r > -1:
                            success = False
                            break
                    if success:
                        result.append(row_id)
        return result

    def format(self, row_id=[]):
        if len(row_id) == 0:
            row_id = range(self.n_rows)
        ret_str = ''
        for r in row_id:
            ret_str += Row(self.lp_model, r).format() + '\n'
        return ret_str

    def add(self, row_type: int, row_index: list, variables: list=[], coefficients: list=[], rhs: float=None, sense: int=None):
        row_id = self.filter(row_type=row_type, index_values=row_index)
        self.lp_model.shop.model.lp_model.lp_model['add_row_type'].set(row_type)
        self.lp_model.shop.model.lp_model.lp_model['add_row_index'].set(row_index)
        self.lp_model.shop.model.lp_model.lp_model['add_row_variables'].set(variables)
        self.lp_model.shop.model.lp_model.lp_model['add_row_coeff'].set(coefficients)
        if len(row_id) > 0:
            info = self[row_id].info()
            self.lp_model.shop.model.lp_model.lp_model['add_row_rhs'].set(info['rhs'] if rhs == None else rhs)
            self.lp_model.shop.model.lp_model.lp_model['add_row_sense'].set(info['sense'] if sense == None else sense)
        else:
            self.lp_model.shop.model.lp_model.lp_model['add_row_rhs'].set(0.0 if rhs == None else rhs)
            self.lp_model.shop.model.lp_model.lp_model['add_row_sense'].set(0 if sense == None else sense)
        
        return self.lp_model.shop.model.lp_model.lp_model['add_row_last'].get()

class RowType(object):
    def __init__(self, lp_model, id):
        self.lp_model = lp_model
        self.id = id

    def __getattr__(self, attr):
        if attr == 'id':
            return self.id
        elif attr == 'name':
            return self.lp_model._lp_model['row_type_names'][self.id]
        elif attr == 'index_types':
            return self.get_index_types()
        elif attr == 'index_type_names':
            index_type = self.get_index_types()
            return self.lp_model.index_type.get_names()[index_type]
            # return self.lp_model.get_index_types()[index_type]
    
    def __dir__(self):
        return ['id', 'name', 'index_types', 'index_type_names']

    def get_index_types(self):
        index_type_beg = self.lp_model._lp_model['row_type_index_type_beg']
        index_type_cnt = self.lp_model._lp_model['row_type_index_type_cnt']
        index_type_val = self.lp_model._lp_model['row_type_index_type_val']
        return index_type_val[index_type_beg[self.id]:index_type_beg[self.id]+index_type_cnt[self.id]]

class RowTypeBuilder(object):
    def __init__(self, lp_model):
        self.lp_model = lp_model
        self.row_type_names_no_space = None

    def __dir__(self):
        if self.row_type_names_no_space is None:
            self.row_type_names_no_space = np.char.replace(self.lp_model._lp_model['row_type_names'], ' ', '_')
        return np.append(self.row_type_names_no_space, super().__dir__())

    def __getattr__(self, attr):
        return RowType(self.lp_model, np.where(self.__dir__() == attr)[0][0])

    def __getitem__(self, item):
        if isinstance(item, str):
            ret = np.where(self.lp_model._lp_model['row_type_names'] == item)[0]
            if ret.size > 0:
                id = ret[0]
            else:
                id = None
        else:
            id = item
        return RowType(self.lp_model, id)

    def get_names(self):
        return self.lp_model._lp_model['row_type_names']

    def print(self, row_type=[]):
        if len(row_type) == 0:
            row_type = range(self.lp_model._lp_model['row_type_names'].size)
        for r in range(self.lp_model.row.n_rows):
            row = Row(self.lp_model, r)
            if row.type_id in row_type:
                row.print()