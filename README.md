# PRTG Custom Sensor for Crypto Miners

This Python script creates a custom sensor for PRTG Network Monitor, allowing you to monitor **Iceriver** and **Antminer** miners. The sensor provides the following features:

1. **Client Socket Communication**:
   - The script establishes a client socket connection to fetch real-time data from the miner devices.

2. **Abstract CreateChannels Class**:
   - The script includes an abstract CreateChannels class to facilitate the integration of other miners.

3. **Logging for Debugging**:
   - If any issues arise during execution, the logs provide valuable insights for troubleshooting.

4. **Test Units**:
   - The script includes unit tests to verify its functionality.

5. **Execution of Windows Executable**:
   - This approach allows seamless integration with existing monitoring script.

![Iceriver](/images/iceriver1.png)

![Antminer](/images/antminer.png)

![Iceriver Error](/images/iceriver2.png)

## Sensor Summary
    Version: 1.2.0 
    Language: PRTG Python 3.9.13
    Author: Juari Marcolino (JM-1000)
    PRTG version: 24.2.96.1315+
    Dependency: paesslerag_prtg_sensor_api v1.0.2


## Iceriver channels

The following channels are implemented:
- Downtime
- Real-Time hashrate
- Average hashrate
- Rejected
- Uptime
- Chip number
- Temperature_In
- Temperature_Out
- Fan [num]
- Connected pool
- Pool - Difficulty
- Pool - Priority
- Pool - Accepted
- Pool - Rejected


## Antminer channels

The following channels are implemented:
- Real-time hashrate
- Average hashrate
- Rejected shares
- Accepted shares
- Hardware Errors
- Uptime
- Fan [num]
- Temperature_In Chip [num]
- Temperature_Out Chip [num]
- Chain [num] - Average hashrate
- Temperature_In Chip 3
- Pool [num] - Status
- Pool [num] - Mining jobs received
- Pool [num] - Accepted
- Pool [num] - Rejected
- Pool [num] - Difficulty


## Sensor parameters

The sensor expects key-value pairs in the format `--key value`. The parameter string MUST:
- Each pair be separated by a blankspace.
- Not contain quotes, braces and brackets. 
- Not contain characters outside the ASCII character set.
- Not contain the `--` combination within the `value`.

#### Parameter `ip` (required)
The IP address of the miner, it is set in the PRTG device settings.

### Parameters defined in the PRTG sensor settings
#### Parameter `--port`
The port for the monitoring interface (API) of the miner, 4111 is the default for Iceriver and 4028 is for the Antminer.

#### Parameter `--jsonFile`
The json file path where the requested data will be saved. If not specified, a file will be automatically created in the system's temporary directory. The log directory will be in the same directory as json file as `sensor_id_0000` where 0000 is the sensor ID.

#### Parameter `--waitTime`
The time interval (in milliseconds) the script should wait for a response. The default value is 100 ms.

#### Parameter `--exeFile`
An optional parameter that allows the user to request monitoring data using a Windows executable file. This file should accept the following parameters: --ip, --port, --file, --wait, --mode. The data must be saved as a json file.

#### Parameter `--forceExe`
If set to True, the script will only request monitoring data using the Windows executable file.

### Parameter Exemple:
`--waitTime 200 --port 4028 --jsonFile C:\Windows\temp\file.json --exeFile C:\Program Files (x86)\PRTG Network Monitor\Custom Sensors\python\iceriver.exe`


## Installation

1. [Download the sensor files](https://download-directory.github.io/?url=https%3A%2F%2Fgithub.com%2Fjm-1000%2FPython-PRTG-Custom-Sensor-for-Antminer-and-Iceriver-Miners%2Ftree%2Fmain%2Fcustom_sensor) and put them in `C:\Program Files (x86)\PRTG Network Monitor\Custom Sensors\python` as the tree:
```
 C:\P...\Custom Sensors\python\
                           custom_sensor_lib\
                           iceriver.py
                           antminer.py
```

2. (Optional) For testing you need use the *PRTG Python* installation because of the script dependency: `C:\Program Files (x86)\PRTG Network Monitor\python\python.exe -m unittest discover -s .\custom_sensor_lib\tests`

3. Create PRTG device for the miner (setting its IP address).

4. For the device created, add a new sensor:
    1. In the `Add Sensor` section (Step 1), search for `Python Script Advanced` sensor then click in the add buttom.

    2. (Optional) Define the sensor name (and others fields). 
    
    3. In the `Script` field, select the miner Python file (`antminer.py` or `iceriver.py`).

    4. (Optional) In the `Additionnal Parameters`, add the desired sensor parameter then click in the `Create` buttom.

5. Click in the created sensor and wait or click in the `Scan Now` buttom (in the right superior corner) to accelerate the update.
