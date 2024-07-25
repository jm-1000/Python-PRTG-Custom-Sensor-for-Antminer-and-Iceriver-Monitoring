# -*- coding: utf-8 -*-
# It was developed by JM-1000.

# __version__ = "1.2.0"

"""
This script is a custom PRTG Python sensor, designed to monitor an Iceriver 
miner. 
"""

from json import loads, dump
from paesslerag_prtg_sensor_api.sensor.units import ValueUnit
# Local library imports
from custom_sensor_lib.create_channel import CreateChannels


class IceriverChannels(CreateChannels):  
    SERVER_PORT = 4111
    MSG_FORMAT: str = '{"id": "%s"}\n'
    COMMANDS: list = \
        ['info', 'fan', 'board', 'boardpow', 'getnet', 'getpool']

    def _boardpower_channels(self, data: dict):
        self.result.add_primary_channel(
            name='Real-Time hashrate',
            value=int(self.get_value('rtpow', data)[:-1]),
            unit=self.get_value('unit', data) + 'H/s',
            is_limit_mode=True,
            limit_min_warning=130,
            limit_min_error=120
        )
        self.result.add_channel(
            name='Average hashrate',
            value=int(self.get_value('avgpow', data)[:-1]),
            unit=self.get_value('unit', data) + 'H/s',
            is_limit_mode=True,
            limit_min_warning=130,
            limit_min_error=120
        )
        self.result.add_channel(
            name='Rejected',
            value=self.get_value('reject', data),
            unit=" ",
            is_float=False,
            is_limit_mode=True,
            limit_max_warning=30,
            limit_max_error=15
        )
        _runtime = self.get_value('runtime', data).split(':')
        _days, _hours, _min, _sec = [int(part) for part in _runtime]
        _runtime_sec = _days * 86400 + _hours * 3600 + _min * 60 + _sec
        self.result.add_channel(name='Uptime',
            value=_runtime_sec,
            unit=ValueUnit.TIMESECONDS,
            speed_time='Hour'
        )


    def _board_channels(self, data: dict):
        self.result.add_channel(
            name='Chip number',
            value=self.get_value('chipnum', data),
            unit=' '
        )
        _value = self.get_value('intmp', data)  
        if not _value: _value = self.get_value('inttemp', data) 
        self.result.add_channel(
            name='Temperature_In',
            value=_value,
            unit=ValueUnit.TEMPERATURE,
            is_limit_mode=True,
            limit_max_warning=70,
            limit_max_error=80
        )
        _value = self.get_value('outtmp', data) 
        if not _value: _value = self.get_value('outtemp', data) 
        self.result.add_channel(
            name='Temperature_Out',
            value=_value,
            unit=ValueUnit.TEMPERATURE,
            is_limit_mode=True,
            limit_max_warning=70,
            limit_max_error=80
        )


    def _fan_channels(self, data: list):
        """
        Add channels for fans if the number of transactions per minute 
        is greater than 0.
        """
        for iter,fan in enumerate(data):
            if fan > 0:
                self.result.add_channel(
                    name='Fan ' + str(iter + 1),
                    value=fan,
                    unit='trs/m',
                    is_limit_mode=True,
                    limit_min_warning=500,
                    limit_min_error=250,
                    limit_max_warning=3000,
                    limit_max_error=3200
                )


    def _pool_channels(self, data: list):
        """Add channel for a connected pool."""
        _nbPool = 0
        for pool in data:
            if self.get_value('connect', pool): 
                _nbPool += 1
                if self.get_value('state', pool) == 1:
                    name = lambda string: 'Pool - {}'.format(string)

                    self.result.add_channel(
                        name=name('Difficulty'),
                        value=float(self.get_value('diff', 
                                                   pool).split(' ')[0]),
                        unit=self.get_value('diff', pool).split(' ')[1],
                        is_float=True
                    )
                    self.result.add_channel(
                        name=name('Priority'),
                        value=self.get_value('priority', pool),
                        unit=' '
                    )
                    self.result.add_channel(
                        name=name('Accepted'),
                        value=self.get_value('accepted', pool),
                        unit=' '
                    ) 
                    self.result.add_channel(
                        name=name('Rejected'),
                        value=self.get_value('rejected', pool),
                        unit=ValueUnit.PERCENT,
                        is_float=False,
                        is_limit_mode=True,
                        limit_max_warning=5,
                        limit_max_error=7
                    )
        # Add a channel for the number of pool connected, if the number 
        # is not equal to 1, an alert will be created in the PRTG sensor.
        self.result.add_channel(
            name='Connected pool',
            value=_nbPool,
            unit='pool',
            is_limit_mode=True,
            is_float=True,
            limit_max_warning=1.8,
            limit_warning_msg='Too many pools connected',
            limit_min_error=0.2,
            limit_error_msg='No pool connected'
        )


    def channels(self): 
        self._boardpower_channels(self.get_value('boardpower', self.data))
        self._board_channels(
            self.get_value('boards', self.get_value('boardinfo', 
                                                    self.data))[0])
        self._fan_channels(
            self.get_value('fans', self.get_value('fans', self.data)))
        self._pool_channels(
            self.get_value('pools', self.get_value('pool', self.data)))
    
    
    def get_value(self, key: str, dict: dict) -> any:
        """
        Retrieve the value associated with a key from a dictionary, 
        regardless of the case of the key for compactability 
        with a preexistent Windows executable data. 
        """

        for key2, value in dict.items():
            if key2.lower() == key.lower(): return value


    def to_dict(self, data: list) -> dict:
        """
        This function formats the fetched data 
        from [{'id': 'info', 'ret': {'code': 0, ... }, ... ] 
        to {'informations': {'id': 'info', 'code': 0, ... }, ... } for 
        compactability with a preexistent Windows executable data format.
        """

        _COMMANDS_DICT = {
            'info': "informations", 
            'fan': "fans", 
            'board': "boardinfo", 
            'boardpow': "boardpower", 
            'getnet': "network", 
            'getpool': "pool"
        }
        # Data from the preexistent Windows executable
        if isinstance(data[0], dict): return data[0] 
        # Data from the client socket 
        _adapted_data = {}
        for response in data:
            _response_dict = loads(response)
            cmd = _COMMANDS_DICT[_response_dict['id']]
            _adapted_data[cmd] = {'id':_response_dict['id']}
            _adapted_data[cmd].update(_response_dict['ret'])

        # Remove sensitive informations
        _adapted_data['informations']['softver1'] = "---"
        _adapted_data['informations']['softver2'] = "---"
        for pool in _adapted_data['pool']['pools']:
            for key in ['addr', 'user', 'pass']:
                pool[key] = "---"

        # Save the data in the json file
        with open(self.json_file, 'w') as json_file:
            dump(_adapted_data, json_file)
        return _adapted_data



if __name__ == "__main__":
    IceriverChannels().main()
