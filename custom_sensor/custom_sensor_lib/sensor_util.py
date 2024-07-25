# -*- coding: utf-8 -*-
# MIT License

# Copyright (c) 2024 Juari Marcolino

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging
from time import sleep
from subprocess import Popen
from json import load, loads
from datetime import datetime
from os import path, makedirs
from re import findall, split
from tempfile import TemporaryFile
# Local library imports
from custom_sensor_lib.client_socket import ClientSocket


script_params = {
    'ip': '',
    'port': None,
    'mode': 'GET',
    'waitTime': 100,
    'exeFile': None,
    'jsonFile': None,
    'logFile': None,
    'exeLogFile': None,
    'forceExe': False,
    'sensorid': '0000'
}


def _assign_script_params(params: list):
    """
    This function assigns the parameters values to the 'script_params' 
    dictionary.

    Parameter:
    params (list)       : Sensor parameters as key-value pairs.
    """

    # The log file is not set yet, so log messages are saved
    # Save the log message and its log severity level, 20 for information
    _saved_log = [('Setting sensor parameters', 20)]
    try:
        for key, value in params: 
            if key in script_params.keys():
                if key == 'port':
                    if value.isdigit(): script_params[key] = int(value)

                elif key == 'exeFile':
                    if path.exists(value):
                        script_params[key] = path.abspath(value)
                        _saved_log.append(('Executable file set as %s'
                                           %script_params[key], 20))
                        
                elif key == 'forceExe':
                    if value.lower() == 'true': 
                        script_params[key] = True 
                        _saved_log.append(('Request data via executable '
                                          'file only', 20))
                        
                elif key == 'waitTime':
                    if value.isdigit(): script_params[key] = int(value)

                elif key == 'jsonFile':
                    try: assign_sensor_files(value)
                    except Exception as e: 
                        _saved_log.append(('Error setting json file: %s' %e, 
                                          40)) # 40 for error severity level
                        _saved_log.append(('Using the OS temporary directory', 
                                          30)) # 30 for warning severity level
    except:
        # If an error, do the logging of the saved log messages
        if not script_params['jsonFile']: assign_sensor_files()
        _logger = get_logger()
        for msg, level in _saved_log: _logger.log(msg=msg, level=level)
        raise Exception()
    
    # if an error or json file not defined, using the OS temporary directory 
    if not script_params['jsonFile']: assign_sensor_files()
    # Save log messages
    _saved_log.insert(
        1, ('Remote host ip address set to %s' %script_params['ip'], 20))
    _saved_log.insert(
        2, ('Remote host port number set to %s'%script_params['port'], 20))
    _saved_log.insert(
        3, ('Wait time set to %s ms' %script_params['waitTime'], 20))
    _saved_log.append(('Json file set as %s' %script_params['jsonFile'], 20))
    _saved_log.append(('Log file set as %s \n' %script_params['logFile'], 20))
    # Do the logging of the saved log messages
    _logger = get_logger()
    for msg, level in _saved_log: _logger.log(msg=msg, level=level)


def _run_exe_file():
    """
    This function runs a Windows executable file to fetch the data 
    saving it in json file.
    """

    try:
        _exe_file = script_params['exeFile']
        if path.exists(_exe_file) and _exe_file.endswith('.exe'):
            with open(script_params['exeLogFile'], 'w') as log_file:
                # Run the executable file
                process = Popen([
                                _exe_file, 
                                '--ip', script_params['ip'],
                                '--port', str(script_params['port']),
                                '--mode', script_params['mode'],
                                '--file', script_params['jsonFile'],
                                '--wait', str(script_params['waitTime'])], 
                                # Save the output
                                stdout=log_file, 
                                stderr=log_file
                    )
                # Wait 25 seconds as the time necessary for the program
                # logs a message in case of an error 
                sleep(25) 
                # Kill the program if it is still running
                if not process.poll(): process.kill()
        else: raise Exception('Invalid Windows executable file.')
    except Exception as e:
        raise Exception(e)


def assign_sensor_files(json_file: str=None):
    """
    This function sets files used by the sensor script.
    
    It takes the directory name and assign sensor directory, log file,
    json file and Windows executable log file to the 'script_params' 
    dictionary. 

    Parameter:
    json_file (str)     : This is the path to the JSON file. 
    The file itself may not exist, but its parent directory must have 
    write permissions. If None, system’s temporary directory is used.
    """

    # Formating the name of the sensor directory
    _sensor_dir_name = 'sensor_id_' + script_params['sensorid']
    # Formating the name of the files
    _date = str(datetime.now().date()).replace('-', '_')
    _sensor_log_name = "{}_{}.log".format(_sensor_dir_name, _date) 
    _exe_log_name = "%s_exe.log" %_sensor_dir_name
    
    dir = None
    if json_file: dir = path.dirname(json_file)
    # Create a temporary file to verify the write permission in the directory
    # If json_file is unset, using the temporary directory of the system as
    # parent directory 
    with TemporaryFile(dir=dir) as file:
        _new_dir = path.join(path.dirname(file.name), _sensor_dir_name)
        makedirs(_new_dir, exist_ok=True)

        script_params['logFile'] = path.join(_new_dir, _sensor_log_name)
        script_params['exeLogFile'] = path.join(_new_dir, _exe_log_name)
        if json_file: script_params['jsonFile'] = json_file
        else: 
            json_file = path.join(_new_dir, '%s.json' %_sensor_dir_name)
            script_params['jsonFile'] = json_file


def get_logger() -> logging:
    """
    This function does the logging system configuration and 
    return its instance.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
        logging.FileHandler(script_params['logFile'])
        ]
    )
    return logging.getLogger(__name__)


def get_data(miner_cmds: list=None, miner_msg_format: str=None) -> list:
    """
    This function is used to fetch the monitoring data from a client socket 
    or a Windows executable file.

    Parameters:
    miner_cmds (list)       : Miner specific commands.
    miner_msg_format (str)  : Miner specific request message format. 
    """

    _logger = get_logger()
    _logger.info('Starting data request')
    if not script_params['forceExe']:
        _logger.info('Starting client socket')
        try:
            # Fetch the data
            client_sock = ClientSocket(script_params['ip'], 
                                       script_params['port'],
                                       miner_cmds,
                                       miner_msg_format,
                                       script_params['waitTime'])
            data = client_sock.fetch_data()
            _logger.info('Successful reception of the data \n')
            return data 
        except Exception as e: 
            _logger.error('An error has occurred:' + str(e))
            if script_params['exeFile']:
                _logger.info('Trying executable file execution instead')
            else: raise Exception()

    if script_params['exeFile']:
        _logger.info('Executing the executable file')
        _run_exe_file()
        _logger.info('Successful execution of the executable file')

        _logger.info('Reading json file \n')
        with open(script_params['jsonFile']) as json_file:
            return [load(json_file)]


def parse_sensor_params(prtg_args: list):
    """
    This function reads the PRTG sensor parameters.
    It accepts parameters in '--key value' format.

    Parameter:
    prtg_args (list)        : PRTG sensor arguments.
    """
    
    try: 
        # Load PRTG sensor arguments
        _prtg_args = loads(prtg_args[1])
        # Assign sensor ID and host IP address
        script_params['sensorid'] = _prtg_args['sensorid']
        script_params['ip'] = _prtg_args['host']

        # Convert string parameters into a list
        _params_list = _prtg_args['params'].split('--')
        if _params_list[0] == '': _params_list.pop(0)
        _params_cleaned = []
        for param in _params_list:
            _key = findall('^\S+', param)[0]
            _value = split(r'^' + _key , param)[1].strip()
            # The \ symbol used in Windows file system is special in python
            # Its string version is \\  
            symbol = [  
                        '\n', '\\n',
                        '\t', '\\t', 
                        '\r', '\\r', 
                        '\b', '\\b', 
                        '\f', '\\f'
            ]
            # For each special combination in the Windows file path  
            # replace it with its string version
            if _key in ['exeFile', 'jsonFile']:
                for i in range(0, len(symbol), 2):
                    if symbol[i] in _value and symbol[i+1] not in _value:
                        _value = _value.replace(symbol[i], symbol[i+1])
            _params_cleaned.append((_key, _value))
        _assign_script_params(_params_cleaned)
    except: raise Exception()

