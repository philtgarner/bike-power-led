import pygatt
import yaml
import logging
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Default FTP
ftp = 200

# Default power average window (seconds)
power_average_duration = 3

# Dataframe for storing the power data in
# This will be manipulated to only store data for the duration specified by power_average_duration
power_readings = pd.DataFrame(columns=['power'])

# The UUID associated with the BLE characteristic org.bluetooth.characteristic.cycling_power_measurement
characteristic = '00002A63-0000-1000-8000-00805F9B34FB'

# Set the BLE address type
address_type = pygatt.BLEAddressType.random


def handle_data(handle, value):
    global power_readings

    # Get the current time.
    # This will be used to store the current power and also get our moving average
    now = datetime.now()

    # The only part of the data we care about is the "Instantaneous Power" reading.
    # The first 16 bits are a series of flags.
    # The second 16 bits are a signed integer representing the current power.
    # If we turn the complete dataset to 16 bit integers then a lot of it will be meaningless but
    # the second number will be the current power
    bluetooth_data = np.frombuffer(value, np.int16)

    # Store the current power against the current time
    current_power = bluetooth_data[1]
    power_readings.loc[now] = current_power

    # Remove any old data
    power_readings = power_readings.loc[power_readings.index >= now - timedelta(seconds=power_average_duration)]

    # Get the average power and the colour associated with it
    average_power = power_readings['power'].mean()
    led_colour = get_colour(average_power)

    # TODO Light the LED in the desired colour

    print('Average power: %d' % average_power)
    print('Power colour: %s' % led_colour)


# TODO Change this from a sample method to something that returns actual colours
def get_colour(power):
    percentage = power / ftp

    if percentage <= 59:
        # grey
        return 'grey'
    elif percentage <= 75:
        # blue
        return 'blue'
    elif percentage <= 89:
        # green
        return 'green'
    elif percentage <= 104:
        # yellow
        return 'yellow'
    elif percentage <= 118:
        # orange
        return 'orange'
    else:
        # red
        return 'red'


if __name__ == '__main__':

    logging.basicConfig()
    logging.getLogger('pygatt').setLevel(logging.DEBUG)

    # Get the items from the config file
    config = yaml.safe_load(open('config.yml'))
    device_id = config['bluetooth-device']
    ftp = config['ftp']
    power_average_duration = config['power-average-duration']

    # Use the Gatt Tool connection
    adapter = pygatt.GATTToolBackend()
    try:
        # Start the adapter
        adapter.start()

        # Connect to the power meter
        device = adapter.connect(device_id, address_type=address_type)

        # Subscribe to the Cycling Power Measurement characteristic
        device.subscribe(characteristic, callback=handle_data)

        # Sleep for twenty seconds so we can receive some data
        # TODO We probably need to put something like a while(True) in here
        # TODO But we'll need to know how to handle stopping the adapter
        time.sleep(20)
    finally:
        adapter.stop()
