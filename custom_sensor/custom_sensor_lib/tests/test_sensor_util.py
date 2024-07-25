# -*- coding: utf-8 -*-
# It was developed by JM-1000.

import sys
import logging
import unittest
from os import path
from json import dump
from datetime import datetime
from unittest.mock import patch
from tempfile import TemporaryDirectory, TemporaryFile
# Local library imports
# Add the sensor directory of 'custom_sensor_lib' to the system path
dir = path.dirname(path.dirname(path.dirname(__file__)))
sys.path.append(dir) 
from custom_sensor_lib import sensor_util


class TestSensorUtil(unittest.TestCase):
    sensor_util = 'custom_sensor_lib.sensor_util.'

    # This function is executed first and once
    @classmethod
    def setUpClass(cls): 
        cls.default_script_params = {}
        cls.default_script_params.update(sensor_util.script_params)
        # Sample of the data fetched from an iceriver miner 
        cls.miner_data = [  
                """{"id": "getpool", "ret": {"code": 0, "pools": [
                        {"no": 1, "connect": true, "diff": "2199.02 G", 
                        "priority": 1, "accepted": 2418, "rejected": 0,
                        "state": 1}]} 
                }"""
        ]
        # Sample of the data returned by the get_data function
        cls.miner_pool_data = {'id': 'getpool', 'code': 0, 'pools': [
            {'no': 1, 'connect': True, 'diff': '2199.02 G', 'priority': 1,
            'accepted': 2418, 'rejected': 0, 'state': 1}]
        }


    # This function is executed before each test function
    def setUp(self):
        sensor_util.script_params.update(self.default_script_params)
        # Create temporary file and directory for the test. 
        # They are removed after the test. 
        self.temp_file = TemporaryFile()
        self.temp_dir = TemporaryDirectory()


    # All the following fuctions that start with 'test_' are test fuction
    @patch(sensor_util + '_assign_script_params')
    def test_parse_sensor_params(self, mock_assign_params):
        # Context for the test
        host = '127.0.0.1'
        params = {
                "forceExe": "True",
                "waitTime": "200",
                "port": "11111",
                "jsonFile": r"C:\\Test Dir\\temp\\jsonFile.json", 
                "exeFile": r"C:\\nTestDir\\temp\\file_iceriver.exe"
        }
        # Format of the PRTG arguments
        prtg_args = [
            "test.py", 
            '{"sensorid": "0000", "host": "%s",' %host +
             '"params": ' +
                '"--waitTime %s ' %params["waitTime"] +
                '--port %s ' %params["port"] + 
                '--jsonFile %s ' %params["jsonFile"] +
                '--exeFile %s' %params["exeFile"] + 
            '"}'
        ]
        print(prtg_args)
        # Testing the expected result
        sensor_util.parse_sensor_params(prtg_args)
        mock_assign_params.assert_called_once()
        parsed_params = mock_assign_params.call_args[0][0]
        self.assertIsInstance(parsed_params, list)
        self.assertIsInstance(parsed_params[0], tuple)
        for key, value in parsed_params:
            self.assertTrue(key in params.keys())
            self.assertEqual(value, params[key].replace(r'\\', '\\'))
        self.assertEqual(sensor_util.script_params['ip'], host)
        self.assertEqual(sensor_util.script_params['sensorid'], '0000')


    # Mocking a functions to isolate the unit of the code tested
    @patch(sensor_util + 'get_logger') 
    @patch(sensor_util + 'assign_sensor_files') 
    def test_assign_script_params(self, 
                                  mock_assign_files, mock_get_logger):
        # Context for the test.
        # Data returned by _parse_sensor_params function
        parsed_params = [
            ('forceExe', 'True'), 
            ('waitTime', '200'), 
            ('port', '11111'),
            ('exeFile', self.temp_file.name)
        ]
        # Testing the expected result
        sensor_util._assign_script_params(parsed_params)
        script_params = sensor_util.script_params
        self.assertEqual(script_params['exeFile'], self.temp_file.name)
        self.assertEqual(script_params['forceExe'], True)
        self.assertEqual(script_params['waitTime'], 200)
        self.assertEqual(script_params['port'], 11111)
        mock_assign_files.assert_called_once()
        mock_get_logger.assert_called_once()


    # Test the _assign_sensor_files function when the json file 
    # was provided.
    def test_assign_sensor_files_json(self):
        # Context for the test
        json_file = path.join(self.temp_dir.name, 'file.json')
        sensor_util.script_params['sensorid'] = '0000'
        # Setting the expected result
        date = str(datetime.now().date()).replace('-', '_')
        dir = "sensor_id_0000"
        sensor_log = path.join(self.temp_dir.name, 
                               dir, dir + "_%s.log" %date)
        exe_log = path.join(self.temp_dir.name, dir, dir + "_exe.log")
        # Testing the expected result
        sensor_util.assign_sensor_files(json_file)
        self.assertEqual(sensor_util.script_params['logFile'], sensor_log)
        self.assertEqual(sensor_util.script_params['exeLogFile'], exe_log)
        self.assertEqual(sensor_util.script_params['jsonFile'], json_file)
        
    # Test the _assign_sensor_files function when the json file
    # was not provided.
    @patch(sensor_util + 'makedirs')
    def test_assign_sensor_files(self, mock_mkdirs): 
        # Context for the test
        sensor_util.script_params['sensorid'] = '0000'
        # Set up the expected result
        date = str(datetime.now().date()).replace('-', '_')
        sensor_file = "sensor_id_0000"
        dir_parent = path.join(path.dirname(self.temp_dir.name), sensor_file)
        sensor_log = path.join(dir_parent, sensor_file + "_%s.log" %date)
        exe_log = path.join(dir_parent, sensor_file + "_exe.log")
        json_file = path.join(dir_parent, sensor_file + '.json')
        # Testing the expected result
        sensor_util.assign_sensor_files()
        self.assertEqual(sensor_util.script_params['logFile'], sensor_log)
        self.assertEqual(sensor_util.script_params['exeLogFile'], exe_log)
        self.assertEqual(sensor_util.script_params['jsonFile'], json_file)
        mock_mkdirs.assert_called_once()


    def test_get_logger(self):
        # Context for the test
        logFile = path.join(self.temp_dir.name, 'log.log')
        sensor_util.script_params['logFile'] = logFile
        # Test the expected result
        logger = sensor_util.get_logger()
        self.assertIsNotNone(logger)
        logger.info('Test logging')
        with open(logFile) as log_output:
            self.assertIn('[INFO] Test logging', log_output.read())
        logging.shutdown()

    
    @patch(sensor_util + 'Popen')
    @patch(sensor_util + 'sleep')
    def test_run_exe_file(self, mock_sleep, mock_popen):
        # Context for the test
        file = lambda fname: path.join(self.temp_dir.name, fname)
        params = {
                    'exeFile': file('file.exe'),
                    'exeLogFile': file('exe.log'),
                    'jsonFile': 'file.json',
                    'ip': '127.0.0.1',
                    'port': '11111',
                    'waitTime': '200'
        }
        sensor_util.script_params.update(params)
        # Should raise an exception for a non-existent executable file
        with self.assertRaisesRegex(Exception, 
                                    'Invalid Windows executable file.'):
            sensor_util._run_exe_file() 

        # Create the executable file
        open(sensor_util.script_params['exeFile'], 'w').close()
        # Test the expected result
        sensor_util._run_exe_file()
        for value in params.values():
            if value == params['exeLogFile']:
                with open(value, 'w') as open_file:
                    self.assertEqual(str(open_file),
                                     str(mock_popen.call_args[1]['stdout']))
            else: self.assertIn(value, mock_popen.call_args[0][0])
        mock_sleep.assert_called_once()


    # The default order for testing the functions is alphabetical
    # so 'test_z_' are last to be tested as the previous functions are needed. 
    @patch(sensor_util + 'get_logger') 
    @patch(sensor_util + 'ClientSocket.__init__') 
    @patch(sensor_util + 'ClientSocket.fetch_data') 
    def test_z_get_data_socket(self, mock_fetch_data, mock_init, _):
        # Test receiving the data using python sockets.
        # Context for the test
        params = {
                    'ip': '127.0.0.1',
                    'port': '11111',
                    'waitTime': '200'
        }
        sensor_util.script_params.update(params)
        cmds = ['info', 'fan', 'board', 'boardpow', 'getnet', 'getpool']
        msg_format = '{"id": "%s"}\n'
        # Setting the expected returned data of the mock functions
        mock_init.return_value = None
        mock_fetch_data.return_value = self.miner_data
        # Test the expected result
        returned_data = sensor_util.get_data(cmds, msg_format)
        self.assertListEqual(self.miner_data, returned_data)
        for arg in [*params.values(), cmds, msg_format]: 
            self.assertIn(arg, mock_init.call_args[0])


    @patch(sensor_util + 'get_logger') 
    @patch(sensor_util + '_run_exe_file') 
    def test_z_get_data_exe(self, mock_run_exe, _):
        # Test receiving the data using an executable file.
        # Context for the test
        jsonFile = path.join(self.temp_dir.name, 'file.json')
        params = {
                    'ip': '127.0.0.1',
                    'port': '11111',
                    'waitTime': '200',
                    'jsonFile': jsonFile,
                    'exeFile': self.temp_file.name
        }
        sensor_util.script_params.update(params)
        with open(jsonFile, 'w') as file:
            dump({'pool': self.miner_pool_data}, file)
        # Test the expected result
        returned_data = sensor_util.get_data()
        self.assertDictEqual(self.miner_pool_data, returned_data[0]['pool'])
        mock_run_exe.assert_called_once()
        

    # This function is executed after each test function
    def tearDown(self): 
        self.temp_file.close()
        self.temp_dir.cleanup()


if __name__ == '__main__':
    unittest.main()
    