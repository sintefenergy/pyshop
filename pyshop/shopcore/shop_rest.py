import requests

class ShopRestNative(object):
    def __init__(self, shop_session):
        self._session = shop_session
        self.commands = requests.get(
                f'http://{shop_session._host}:{shop_session._port}/internal',
                headers={**shop_session._auth_headers, "session-id": str(shop_session._id)}
            ).json()
        # {shop_api._session_id}

    def __dir__(self):
        return self.commands

    def __getattr__(self, name):
        return self._generate_command_func(self._session, name)

    def _generate_command_func(self, shop_session, name):
        def command_func(*args, **kwargs):
            return requests.post(f'http://{shop_session._host}:{shop_session._port}/internal/{name}',
                                headers={**shop_session._auth_headers, "session-id": str(shop_session._id)},
                                # params=dict(session=shop_session._id),
                                json=dict(args=args, kwargs=kwargs)).json()
        return command_func