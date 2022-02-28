import pandas as pd

from pyshop.shopcore.shop_api import get_attribute_value


class ShopApiMock:
    mock_dict = {
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
        'GetTimeZone': ''
    }

    def __getattr__(self, command):
        def dummy_func(*args):
            return self.mock_dict[command]
        return dummy_func
    
    def __getitem__(self, command):
        return self.mock_dict[command]


class TestGetAttribute:
    shop_api = ShopApiMock()

    def test_get_xy(self):
        value = get_attribute_value(self.shop_api, 'obj_name', 'obj_type', 'attr_name', 'xy')
        assert (value.index == self.shop_api['GetXyCurveX']).all()
        assert (value.values == self.shop_api['GetXyCurveY']).all()
        assert value.name == self.shop_api['GetXyCurveReference']

    def test_get_xy_array(self):
        value = get_attribute_value(self.shop_api, 'obj_name', 'obj_type', 'attr_name', 'xy_array')
        for i, n in enumerate(self.shop_api['GetXyCurveArrayNPoints']):
            n_sum = sum(self.shop_api['GetXyCurveArrayNPoints'][0:i])
            assert (value[i].index == self.shop_api['GetXyCurveArrayX'][n_sum:n_sum+n]).all()
            assert (value[i].values == self.shop_api['GetXyCurveArrayY'][n_sum:n_sum+n]).all()
            assert value[i].name == self.shop_api['GetXyCurveArrayReferences'][i]

    def test_get_txy(self):
        value = get_attribute_value(self.shop_api, 'obj_name', 'obj_type', 'attr_name', 'txy')
        if self.shop_api['GetTimeUnit'] == 'hour':
            starttime = pd.Timestamp(self.shop_api['GetTxySeriesStartTime'])
            assert (value.index == [starttime + pd.Timedelta(hours=t) for t in self.shop_api['GetTxySeriesT']]).all()
            assert (value.values == self.shop_api['GetTxySeriesY']).all()
