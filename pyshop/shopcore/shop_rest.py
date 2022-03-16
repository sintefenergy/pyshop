from typing import Any, Callable, Dict
from .. import shop_runner 
import requests
import json
import numpy as np
import pandas as pd


class NumpyArrayEncoder(json.JSONEncoder):
    def default(self, obj:Any) -> Any:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Index):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


class ShopRestNative(object):
    
    _session:'shop_runner.ShopSession'
    commands:Dict

    def __init__(self, shop_session:'shop_runner.ShopSession') -> None:
        self._session = shop_session        
        self.commands = requests.get(
                f'http://{shop_session._host}:{shop_session._port}/internal',
                headers={**shop_session._auth_headers, "session-id": str(shop_session._id)}
            ).json()
        # {shop_api._session_id}

    def __dir__(self) -> Dict:
        return self.commands

    def __getattr__(self, name:str) -> Callable:
        return self._generate_command_func(self._session, name)

    def _generate_command_func(self, shop_session:'shop_runner.ShopSession', name:str) -> Callable:
        def command_func(*args, **kwargs):
            return requests.post(
                f'http://{shop_session._host}:{shop_session._port}/internal/{name}',
                headers={**shop_session._auth_headers, "session-id": str(shop_session._id)},
                # params=dict(session=shop_session._id),
                data=json.dumps(dict(args=args, kwargs=kwargs), cls=NumpyArrayEncoder)
            ).json()
        return command_func
