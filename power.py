import os
import pygatt
import yaml
import logging
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import board
import neopixel
import RPi.GPIO as GPIO

# The pin that the NeoPixel ring is connected to
pixel_pin = board.D18

# The number of LEDs in the NeoPixel ring
num_pixels = 12

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB
GPIO.setmode(GPIO.BCM)

# Power zone colours
grey = (100, 100, 100)
blue = (0, 0, 100)
green = (0, 100, 0)
yellow = (100, 100, 0)
orange = (120, 65, 0)
red = (100, 0, 0)
off = (0, 0, 0)

# Keep track of the current colour
current_colour = off

# Set up the pixel ring
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER)

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
    """
    The callback for the bluetooth characteristic subscription.
    :param handle: integer, characteristic read handle the data was received on
    :param value: bytearray, the data returned in the notification
    """
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

    # Change the LED colour
    change_colour(led_colour)


def change_colour(new_colour):
    """
    Changes the colour displayed on the LED ring.
    Changes each LED in turn with a brief pause between each change.
    :param new_colour: The new colour to display
    """
    global current_colour
    global pixels
    interval = 0.05

    if new_colour != current_colour:
        for pixel in range(num_pixels):
            pixels[pixel] = new_colour
            pixels.show()
            time.sleep(interval)

        current_colour = new_colour


def get_colour(power):
    """
    Gets the colour associated with a given power.
    This is calculated by working out what percentage of the users FTP they are at.
    :param power: The current power
    :return: The colour associated with the specified power
    """
    percentage = power / ftp

    if percentage <= 0.59:
        return grey
    elif percentage <= 0.75:
        return blue
    elif percentage <= 0.89:
        return green
    elif percentage <= 1.04:
        return yellow
    elif percentage <= 1.18:
        return orange
    else:
        return red


def flash_colour(colour):
    """
    Displays one colour and then turns the LEDs off.
    Used to display information to the user
    :param colour: The colour to flash
    """
    change_colour(colour)
    time.sleep(1)
    change_colour(off)


if __name__ == '__main__':

    # Flash the LEDs blue to show startup
    flash_colour(blue)

    # Get the items from the config file
    config_file_location = os.path.join(os.path.dirname(__file__), 'config.yml')
    config = yaml.safe_load(open(config_file_location))
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

        # flash the LEDs green to show we have connected
        flash_colour(green)

        # Subscribe to the Cycling Power Measurement characteristic
        device.subscribe(characteristic, callback=handle_data)

        # Sleep while we receive events
        while True:
            time.sleep(1000)
    except:
        # If we have an exception (most likely failed to connect) flash the LEDs red to tell the user
        flash_colour(red)
    finally:
        adapter.stop()
