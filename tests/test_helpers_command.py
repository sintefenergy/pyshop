from pyshop.helpers.commands import get_commands_from_file

def test_get_commands_from_file():
    command_array = get_commands_from_file(
        'add model MyModel.ascii\n' +
        'set nseg /down 25\n' +
        '#set power_head_optimization /on\n' +
        'set password "shop_func=abc"'
    )
    assert command_array[0] == {
        'command': 'add model',
        'options': [],
        'values': ['MyModel.ascii']
    }
    assert command_array[1] == {
        'command': 'set nseg',
        'options': ['down'],
        'values': ['25']
    }
    assert command_array[2] == {
        'command': 'set password',
        'options': [],
        'values': ['"SHOP_FUNC=abc"']
    }
    assert len(command_array) == 3