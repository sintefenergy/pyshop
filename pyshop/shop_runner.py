import json
import os
import sys
from typing import Dict, List, Optional, Callable
import pandas as pd
import numpy as np
import requests

from .helpers.commands import get_commands_from_file
from .helpers.time import get_shop_timestring
from .helpers.typing_annotations import CommandOptions, CommandValues, DataFrameOrSeries, Message, ShopApi
from .shopcore.model_builder import ModelBuilderType
from .shopcore.command_builder import CommandBuilder, get_derived_command_key
from .shopcore.shop_api import get_time_resolution
from .shopcore.shop_rest import ShopRestNative
from .lp_model.lp_model import LpModelBuilder


class ShopSession(object):
    # Class for handling a SHOP session through the python API.
    _log_file:str 
    _name:str
    _id:int
    _sim_has_started:bool
    _host:str
    _port:int
    _auth_headers:Dict[str,str]
    shop_api:ShopApi
    model:ModelBuilderType
    lp_model:LpModelBuilder
    _commands:Dict[str,str]
    _all_messages:List[Dict[str,str]]
    _command:str

    def __init__(self, license_path:str = '', silent:bool = True, log_file:str = '', solver_path:str = '', suppress_log:bool = False,
                 log_gets:bool = True, name:str = 'unnamed', id:int = 1, host:str = '', port:int = 8000) -> None:
        #Used by the SHOP rest APi 
        self._log_file = log_file
        self._name = name
        self._id = id
        self._sim_has_started = False

        # Create rest client if host ip is given
        if host:
            self._host = host
            self._port = port
            self._auth_headers = {
                'Content-Type': 'application/json'
            }
            response = requests.post(
                f'http://{host}:{port}/session',
                json=dict(session_name=name, log_file=log_file),
                headers=self._auth_headers
            )
            if response.ok:
                response_json = response.json()
                self._id = response_json['session_id']
                self._name = response_json['session_name']
            else:
                raise Exception(f"Could not connect to server: Status code {response.status_code}")
            self.shop_api = ShopRestNative(self)
        else:
            # Initialize a new SHOP session
            #
            # @param license_path The path where the license file, solver and solver interface are located
            if license_path:
                os.environ['ICC_COMMAND_PATH'] = license_path

            if 'ICC_COMMAND_PATH' not in os.environ:
                print("""The environment variable 'ICC_COMMAND_PATH' is not set.
                    Please use the keyword argument 'license_path' to specify the location of the SHOP license file.""")

            # Insert either the solver_path or the ICC_COMMAND_PATH to sys.path to find shop_pybind.pyd and solver dlls
            if solver_path:
                solver_path = os.path.abspath(solver_path)
                sys.path.insert(1, solver_path)
            else:
                sys.path.insert(1, os.environ['ICC_COMMAND_PATH'])

            import shop_pybind as pb

            silent_console = silent
            silent_log = suppress_log
            if log_file:
                self.shop_api = pb.ShopCore(silent_console, silent_log, log_file, log_gets)
            else:
                self.shop_api = pb.ShopCore(silent_console, silent_log)

            # Override where SHOP will look for solver dlls
            if solver_path:
                self.shop_api.OverrideDllPath(solver_path)

        self.model = ModelBuilderType(self.shop_api)
        self.lp_model = LpModelBuilder(self)
        self._commands = {x.replace(' ', '_'): x for x in self.shop_api.GetCommandTypesInSystem()}
        self._all_messages = []
        self._command = ""        

    def __dir__(self) -> List[str]:
        return list(self._commands.keys()) + [x for x in super().__dir__() if x[0] != '_' 
                                              and x not in self._commands.keys()]

    def __getattr__(self, command:str) -> Callable[[CommandOptions,CommandValues],bool]:
        self._command = command.lower()
        return self._execute_command

    def _execute_command(self, options:CommandOptions, values:CommandValues) -> bool:
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
        return self.shop_api.ExecuteCommand(self._commands[self._command], list(options), list(values))

    def set_time_resolution(self, starttime:pd.Timestamp, endtime:pd.Timestamp, timeunit:str, timeresolution:Optional[DataFrameOrSeries]=None) -> None:
        # Reformat timestamps to format expected by Shop
        start_string = get_shop_timestring(starttime)
        end_string = get_shop_timestring(endtime)
        # Handle time resolution
        # Constant
        if not isinstance(timeresolution, pd.DataFrame) and not isinstance(timeresolution, pd.Series):
            self.shop_api.SetTimeResolution(start_string, end_string, timeunit)
        # Timestamp indexed
        elif isinstance(timeresolution.index, pd.DatetimeIndex):
            # Handle time horizon outside time resolution definition
            if timeresolution.loc[starttime:starttime].empty:
                timeresolution.loc[starttime] = np.nan
                timeresolution.sort_index(inplace=True)
                timeresolution.ffill(inplace=True)
            timeresolution = timeresolution[starttime:endtime]
            # Transform timestamp index to integer index expected by Shop
            timeunit_delta = pd.Timedelta(hours=1) if timeunit == 'hour' else pd.Timedelta(minutes=1)
            timeres_t = [int((t - starttime) / timeunit_delta) for t in timeresolution.index]
            self.shop_api.SetTimeResolution(start_string, end_string, timeunit, timeres_t, timeresolution.values)
        # Integer indexed
        else:
            timeres_t = timeresolution.index.values
            self.shop_api.SetTimeResolution(start_string, end_string, timeunit, timeres_t, timeresolution.values)

        # Save the time zone in the API so that it can be added to the output TXYs
        tz_name = starttime.tzname()
        if tz_name is not None:
            self.shop_api.SetTimeZone(tz_name)

    def get_time_resolution(self) -> Dict:
        # Get time resolution
        return get_time_resolution(self.shop_api)

    def get_messages(self, all_messages:bool=False) -> Message:
        # Get all new messages from the buffer as a dict.
        messages = self.shop_api.GetMessages()
        messages = json.loads(messages)

        self._all_messages.extend(messages)

        if all_messages:
            return self._all_messages
        else:
            return messages

    def execute_full_command(self, full_command:str) -> None:
        parts = full_command.lower().strip().split()
        # First try to get a match using the two first words
        first_non_command = 2
        try:
            command = get_derived_command_key(parts[0] + '_' + parts[1], self._commands)
        except ValueError as err:
            try:
                command = get_derived_command_key(parts[0], self._commands)
                first_non_command = 1
            except ValueError as err2:
                error_message = "Could not find any a single command match. Got the following errors:\n" + str(err) + \
                                '\n' + str(err2)
                raise ValueError(error_message)

        parts = parts[first_non_command:]
        options = []
        values = []
        for word in parts:
            if word[0] == '/':
                options.append(word[1:])
            else:
                values.append(word)
        self._command = command
        self._execute_command(options, values)

    def get_executed_commands(self) -> List[str]:
        commands = self.shop_api.GetExecutedCommands()
        return commands

    def read_ascii_file(self, file_path:str) -> None:
        self.shop_api.ReadShopAsciiFile(file_path)

    def load_yaml(self, file_path:str='', yaml_string:str='') -> None:
        if file_path != '' and yaml_string != '':
            raise ValueError('Provide either a file path or a yaml string, not both')
        if file_path != '':
            with open(file_path, 'r', encoding='utf8') as f:
                yaml_file_string = f.read()
            self.shop_api.ReadYamlString(yaml_file_string)
        elif yaml_string != '':
            self.shop_api.ReadYamlString(yaml_string)

    def dump_yaml(self, file_path:str='', input_only:bool=True, compress_txy:bool=True, compress_connection:bool=True) -> str:
        if file_path != '':
            self.shop_api.DumpYamlCase(file_path, input_only, compress_txy, compress_connection)
            return f'YAML case is dumped to the provided file path: "{file_path}"'
        else:
            return self.shop_api.DumpYamlString(input_only, compress_txy, compress_connection)

    def run_command_file(self, folder:str, command_file:str, break_before_opt:bool = False) -> None:
        
        with open(os.path.join(folder, command_file), 'r', encoding='iso-8859-1') as run_file:
            file_string = run_file.read()
            run_commands = get_commands_from_file(file_string)
        
        for command in run_commands:
            command_text = command['command']
            options = command['options']
            values = command['values']

            #Simply break on the quit command instead of destroying the session
            if command_text == "q":
                break
            
            #Stop before optimization begins if requested
            if break_before_opt and command_text == "start sim":
                break
            
            #Reading input files should be done with proper API calls instead
            if command_text in ["read model", "add model"]:
                self.read_ascii_file(os.path.join(folder, values[0]))
            elif command_text == "read yaml":
                self.load_yaml(folder,values[0])
            else:            
                #Directly execute all other commands
                self.shop_api.ExecuteCommand(command_text, options, values)

    def run_command_file_progress(self, folder:str, command_file:str) -> None:
        with open(os.path.join(folder, command_file), 'r', encoding='iso-8859-1') as run_file:
            file_string = run_file.read()
            run_commands = get_commands_from_file(file_string)
        command_list = []
        options_list = []
        values_list = []
        for command in run_commands:
            command_list.append(command['command'])
            options_list.append(command['options'])
            values_list.append(command['values'])
        self.shop_api.ExecuteCommandList(command_list, options_list, values_list)

    def execute_command(self) -> CommandBuilder:
        # Terminal function for executing SHOP commands that gives code completion for SHOP commands.
        return CommandBuilder(self.shop_api)

    def get_shop_version(self) -> str:
        version_string = self.shop_api.GetVersionString()
        return version_string.split()[0]
