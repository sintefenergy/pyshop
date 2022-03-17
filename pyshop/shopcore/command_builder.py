from typing import Dict, List
from ..helpers.typing_annotations import CommandOptions, CommandValues, ShopApi


class OptionBuilder(object): # pragma: no cover

    _shop_api:ShopApi
    _commands:Dict[str,str]
    _command:str

    def __init__(self, shop_api:ShopApi, commands:Dict[str,str], command:str) -> None:
        self._shop_api = shop_api
        self._commands = commands
        self._command = command

    def set(self, options:CommandOptions, values:CommandValues) -> bool:
        self._command = get_derived_command_key(self._command, self._commands)
        if self._command not in self._commands:
            raise ValueError(f'Unknown command: "{self._command.replace("_", " ")}"')
        if not isinstance(options, list):
            options = [options]
        if not isinstance(values, list):
            values = [values]
        options = map(str, options)
        options = filter(lambda x: x, options)
        values = map(str, values)
        values = filter(lambda x: x, values)
        return self._shop_api.ExecuteCommand(self._commands[self._command], list(options), list(values))


class CommandBuilder(object): # pragma: no cover

    _shop_api:ShopApi
    _commands:Dict[str,str]

    def __init__(self, shop_api:ShopApi) -> None:
        self._shop_api = shop_api
        self._commands = {x.replace(' ', '_'): x for x in shop_api.GetCommandTypesInSystem()}

    def __getattr__(self, command:str) -> OptionBuilder:
        return OptionBuilder(self._shop_api, self._commands, command.lower())

    def __dir__(self) -> List[str]:
        return list(self._commands.keys())


def get_derived_command_key(original_command:str, command_dict:Dict[str,str]) -> str:
    derived_command = original_command
    command_keys = list(command_dict.keys())
    num_matches = 0
    for command_key in command_keys:
        if command_key.startswith(original_command):
            derived_command = command_key
            if command_key == original_command:
                return original_command
            num_matches += 1
        
    if num_matches > 1:
        raise ValueError(f'Abbreviation matches multiple commands: "{original_command.replace("_", " ")}"')
    if num_matches == 0:
        raise ValueError(f'Unknown command: "{original_command.replace("_", " ")}"')
    return derived_command