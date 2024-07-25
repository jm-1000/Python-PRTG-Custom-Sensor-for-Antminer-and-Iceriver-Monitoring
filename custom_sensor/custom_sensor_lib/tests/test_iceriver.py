# -*- coding: utf-8 -*-
# It was developed by JM-1000.

import sys
import unittest
from os import path
import unittest.mock
from json import loads
from unittest.mock import patch
from tempfile import TemporaryDirectory
from paesslerag_prtg_sensor_api.sensor.result import CustomSensorResult
# Local library imports
# Add the sensor root directory to the system path
sys.path.append(
    path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
from iceriver import IceriverChannels


class TestIceriver(unittest.TestCase):
    # This function is executed before each test function
    def setUp(self):
        # Sample of the native Iceriver miner data 
        self.fetched_data = [
            '{"id": "info", "ret": {'
                '"softver1": "v1.0", "softver2": "v1.0"}}',
            '{"id": "fan", "ret": {"code": 0, "fans": [300, 100]}}', 
            '{"id": "board", "ret": {"code": 0, "boards": [' 
                '{"no": 1, "chipnum": 18, "rtpow": "36.71G",' 
                '"intmp": 34, "outtmp": 52, "state": true}]}}', 
            '{"id": "boardpow", "ret": {"code": 0,'
                '"reject": 0, "rtpow": "155G", "avgpow": "152G",'
                '"runtime": "00:09:21:23",  "unit": "G"}}',  
            '{"id": "getpool", "ret": {"code": 0, "pools": ['
                '{"no": 1, "connect": true, "diff": "2199.02 G",'
                '"priority": 1, "accepted": 2418, "rejected": 0,' 
                '"addr": "test.com", "user": "testUser", "pass": "x",' 
                '"state": 1}]}}'
        ] 
        # Iceriver miner data for channel creation 
        self.iceriver_data = {
            "informations": {"id": "info", 
                "softver1": "---", "softver2": "---"},
            'fans': {"id": "fan", "code": 0, "fans": [300, 100]}, 
            'boardinfo': {"id": "board", "code": 0, "boards": [ 
                {"no": 1, "chipnum": 18, "rtpow": "36.71G", 
                "intmp": 34, "outtmp": 52, "state": True}]}, 
            'boardpower': {"id": "boardpow", "code": 0,
                "reject": 0, "rtpow": "155G", "avgpow": "152G",
                "runtime": "00:09:21:23",  "unit": "G"},  
            'pool': {"id": "getpool", "code": 0, "pools": [
                {"no": 1, "connect": True, "diff": "2199.02 G",
                "priority": 1, "accepted": 2418, "rejected": 0, 
                "addr": "---", "user": "---", "pass": "---", 
                "state": 1}]}
        }
        self.iceriver = IceriverChannels()
        self.iceriver.result = CustomSensorResult()
        

    # Tests the data adapter function that processes fetched data 
    # from the miner and checks if the data is correctly formatted.
    def test_to_dict(self):
        with TemporaryDirectory() as dir:
            json = path.join(dir, 'file.json')
            self.iceriver.json_file = json
            # Testing the expected result
            data = self.iceriver.to_dict(self.fetched_data)
            for cmd in ["pool", "informations"]:
                self.assertDictEqual(data[cmd], self.iceriver_data[cmd])
            with open(json) as json:
                self.assertIn('"connect": true, "diff": "2199.02 G"', 
                              json.read())


    # Tests the function that creates channels related to board power,
    # ensuring they are correctly generated.
    def test_boardpower_channels(self): 
        rt_channel = {
            "Channel": "Real-Time hashrate", "Value": 155, "Unit": "Custom",
            "CustomUnit": "GH/s", "SpeedSize": "One", "VolumeSize": "One",
            "SpeedTime": "Second", "Mode": "Absolute", 
            "LimitMinError": "120", "LimitMode": 1, "LimitMinWarning": "130"
        }
        self.iceriver._boardpower_channels(self.iceriver_data['boardpower'])
        # Testing the expected result
        result = self.iceriver.result
        self.assertIn(rt_channel, 
                      loads(str(result))['prtg']['result'])
        for channel in ['Real-Time hashrate', 
                        'Average hashrate', 'Rejected', 'Uptime']:
            self.assertIn(channel, str(result))


    # Tests the function that creates channels for board information.
    def test_board_channels(self): 
        self.iceriver._board_channels(
            self.iceriver_data['boardinfo']['boards'][0])
        for channel in ['Chip number', 'Temperature_In', 'Temperature_Out']:
            self.assertIn(channel, str(self.iceriver.result))


    # Tests the function that generates channels for fan information.
    def test_fan_channels(self): 
        self.iceriver._fan_channels(self.iceriver_data['fans']['fans'])
        for channel in ['Fan 1', 'Fan 2']:
            self.assertIn(channel, str(self.iceriver.result))


    #  Tests the function responsible for creating channels related
    #  to pool information.
    def test_pool_channels(self): 
        self.iceriver._pool_channels(self.iceriver_data['pool']['pools'])
        for channel in ['Difficulty', 'Priority', 
                        'Accepted', 'Rejected', 'Connected pool']:
            self.assertIn(channel, str(self.iceriver.result))
        

    # Tests the main execution of the Iceriver script, 
    # mocking functions to ensure the module isolation.
    @patch('custom_sensor_lib.create_channel.get_data')
    @patch('custom_sensor_lib.create_channel.get_logger')
    @patch('custom_sensor_lib.create_channel.CreateChannels.load_args')
    @patch('custom_sensor_lib.create_channel.print')
    def test_z_main(self, mock_print, mock_load_args,  
                    mock_get_logger, mock_get_data): 
        with TemporaryDirectory() as dir:
            self.iceriver.json_file = path.join(dir, 'file.json')
            self.iceriver.log_file = 'file.log'
            mock_get_data.return_value = self.fetched_data
            # Testing the expected result
            self.iceriver.main()
            self.assertIn('"result"', mock_print.call_args[0][0])
            mock_get_data.assert_called_once()
            mock_get_logger.assert_called_once()
            mock_load_args.assert_called_once()



if __name__ == '__main__':
    unittest.main()
 