import pandas as pd

from pyshop.shopcore.shop_api import get_attribute_value


class ShopApiMock:
    x_curve = [0, 1]
    y_curve = [0.0, 1.1]
    ref = 0.0
    array_reference = [0.0, 10.0]
    array_n_points = [2, 3]
    array_x_curve = [0, 1, 0, 1, 2]
    array_y_curve = [0.0, 1.1, 0.0, 1.1, 2.2]
    timeunit = 'hour'
    starttime = '202201010000'
    txy_t = [0, 1, 2]
    txy_y = [0.0, 1.1, 2.2]

    def __getattr__(self, command):
        def dummy_func(*args):
            if command == 'GetXyCurveX':
                return self.x_curve
            elif command == 'GetXyCurveY':
                return self.y_curve
            elif command == 'GetXyCurveReference':
                return self.ref
            elif command == 'GetXyCurveArrayReferences':
                return self.array_reference
            elif command == 'GetXyCurveArrayNPoints':
                return self.array_n_points
            elif command == 'GetXyCurveArrayX':
                return self.array_x_curve
            elif command == 'GetXyCurveArrayY':
                return self.array_y_curve
            elif command == 'GetTxySeriesStartTime':
                return self.starttime
            elif command == 'GetTxySeriesT':
                return self.txy_t
            elif command == 'GetTxySeriesY':
                return self.txy_y
            elif command == 'GetTimeUnit':
                return self.timeunit
            elif command == 'GetTimeZone':
                return ''
            else:
                return command, list(args)
        return dummy_func


class TestGetAttribute:
    shop_api = ShopApiMock()

    # def test_get_int(self):
    #     command, args = get_attribute_value(self.shop_api, 'obj_name', 'obj_type', 'attr_name', 'int')
    #     assert command == 'GetIntValue'
    #     assert args == ['obj_type', 'obj_name', 'attr_name']

    def test_get_xy(self):
        value = get_attribute_value(self.shop_api, 'obj_name', 'obj_type', 'attr_name', 'xy')
        assert (value.index == self.shop_api.x_curve).all()
        assert (value.values == self.shop_api.y_curve).all()
        assert value.name == self.shop_api.ref

    def test_get_xy_array(self):
        value = get_attribute_value(self.shop_api, 'obj_name', 'obj_type', 'attr_name', 'xy_array')
        for i, n in enumerate(self.shop_api.array_n_points):
            n_sum = sum(self.shop_api.array_n_points[0:i])
            assert (value[i].index == self.shop_api.array_x_curve[n_sum:n_sum+n]).all()
            assert (value[i].values == self.shop_api.array_y_curve[n_sum:n_sum+n]).all()
            assert value[i].name == self.shop_api.array_reference[i]

    def test_get_txy(self):
        value = get_attribute_value(self.shop_api, 'obj_name', 'obj_type', 'attr_name', 'txy')
        if self.shop_api.timeunit == 'hour':
            starttime = pd.Timestamp(self.shop_api.starttime)
            assert (value.index == [starttime + pd.Timedelta(hours=t) for t in self.shop_api.txy_t]).all()
            assert (value.values == self.shop_api.txy_y).all()
