import pytest
from pyshop_rest_server.app import app
import threading

from pyshop import ShopRestSession

@pytest.fixture(scope='module')
def client():
    keywords = {'host': '127.0.0.1', 'port': 5000, 'debug': False}
    server = threading.Thread(target=app.run, kwargs=keywords, daemon=True)
    server.start()

def test_loading_model_with_and_yaml(client):
    shop = ShopRestSession(usr='per', pwd='aaslid')
    shop.load_yaml('./models/basic_model.yaml')
    assert 'Reservoir1' in shop.model.reservoir.get_object_names()
    assert 'Plant1' in shop.model.plant.get_object_names()