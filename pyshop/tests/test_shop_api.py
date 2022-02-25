from ..shopcore.shop_api import *

class ShopApiMock:
    x_curve = [0,1]
    y_curve = [0.0, 1.1]
    ref = 0.0

    def __getattr__(self, command):
        def dummy_func(*args):
            if command == 'GetXyCurveX':
                return self.x_curve
            elif command == 'GetXyCurveY':
                return self.y_curve
            elif command == 'GetXyCurveReference':
                return self.ref
            else:
                return command, list(args)
        return dummy_func

class TestGetAttribute:
    shop_api = ShopApiMock()

    def test_get_int(self):
        command, args = get_attribute_value(self.shop_api, 'obj_name', 'obj_type', 'attr_name', 'int')
        assert command == 'GetIntValue'
        assert args == ['obj_type', 'obj_name', 'attr_name']

    def test_get_xy(self):
            value = get_attribute_value(self.shop_api, 'obj_name', 'obj_type', 'attr_name', 'xy')
            assert (value.index == self.shop_api.x_curve).all()
            assert (value.values == self.shop_api.y_curve).all()
            assert value.name == self.shop_api.ref
