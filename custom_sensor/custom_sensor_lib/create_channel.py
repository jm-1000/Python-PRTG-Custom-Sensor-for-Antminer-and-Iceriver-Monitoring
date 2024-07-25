# -*- coding: utf-8 -*-
# It was developed by JM-1000.

from sys import argv
from traceback import format_exc
from paesslerag_prtg_sensor_api.sensor.result import CustomSensorResult
# Local library imports
from custom_sensor_lib.sensor_util import (
        assign_sensor_files,
        get_data, 
        get_logger,
        parse_sensor_params, 
        script_params
    )


class CreateChannels():
    """
    This class fetches monitoring data from the miner and integrates it into 
    a PRTG sensor. Also, it generates a log file that records its execution 
    and errors.
    
    For specific miner, you must define: 
    * The MSG_FORMAT variable: a string containing the miner-specific request 
    message format. 

    * The COMMANDS variable: a list of miner-specific commands.

    * The SERVER_PORT: a integer for the service port of the miner.

    * Implement to_dict and channels methods. 
    """

    MSG_FORMAT: str 
    COMMANDS: list
    SERVER_PORT: int

    def __init__(self):
        """
        The following parameters are defined in the PRTG sensor parameters:
        --port      : The port for the miner monitoring interface (API).
        --waitTime  : The time interval (in milliseconds) the script should   
                        wait for a response. The default value is 100.
        --jsonFile  : The path of the json file where the requested data   
                        will be saved. If not specified, a file will be 
                        automatically created.
        --exeFile   : An optional parameter that allows the user to request
                        monitoring data using a Windows executable file. 
                        This file should accept the following parameters:   
                        --ip, --port, --file, --wait, --mode. The data should
                        be saved as a json file.
        --forceExe  : If set to True, the script will only request 
                        monitoring data using the Windows executable file.
        
        The script utilizes the IP address that is specifically designated 
        within the settings of the PRTG device.
        """

    
    def channels(self): 
        """
        This function calls the functions responsible for the creation of 
        channels for a specific miner.
        """

        raise NotImplementedError
    

    def handle_exception(self):
        if not script_params['logFile']: assign_sensor_files()
        _logger = get_logger()
        _logger.error('An error has occurred: %s \n\n' %format_exc(limit=2))
        # Show the log file location in PRTG sensor
        result = CustomSensorResult(text="Python Script execution error")
        result.error = \
            "ERROR: Go to \"%s\" for more details" %script_params['logFile']
        print(result.json_result)


    def load_args(self):
        script_params['port'] = self.SERVER_PORT
        parse_sensor_params(argv)
        self.json_file = script_params['jsonFile']


    def main(self):
        """Main function for the creation of the miner channels."""

        try:
            # Load the script parameters from the PRTG sensor arguments
            self.load_args()
            # Request the monitoring data 
            self.data = self.to_dict(get_data(self.COMMANDS, 
                                              self.MSG_FORMAT))     
            self.logger = get_logger()
            self.logger.info('Starting the creation of channels')

            # Create an instance of the PRTG custom sensor api to create   
            # a PRTG json format for the sensor 
            self.result = CustomSensorResult()
            # Create channels for a specific miner
            self.channels()
            # Integrate the channels into PRTG sensor 
            print(self.result.json_result)

            self.logger.info('Channels created')
            self.logger.info('The script was successfully executed \n\n\n\n')
        except:
            self.handle_exception()            


    def to_dict(self, data: list) -> dict: 
        """
        This function converts the fetched json string data into a dictionary. 
        """

        raise NotImplementedError

