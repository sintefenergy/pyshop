import pandas as pd

from pyshop.shopcore.shop_api import get_attribute_value, set_attribute


class ShopApiMock:
    mock_dict = {
        'GetIntValue': 11,
        'GetIntArray': [11, 22],
        'GetDoubleValue': 1.1,
        'GetDoubleArray': [1.1, 2.2],
        'GetXyCurveX': [0, 1],
        'GetXyCurveY': [0.0, 1.1],
        'GetXyCurveReference': 0.0,
        'GetXyCurveArrayReferences': [0.0, 10.0],
        'GetXyCurveArrayNPoints': [2, 3],
        'GetXyCurveArrayX': [0, 1, 0, 1, 2],
        'GetXyCurveArrayY': [0.0, 1.1, 0.0, 1.1, 2.2],
        'GetTimeUnit': 'hour',
        'GetTxySeriesStartTime': '202201010000',
        'GetTxySeriesT': [0, 1, 2],
        'GetTxySeriesY': [0.0, 1.1, 2.2],
        'GetTimeZone': '',
        'GetStartTime': '202201010000',
        'GetEndTime': '202201010200',
        'GetTimeResolutionT': [0],
        'GetTimeResolutionY': [1]
    }

    def __getattr__(self, command: str):
        def dummy_func(*args):
            if command.startswith('Get'):
                return self.mock_dict[command]
            elif command.startswith('Set'):
                self.mock_dict[command] = args
        return dummy_func

    def __getitem__(self, command):
        return self.mock_dict[command]


class TestGetAttribute:
    shop_api = ShopApiMock()

    def test_get_int(self):
        assert get_attribute_value(self.shop_api, 'obj_name', 'obj_type', 'attr_name', 'int') == self.shop_api['GetIntValue']

    def test_get_int_array(self):
        assert get_attribute_value(self.shop_api, 'obj_name', 'obj_type', 'attr_name', 'int_array') == self.shop_api['GetIntArray']

    def test_get_double(self):
        assert get_attribute_value(self.shop_api, 'obj_name', 'obj_type', 'attr_name', 'double') == self.shop_api['GetDoubleValue']

    def test_get_double_array(self):
        assert get_attribute_value(self.shop_api, 'obj_name', 'obj_type', 'attr_name', 'double_array') == self.shop_api['GetDoubleArray']

    def test_get_xy(self):
        value = get_attribute_value(self.shop_api, 'obj_name', 'obj_type', 'attr_name', 'xy')
        assert (value.index == self.shop_api['GetXyCurveX']).all()
        assert (value.values == self.shop_api['GetXyCurveY']).all()
        assert value.name == self.shop_api['GetXyCurveReference']

    def test_get_xy_array(self):
        value = get_attribute_value(self.shop_api, 'obj_name', 'obj_type', 'attr_name', 'xy_array')
        for i, n in enumerate(self.shop_api['GetXyCurveArrayNPoints']):
            n_sum = sum(self.shop_api['GetXyCurveArrayNPoints'][0:i])
            assert (value[i].index == self.shop_api['GetXyCurveArrayX'][n_sum:n_sum + n]).all()
            assert (value[i].values == self.shop_api['GetXyCurveArrayY'][n_sum:n_sum + n]).all()
            assert value[i].name == self.shop_api['GetXyCurveArrayReferences'][i]

    def test_get_txy(self):
        value = get_attribute_value(self.shop_api, 'obj_name', 'obj_type', 'attr_name', 'txy')
        if self.shop_api['GetTimeUnit'] == 'hour':
            starttime = pd.Timestamp(self.shop_api['GetTxySeriesStartTime'])
            assert (value.index == [starttime + pd.Timedelta(hours=t) for t in self.shop_api['GetTxySeriesT']]).all()
            assert (value.values == self.shop_api['GetTxySeriesY']).all()


class TestSetAttribute:
    shop_api = ShopApiMock()

    def test_set_xy(self):
        xy_val = pd.Series(
            self.shop_api['GetXyCurveY'], index=self.shop_api['GetXyCurveX'], name=self.shop_api['GetXyCurveReference']
        )
        set_attribute(self.shop_api, 'obj_name', 'obj_type', 'attr_name', 'xy', xy_val)
        res = self.shop_api['SetXyCurve']
        assert res[3] == self.shop_api['GetXyCurveReference']
        assert (res[4] == self.shop_api['GetXyCurveX']).all()
        assert (res[5] == self.shop_api['GetXyCurveY']).all()

    def test_set_xy_array(self):
        xy_array_val = []
        for i, n in enumerate(self.shop_api['GetXyCurveArrayNPoints']):
            n_sum = sum(self.shop_api['GetXyCurveArrayNPoints'][0:i])
            xy_array_val.append(
                pd.Series(
                    self.shop_api['GetXyCurveArrayY'][n_sum:n_sum + n],
                    index = self.shop_api['GetXyCurveArrayX'][n_sum:n_sum + n],
                    name = self.shop_api['GetXyCurveArrayReferences'][i]
                )
            )
        set_attribute(self.shop_api, 'obj_name', 'obj_type', 'attr_name', 'xy_array', xy_array_val)
        res = self.shop_api['SetXyCurveArray']
        assert (res[3] == self.shop_api['GetXyCurveArrayReferences']).all()
        assert (res[4] == self.shop_api['GetXyCurveArrayNPoints']).all()
        assert (res[5] == self.shop_api['GetXyCurveArrayX']).all()
        assert (res[6] == self.shop_api['GetXyCurveArrayY']).all()

    def test_set_txy(self):
        starttime = pd.Timestamp(self.shop_api['GetStartTime'])
        txy_val = pd.Series(
            self.shop_api['GetTxySeriesY'],
            index=[starttime + pd.Timedelta(hours=t) for t in self.shop_api['GetTxySeriesT']]
        )
        set_attribute(self.shop_api, 'obj_name', 'obj_type', 'attr_name', 'txy', txy_val)
        res = self.shop_api['SetTxySeries']
        assert res[3].startswith(self.shop_api['GetStartTime'])
        assert (res[4] == self.shop_api['GetTxySeriesT']).all()
        assert (res[5] == self.shop_api['GetTxySeriesY']).all()

    def test_set_constant_txy(self):
        set_attribute(self.shop_api, 'obj_name', 'obj_type', 'attr_name', 'txy', 1.1)
        starttime = pd.Timestamp(self.shop_api['GetStartTime'])
        res = self.shop_api['SetTxySeries']
        assert res[3].startswith(self.shop_api['GetStartTime'])
        assert (res[4] == self.shop_api['GetTxySeriesT'][0:1]).all()
        assert (res[5] == [1.1]).all()
