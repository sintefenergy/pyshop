from pyshop.helpers.commands import get_commands_from_file

def test_get_commands_from_file():
    command_array = get_commands_from_file(
        "add model MyModel.ascii\nset nseg /down 25\n#set power_head_optimization /on"
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
    assert len(command_array) == 2