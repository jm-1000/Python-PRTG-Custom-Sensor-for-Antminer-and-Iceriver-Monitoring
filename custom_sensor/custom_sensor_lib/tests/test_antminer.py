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
from antminer import AntminerChannels


class TestAntminer(unittest.TestCase):
    # This function is executed before each test function
    def setUp(self):
        # Sample of the native Antminer miner data 
        self.fetched_data = [
            '{"STATUS":[{"Msg":"Summary", "Description":"jansson2"}],' 
            '"SUMMARY":[{'
                '"RT HASHRATE":"21632.89GH/s", "AV HASHRATE":"20442GH/s",'
                '"THEORY HASHRATE":"20517GH/s", "Rejected":0,'
                '"Accepted": 1000, "Hardware Errors": 5}],'
            '"id":1}\x00',
            '{"STATUS":[{"Msg":"3Pool(s)", "Description":"jansson2"}],' 
            '"POOLS":[{'
                '"POOL":0, "URL":"test.com", "Status":"Alive",' 
                '"User":"user", "Accepted":150,'
                '"Getworks": 500, "Diff":10000, "Rejected":0}],'
            '"id":1}\x00',
            '{"STATUS":[{"Msg":"CGMinerstats", "Description":"jansson2"}],' 
            '"STATS":[{'
                '"Type":"AntminerKS5"}, {"STATS":3 , "fan_num":2,' 
                '"fan1":4430, "fan2":4440, "Elapsed": 366810,'
                '"temp_in_chip_1":"69", "temp_in_chip_2":"70",'
                '"temp_in_chip_3":"67", "temp_out_chip_1":"64",'
                '"temp_out_chip_2":"64","temp_out_chip_3":"64",'
                '"CHAIN AVG HASHRATE1":"6809.27GH/s",'
                '"CHAIN AVG HASHRATE2":"100GH/s",'
                '"CHAIN AVG HASHRATE3":"50GH/s"}],'
            '"id":1}\x00'
        ] 
        # Antminer miner data for channel creation 
        self.antminer_data = {
            "summary":[{
                "RT HASHRATE":"21632.89GH/s", "AV HASHRATE":"20442GH/s",
                "THEORY HASHRATE":"20517GH/s", "Rejected":0,
                "Accepted": 1000, "Hardware Errors": 5}],
            "pools":[{
                "POOL":0, "URL":"---", "Status":"Alive", "Getworks": 500,
                "User":"---", "Accepted":150, "Diff":10000, "Rejected":0}],
            "stats":[{
                "Type":"AntminerKS5"}, {"STATS":3 , "fan_num":2,
                "fan1":4430, "fan2":4440,"Elapsed": 366810,
                "temp_in_chip_1":"69", "temp_in_chip_2":"70",
                "temp_in_chip_3":"67", "temp_out_chip_1":"64",
                "temp_out_chip_2":"64","temp_out_chip_3":"64",
                "CHAIN AVG HASHRATE1":"6809.27GH/s",
                "CHAIN AVG HASHRATE2":"100GH/s",
                "CHAIN AVG HASHRATE3":"50GH/s"}]
        }
        self.antminer = AntminerChannels()
        self.antminer.result = CustomSensorResult()
        

    # Tests the data adapter function that processes fetched data 
    # from the miner and checks if the data is correctly formatted.
    def test_to_dict(self): 
        with TemporaryDirectory() as dir:
            json = path.join(dir, 'file.json')
            self.antminer.json_file = json
            # Testing the expected result
            data = self.antminer.to_dict(self.fetched_data)
            self.assertDictEqual(data, self.antminer_data)
            with open(json) as json:
                self.assertIn('"temp_in_chip_1": "69", "temp_in_chip_2": "70"', 
                              json.read())


    # Tests the function that creates channels related to summary
    def test_summary_channels(self):
        rt_channel = {
            "Channel": "Real-time hashrate", "Value": 21632.8, 
             "DecimalMode": "All", "Float": 1, "Unit": "Custom", 
             "CustomUnit": "9GH/s", "SpeedSize": "One", "VolumeSize": "One", 
             "SpeedTime": "Second", "Mode": "Absolute", "LimitMinError": 
             "1640.8000000000002", "LimitMode": 1, 
             "LimitMinWarning": "1845.9"
        }
        self.antminer._summary_channels(self.antminer_data['summary'][0])
        # Testing the expected result
        result = self.antminer.result
        self.assertIn(rt_channel, 
                      loads(str(result))['prtg']['result'])
        for channel in ['Real-time hashrate', 'Average hashrate', 
                        'Accepted shares', 'Rejected', 'Hardware Errors']:
            self.assertIn(channel, str(result))


    # Tests the function that creates channels related to stats
    def test_stats_channels(self):
        self.antminer._stats_channels(self.antminer_data['stats'][1])
        # Testing the expected result
        for channel in ['Uptime', "Temperature_In Chip 1", 
                        "Temperature_Out Chip 1", 'Fan 1', 
                        "Chain 1 - Average hashrate"]:
            self.assertIn(channel, str(self.antminer.result))

    
    # Tests the function that creates channels related to pools
    def test_pools_channels(self):
        self.antminer._pools_channels(self.antminer_data['pools'])
        # Testing the expected result
        for channel in ['Status', 'Accepted', 
                        'Mining jobs received', 'Difficulty']:
            self.assertIn("Pool 0 - " + channel, 
                          str(self.antminer.result))
    

    # Tests the main execution of the Antminer script, 
    # mocking functions to ensure the module isolation.
    @patch('custom_sensor_lib.create_channel.get_data')
    @patch('custom_sensor_lib.create_channel.get_logger')
    @patch('custom_sensor_lib.create_channel.CreateChannels.load_args')
    @patch('custom_sensor_lib.create_channel.print')
    def test_z_main(self, mock_print, mock_load_args,
                    mock_get_logger, mock_get_data): 
        with TemporaryDirectory() as dir:
            self.antminer.json_file = path.join(dir, 
                                                              'file.json')
            self.antminer.log_file = 'file.log'
            mock_get_data.return_value = self.fetched_data
            # Testing the expected result
            self.antminer.main()
            self.assertIn('"result"', mock_print.call_args[0][0])
            mock_get_data.assert_called_once()
            mock_get_logger.assert_called_once()
            mock_load_args.assert_called_once()


if __name__ == '__main__':
    unittest.main()
 