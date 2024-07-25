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

# __version__ = "1.2.0"

"""
This script is a custom PRTG Python sensor, designed to monitor an Antiminer 
miner.
"""

from json import loads, dump
from paesslerag_prtg_sensor_api.sensor.units import ValueUnit
# Local library imports
from custom_sensor_lib.create_channel import CreateChannels


class AntminerChannels(CreateChannels):
    SERVER_PORT = 4028
    COMMANDS = ['summary', 'pools', 'stats']
    MSG_FORMAT = '{"command": "%s", "parameter": "0"}'

    def _pools_channels(self, data: dict):
        for pool in data:
            _name = lambda string: 'Pool {} - {}'.format(pool['POOL'], string)
            is_connected = lambda : pool['Status'] == "Alive"
            self.result.add_channel(
                name=_name('Status'),
                value=1 if is_connected else 0,
                unit="(Connected)" if is_connected else "(Disconnected)",
                is_limit_mode=True,
                limit_min_warning=0,
                limit_warning_msg="Pool not connected"
            )
            self.result.add_channel(
                name=_name('Mining jobs received'),
                value=pool['Getworks'],
                unit=" "
            )
            self.result.add_channel(
                name=_name('Accepted'),
                value=pool['Accepted'],
                unit=" "
            )
            self.result.add_channel(
                name=_name('Rejected'),
                value=pool['Rejected'],
                unit=" "
            )
            self.result.add_channel(
                name=_name('Difficulty'),
                value=float(pool['Diff']),
                unit=" "
            )


    def _stats_channels(self, data: dict):
        self.result.add_channel(name='Uptime',
            value=data['Elapsed'],
            unit=ValueUnit.TIMESECONDS,
            speed_time='Hour'
        )
        for num in range(1, data['fan_num'] + 1):
            self.result.add_channel(
                name='Fan %s' %num,
                value=data['fan%s' %num],
                unit='trs/m',
                is_limit_mode=True,
                limit_min_warning=2000,
                limit_min_error=1000,
                limit_max_warning=5800,
                limit_max_error=6000
            )
        for num in [1, 2, 3]:
            self.result.add_channel(
                name='Temperature_In Chip %s' %num,
                value=int(data["temp_in_chip_%s" %num]),
                unit=ValueUnit.TEMPERATURE,
                is_limit_mode=True,
                limit_max_warning=75,
                limit_max_error=80
            )
            self.result.add_channel(
                name='Temperature_Out Chip %s' %num,
                value=int(data["temp_out_chip_%s" %num]),
                unit=ValueUnit.TEMPERATURE,
                is_limit_mode=True,
                limit_max_warning=75,
                limit_max_error=80
            )
            _rate = data["CHAIN AVG HASHRATE%s" %num]
            self.result.add_channel(
                name='Chain %s - Average hashrate' %num,
                value=float(_rate[:-5]),
                unit=_rate.split(_rate[:-5])[1],
                is_float=True
            )


    def _summary_channels(self, data: dict):
        rate = data["RT HASHRATE"]
        max_rate = float(data["THEORY HASHRATE"][:-5])
        self.result.add_primary_channel(
            name="Real-time hashrate",
            value=float(rate[:-5]),
            unit=rate.split(rate[:-5])[1],
            is_float=True,
            is_limit_mode=True,
            limit_min_warning=0.9 * max_rate,
            limit_min_error=0.8 * max_rate
        )
        self.result.add_channel(
            name="Average hashrate",
            value=float(data["AV HASHRATE"][:-5]),
            unit=rate.split(rate[:-5])[1],
            is_float=True,
            is_limit_mode=True,
            limit_min_warning=0.9 * max_rate,
            limit_min_error=0.8 * max_rate
        )
        self.result.add_channel(name='Rejected shares',
            value=data['Rejected'],
            unit=" ",
            is_limit_mode=True,
            limit_max_warning=50,
            limit_max_error=100
        )
        self.result.add_channel(name='Accepted shares',
            value=data['Accepted'],
            unit=" "
        )
        self.result.add_channel(name='Hardware Errors',
            value=data['Hardware Errors'],
            unit=" "
        )


    def channels(self):
        self._summary_channels(self.data['summary'][0])
        self._stats_channels(self.data['stats'][1])
        self._pools_channels(self.data['pools'])


    def to_dict(self, data: list) -> dict:
        _response_dict = {}
        for msg in data:
            _response = loads(msg[:-1])
            for cmd in self.COMMANDS:
                if cmd.upper() in _response.keys(): 
                    _response_dict[cmd] = _response[cmd.upper()]
                    break
        # Remove sensitive informations
        for pool in _response_dict['pools']:
            pool['URL'] = "---"
            pool['User'] = "---"

        # Save the data in the json file
        with open(self.json_file, 'w') as json_file:
            dump(_response_dict, json_file)
        return _response_dict



if __name__ == "__main__":
    AntminerChannels().main()